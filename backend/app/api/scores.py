"""积分接口：加/减分、流水、等级、统计"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ScoreRecord, TaskRule
from app.schemas.schemas import ScoreRecordCreate, ScoreRecordOut
from app.services.achievement_service import check_achievements
from app.services.score_service import (
    add_score,
    check_score_limit,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_dashboard,
    get_level_before_after,
    get_level_progress,
)
from app.api.achievements import ach_brief_full


def _ach_brief(a):
    """成就简要信息（含段位/稀有度光效）"""
    return ach_brief_full(a)

router = APIRouter(prefix="/scores", tags=["积分"])


@router.post("", response_model=dict)
def create_score(body: ScoreRecordCreate, db: Session = Depends(get_db)):
    """加分/减分（家长操作）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    score_delta = body.score_delta
    task_rule_id = body.task_rule_id
    reason = body.reason
    record_type = "reward"

    if task_rule_id:
        rule = db.get(TaskRule, task_rule_id)
        if not rule:
            raise HTTPException(404, "任务不存在")
        score_delta = rule.score_value
        reason = reason or rule.name
        record_type = "reward" if rule.score_value >= 0 else "penalty"

    if score_delta is None:
        raise HTTPException(400, "必须提供分值")

    # 积分上限校验
    limit_err = check_score_limit(db, child.id, score_delta)
    if limit_err:
        raise HTTPException(400, limit_err)

    # 记录加分前的累计积分（用于等级升级检测）
    lifetime_before = get_child_lifetime_score(db, child.id)

    record = add_score(
        db,
        child.id,
        record_type=record_type,
        score_delta=score_delta,
        reason=reason,
        operator=body.operator,
        task_rule_id=task_rule_id,
    )

    # 等级升级检测
    lifetime_after = get_child_lifetime_score(db, child.id)
    level_change = get_level_before_after(db, child.id, lifetime_before, lifetime_after)

    # 成就检测
    new_ach = check_achievements(db, child.id, event_type="score")
    db.commit()

    return {
        "record": {
            "id": record.id,
            "score_delta": record.score_delta,
            "reason": record.reason,
            "created_at": record.created_at,
        },
        "balance": get_child_balance(db, child.id),
        "level": get_level_progress(db, child.id),
        "level_change": level_change,
        "new_achievements": [_ach_brief(a) for a in new_ach],
    }


@router.get("/balance")
def read_balance(db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return {
        "balance": get_child_balance(db, child.id),
        "level": get_level_progress(db, child.id),
    }


@router.get("/history", response_model=list[ScoreRecordOut])
def read_history(
    limit: int = Query(500, le=5000),
    db: Session = Depends(get_db),
):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return (
        db.query(ScoreRecord)
        .filter(ScoreRecord.child_id == child.id)
        .order_by(ScoreRecord.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/dashboard")
def read_dashboard(
    days: int = Query(14, le=30),
    db: Session = Depends(get_db),
):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return get_dashboard(db, child.id, days=days)
