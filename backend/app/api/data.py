"""数据管理接口：导出 / 导入 / 一键清理

- 导出：将全部业务数据序列化为 JSON（不含密码哈希等敏感字段）
- 导入：清空现有业务数据，按导出的 JSON 重建
- 清理：清空业务数据，重置为默认口令 admin123，重建预置数据

说明：所有接口均为破坏性/文件操作，必须家长认证 + 前端二次确认。
"""
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Date, DateTime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.api.deps import require_parent
from app.seed.seed import seed_data
from app.models import (
    Achievement,
    BankRecord,
    CheckinStreak,
    Child,
    DailyCheckin,
    ExchangeRecord,
    GrowthLog,
    ParentConfig,
    PersonalGoal,
    Reward,
    ScoreRecord,
    ShopTask,
    SurpriseTicket,
    TaskRule,
)

router = APIRouter(prefix="/data", tags=["数据管理"], dependencies=[Depends(require_parent)])

# 业务数据表（按依赖顺序；parent_config 单独处理，level_config 等系统配置靠 seed 重建）
BUSINESS_MODELS = [
    Child,
    TaskRule,
    Reward,
    ScoreRecord,
    Achievement,
    ExchangeRecord,
    GrowthLog,
    DailyCheckin,
    CheckinStreak,
    PersonalGoal,
    BankRecord,
    SurpriseTicket,
    ShopTask,
]

# 导出时排除的敏感字段
SENSITIVE_COLUMNS = {"password_hash", "child_password_hash"}


def _row_to_dict(obj) -> dict:
    """SQLAlchemy 实例 -> dict（排除敏感字段，日期转 ISO 字符串）"""
    data = {}
    for col in obj.__table__.columns:
        name = col.name
        if name in SENSITIVE_COLUMNS:
            continue
        val = getattr(obj, name)
        if isinstance(val, (datetime, date)):
            data[name] = val.isoformat()
        else:
            data[name] = val
    return data


def _row_from_dict(model, data: dict):
    """dict -> SQLAlchemy 实例（日期字段转回 datetime/date）"""
    kwargs = {}
    for key, val in data.items():
        col = model.__table__.columns.get(key)
        if col is None:
            continue
        if isinstance(col.type, DateTime) and val:
            kwargs[key] = datetime.fromisoformat(val)
        elif isinstance(col.type, Date) and val:
            kwargs[key] = date.fromisoformat(val)
        else:
            kwargs[key] = val
    return model(**kwargs)


def _snapshot(db: Session) -> dict:
    """导出快照（保留主键与关联 id，便于恢复）"""
    snapshot = {}
    for model in BUSINESS_MODELS:
        rows = db.query(model).all()
        snapshot[model.__tablename__] = [_row_to_dict(r) for r in rows]
    cfg = db.query(ParentConfig).first()
    snapshot["parent_config"] = _row_to_dict(cfg) if cfg else None
    return snapshot


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    """导出全部业务数据为 JSON"""
    return JSONResponse(content=_snapshot(db), media_type="application/json")


class ImportBody(BaseModel):
    data: dict


@router.post("/import")
def import_data(body: ImportBody, db: Session = Depends(get_db)):
    """导入数据：清空业务表后按 JSON 重建，再补 seed 系统数据"""
    data = body.data
    if not isinstance(data, dict):
        raise HTTPException(400, "数据格式错误")

    _clear_business(db)

    for model in BUSINESS_MODELS:
        rows = data.get(model.__tablename__)
        if not rows:
            continue
        for row in rows:
            db.add(_row_from_dict(model, row))
    db.commit()

    # 补齐系统预置数据（等级、成就、任务规则等缺失项）
    seed_data(db)
    return {"ok": True, "message": "数据导入成功"}


class ClearBody(BaseModel):
    confirm: bool = False


@router.post("/clear")
def clear_data(body: ClearBody, db: Session = Depends(get_db)):
    """一键清理：清空所有业务数据，重置口令为 admin123，重建预置数据"""
    if not body.confirm:
        raise HTTPException(400, "请确认后再执行清理")

    _clear_business(db)

    cfg = db.query(ParentConfig).first()
    if cfg:
        cfg.password_hash = hash_password("admin123")
        cfg.child_password_hash = hash_password("admin123")
        db.commit()

    seed_data(db)
    return {"ok": True, "message": "已清理并恢复默认设置"}


def _clear_business(db: Session):
    """清空所有业务表（parent_config、level_config 结构保留）"""
    for model in reversed(BUSINESS_MODELS):
        db.query(model).delete()
    db.commit()