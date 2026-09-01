"""孩子个人目标接口"""
import math
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import PersonalGoal, ScoreRecord
from app.schemas.schemas import GoalCreate
from app.services.achievement_service import check_achievements
from app.services.score_service import (
    add_score,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)

router = APIRouter(prefix="/goals", tags=["个人目标"])

from app.api.achievements import ach_brief_full


def _ach_brief(a):
    return ach_brief_full(a)


def _goal_to_dict(g: PersonalGoal, db: Session) -> dict:
    """转换目标对象为响应字典，含实时进度"""
    progress_ratio = 0.0
    if g.target_score > 0:
        progress_ratio = min(g.progress_score / g.target_score, 1.0)

    return {
        "id": g.id,
        "title": g.title,
        "description": g.description,
        "target_score": g.target_score,
        "bonus_score": g.bonus_score,
        "status": g.status,
        "approved_at": g.approved_at.strftime("%Y-%m-%d %H:%M") if g.approved_at else None,
        "completed_at": g.completed_at.strftime("%Y-%m-%d %H:%M") if g.completed_at else None,
        "deadline": g.deadline.strftime("%Y-%m-%d") if g.deadline else None,
        "progress_score": g.progress_score,
        "progress_ratio": round(progress_ratio, 2),
        "created_at": g.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def _refresh_goal_progress(db: Session, goal: PersonalGoal):
    """重新计算目标进度（通过后从审批时间开始累计加分）"""
    if goal.status != "approved" or not goal.approved_at:
        return

    # 从审批时间到现在的加分总和
    total = db.scalar(
        select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
            ScoreRecord.child_id == goal.child_id,
            ScoreRecord.score_delta > 0,
            ScoreRecord.record_type != "exchange",
            ScoreRecord.created_at >= goal.approved_at,
        )
    )
    goal.progress_score = int(total or 0)

    # 检查是否达成
    if goal.progress_score >= goal.target_score and goal.status == "approved":
        goal.status = "completed"
        goal.completed_at = datetime.now(timezone.utc)
        # 发放奖励
        lifetime_before = get_child_lifetime_score(db, goal.child_id)
        add_score(
            db,
            goal.child_id,
            record_type="reward",
            score_delta=goal.bonus_score,
            reason=f"目标达成奖励：{goal.title}",
            operator="系统",
        )


@router.get("")
def list_goals(db: Session = Depends(get_db)):
    """获取目标列表"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    goals = db.execute(
        select(PersonalGoal)
        .where(PersonalGoal.child_id == child.id)
        .order_by(PersonalGoal.created_at.desc())
    ).scalars().all()

    # 刷新进度
    for g in goals:
        _refresh_goal_progress(db, g)
    db.commit()

    return [_goal_to_dict(g, db) for g in goals]


@router.post("")
def create_goal(body: GoalCreate, db: Session = Depends(get_db)):
    """孩子提交新目标"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    bonus = math.ceil(body.target_score * 0.1)
    deadline = None
    if body.deadline:
        try:
            deadline = date.fromisoformat(body.deadline)
        except ValueError:
            raise HTTPException(400, "截止日期格式错误")

    goal = PersonalGoal(
        child_id=child.id,
        title=body.title,
        description=body.description,
        target_score=body.target_score,
        bonus_score=bonus,
        status="pending",
        deadline=deadline,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _goal_to_dict(goal, db)


@router.put("/{goal_id}/approve")
def approve_goal(goal_id: int, db: Session = Depends(get_db)):
    """家长审批通过"""
    goal = db.get(PersonalGoal, goal_id)
    if not goal:
        raise HTTPException(404, "目标不存在")
    if goal.status != "pending":
        raise HTTPException(400, "目标不是待审批状态")

    goal.status = "approved"
    goal.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(goal)
    return _goal_to_dict(goal, db)


@router.put("/{goal_id}/reject")
def reject_goal(goal_id: int, db: Session = Depends(get_db)):
    """家长拒绝目标"""
    goal = db.get(PersonalGoal, goal_id)
    if not goal:
        raise HTTPException(404, "目标不存在")
    if goal.status != "pending":
        raise HTTPException(400, "目标不是待审批状态")

    goal.status = "rejected"
    db.commit()
    db.refresh(goal)
    return _goal_to_dict(goal, db)


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """删除目标"""
    goal = db.get(PersonalGoal, goal_id)
    if not goal:
        raise HTTPException(404, "目标不存在")
    db.delete(goal)
    db.commit()
    return {"ok": True}
