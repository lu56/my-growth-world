"""亲子任务商店接口

家长发布挑战任务 -> 孩子接受 -> 孩子完成(标记) -> 家长确认发奖励
状态流：available -> accepted -> pending_review -> completed
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ShopTask
from app.schemas.schemas import ShopTaskCreate, ShopTaskUpdate
from app.services.achievement_service import check_achievements
from app.services.score_service import (
    add_score,
    check_score_limit,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)
from app.api.achievements import ach_brief_full


def _ach_brief(a):
    return ach_brief_full(a)


def _task_to_dict(t: ShopTask) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "reward": t.reward,
        "icon": t.icon,
        "status": t.status,
        "enabled": t.enabled,
        "accepted_at": t.accepted_at.strftime("%Y-%m-%d %H:%M") if t.accepted_at else None,
        "completed_at": t.completed_at.strftime("%Y-%m-%d %H:%M") if t.completed_at else None,
        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else None,
    }


router = APIRouter(prefix="/shop", tags=["亲子任务商店"])


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    """获取所有任务商店任务"""
    tasks = (
        db.execute(select(ShopTask).order_by(ShopTask.created_at.desc()))
        .scalars()
        .all()
    )
    return [_task_to_dict(t) for t in tasks]


@router.post("")
def create_task(body: ShopTaskCreate, db: Session = Depends(get_db)):
    """家长创建挑战任务"""
    task = ShopTask(
        title=body.title,
        description=body.description,
        reward=body.reward,
        icon=body.icon or "shop_challenge",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


@router.put("/{task_id}")
def update_task(task_id: int, body: ShopTaskUpdate, db: Session = Depends(get_db)):
    """家长修改任务"""
    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return _task_to_dict(task)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """家长删除任务"""
    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.post("/{task_id}/accept")
def accept_task(task_id: int, db: Session = Depends(get_db)):
    """孩子接受任务"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    task = db.get(ShopTask, task_id)
    if not task or not task.enabled:
        raise HTTPException(404, "任务不存在或已下架")
    if task.status != "available":
        raise HTTPException(400, "任务已被接受")

    task.status = "accepted"
    task.child_id = child.id
    task.accepted_at = datetime.now(timezone.utc)
    db.commit()
    return _task_to_dict(task)


@router.post("/{task_id}/submit")
def submit_task(task_id: int, db: Session = Depends(get_db)):
    """孩子提交任务完成（等待家长确认）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    if task.status != "accepted":
        raise HTTPException(400, "任务不在已接受状态")
    if task.child_id != child.id:
        raise HTTPException(403, "这不是你接受的任务")

    task.status = "pending_review"
    db.commit()
    return _task_to_dict(task)


@router.post("/{task_id}/confirm")
def confirm_task(task_id: int, db: Session = Depends(get_db)):
    """家长确认任务完成，发放奖励"""
    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    if task.status != "pending_review":
        raise HTTPException(400, "任务不在待确认状态")

    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    # 积分上限校验
    limit_err = check_score_limit(db, child.id, task.reward)
    if limit_err:
        raise HTTPException(400, limit_err)

    # 加分
    lifetime_before = get_child_lifetime_score(db, child.id)
    record = add_score(
        db,
        child.id,
        record_type="reward",
        score_delta=task.reward,
        reason=f"挑战任务完成：{task.title}",
        operator="家长",
    )
    lifetime_after = get_child_lifetime_score(db, child.id)
    level_change = get_level_before_after(db, child.id, lifetime_before, lifetime_after)

    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)

    # 成就检测
    new_ach = check_achievements(db, child.id, event_type="score")
    db.commit()

    from app.api.achievements import RARITY_GLOW

    return {
        "task": _task_to_dict(task),
        "balance": get_child_balance(db, child.id),
        "level": get_level_progress(db, child.id),
        "level_change": level_change,
        "new_achievements": [_ach_brief(a) for a in new_ach],
    }


@router.post("/{task_id}/reject")
def reject_task(task_id: int, db: Session = Depends(get_db)):
    """家长驳回（退回已接受状态，孩子需重新完成）"""
    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    if task.status != "pending_review":
        raise HTTPException(400, "任务不在待确认状态")

    task.status = "accepted"
    db.commit()
    return _task_to_dict(task)


@router.post("/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """孩子取消已接受的任务（退回商店）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    task = db.get(ShopTask, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    if task.status != "accepted":
        raise HTTPException(400, "任务不在已接受状态")
    if task.child_id != child.id:
        raise HTTPException(403, "这不是你接受的任务")

    task.status = "available"
    task.child_id = None
    task.accepted_at = None
    db.commit()
    return _task_to_dict(task)
