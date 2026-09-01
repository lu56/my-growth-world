"""成长日志接口"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import GrowthLog, ScoreRecord
from app.schemas.schemas import GrowthLogCreate, GrowthLogOut
from app.services.score_service import get_child

router = APIRouter(prefix="/logs", tags=["成长日志"])


@router.get("")
def list_logs(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    logs = (
        db.query(GrowthLog)
        .filter(GrowthLog.child_id == child.id)
        .order_by(GrowthLog.created_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for log in logs:
        item = {
            "id": log.id,
            "child_id": log.child_id,
            "title": log.title,
            "content": log.content,
            "photos": log.photos,
            "score_record_id": log.score_record_id,
            "created_at": log.created_at,
        }
        # 关联积分记录
        if log.score_record_id:
            sr = db.get(ScoreRecord, log.score_record_id)
            if sr:
                item["score_delta"] = sr.score_delta
                item["score_reason"] = sr.reason
        result.append(item)
    return result


@router.post("", response_model=GrowthLogOut)
def create_log(body: GrowthLogCreate, db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    log = GrowthLog(
        child_id=child.id,
        title=body.title,
        content=body.content,
        photos=body.photos,
        score_record_id=body.score_record_id,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.get(GrowthLog, log_id)
    if not log:
        raise HTTPException(404, "日志不存在")
    db.delete(log)
    db.commit()
    return {"ok": True}