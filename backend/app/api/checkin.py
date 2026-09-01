"""每日打卡接口

流程：孩子提交打卡申请（request，仅记 pending 不加分）→ 家长确认（confirm，确认才加分+连续+里程碑+成就）。
"""
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CheckinStreak, DailyCheckin, TaskRule
from app.services.achievement_service import check_achievements
from app.api.achievements import ach_brief_full
from app.services.score_service import (
    add_score,
    check_score_limit,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)
from app.api.deps import require_parent, require_child

router = APIRouter(prefix="/checkin", tags=["每日打卡"])

# 里程碑奖励配置
MILESTONES = [
    (3, 5, "连续打卡3天！奖励5颗魔法宝石"),
    (7, 15, "连续打卡7天！奖励15颗魔法宝石"),
    (15, 30, "连续打卡15天！奖励30颗魔法宝石"),
    (30, 100, "连续打卡30天！奖励100颗魔法宝石"),
]


@router.get("/today")
def get_today_status(db: Session = Depends(get_db)):
    """获取今日打卡状态"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    today = datetime.now(timezone.utc).date()

    # 获取所有可打卡的任务
    tasks = db.execute(
        select(TaskRule).where(TaskRule.is_checkin == True, TaskRule.enabled == True).order_by(TaskRule.sort_order)
    ).scalars().all()

    # 获取今日已申请/已确认的记录
    today_checkins = db.execute(
        select(DailyCheckin).where(
            DailyCheckin.child_id == child.id,
            DailyCheckin.checkin_date == today,
        )
    ).scalars().all()
    checkin_map = {c.task_rule_id: c for c in today_checkins}

    # 获取连续天数
    result = []
    for t in tasks:
        streak = db.scalar(
            select(CheckinStreak).where(
                CheckinStreak.child_id == child.id,
                CheckinStreak.task_rule_id == t.id,
            )
        )
        rec = checkin_map.get(t.id)
        result.append({
            "task_rule_id": t.id,
            "task_name": t.name,
            "task_type": t.task_type,
            "score_value": t.score_value,
            "is_checkin": True,
            "checked_in_today": rec is not None,
            "checkin_id": rec.id if rec else None,
            "status": rec.status if rec else None,  # pending / confirmed
            "current_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
        })
    return result


@router.post("/request")
def request_checkin(task_rule_id: int, db: Session = Depends(get_db)):
    """孩子提交打卡申请（仅记 pending，不加分）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    today = datetime.now(timezone.utc).date()

    task = db.get(TaskRule, task_rule_id)
    if not task or not task.enabled or not task.is_checkin:
        raise HTTPException(404, "打卡任务不存在或不可用")

    existing = db.scalar(
        select(DailyCheckin).where(
            DailyCheckin.child_id == child.id,
            DailyCheckin.task_rule_id == task_rule_id,
            DailyCheckin.checkin_date == today,
        )
    )
    if existing:
        raise HTTPException(400, "今日已提交，等待家长确认")

    checkin = DailyCheckin(
        child_id=child.id,
        task_rule_id=task_rule_id,
        checkin_date=today,
        status="pending",
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    return {
        "ok": True,
        "checkin": {
            "id": checkin.id,
            "task_rule_id": task_rule_id,
            "status": "pending",
        },
    }


@router.post("/confirm/{checkin_id}")
def confirm_checkin(
    checkin_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_parent),
):
    """家长确认打卡申请（确认才加分+连续+里程碑+成就）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    checkin = db.get(DailyCheckin, checkin_id)
    if not checkin or checkin.child_id != child.id:
        raise HTTPException(404, "打卡记录不存在")
    if checkin.status == "confirmed":
        raise HTTPException(400, "该打卡已确认")

    task_rule_id = checkin.task_rule_id
    today = datetime.now(timezone.utc).date()
    task = db.get(TaskRule, task_rule_id)
    if not task:
        raise HTTPException(404, "任务不存在")

    # 积分上限校验
    limit_err = check_score_limit(db, child.id, task.score_value)
    if limit_err:
        raise HTTPException(400, limit_err)

    # 加分
    lifetime_before = get_child_lifetime_score(db, child.id)
    record = add_score(
        db,
        child.id,
        record_type="reward",
        score_delta=task.score_value,
        reason=task.name,
        operator="家长确认",
        task_rule_id=task_rule_id,
    )
    lifetime_after = get_child_lifetime_score(db, child.id)
    level_change = get_level_before_after(db, child.id, lifetime_before, lifetime_after)

    # 更新打卡状态
    checkin.status = "confirmed"
    checkin.score_record_id = record.id

    # 更新连续天数
    streak = db.scalar(
        select(CheckinStreak).where(
            CheckinStreak.child_id == child.id,
            CheckinStreak.task_rule_id == task_rule_id,
        )
    )
    if not streak:
        streak = CheckinStreak(
            child_id=child.id,
            task_rule_id=task_rule_id,
            current_streak=0,
            longest_streak=0,
            milestone_claimed="",
        )
        db.add(streak)

    # 判断连续：上次打卡是昨天则+1，否则重置为1
    yesterday = today.fromordinal(today.toordinal() - 1)
    if streak.last_checkin_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.last_checkin_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    # 检测里程碑
    milestone_reward = None
    for days, bonus, msg in MILESTONES:
        if streak.current_streak == days:
            milestone_record = add_score(
                db,
                child.id,
                record_type="score",
                score_delta=bonus,
                reason=f"连续打卡{days}天奖励",
                operator="系统",
            )
            streak.milestone_claimed = str(days)
            milestone_reward = {
                "milestone": days,
                "bonus": bonus,
                "message": msg,
            }
            break
        elif streak.current_streak > days and (not streak.milestone_claimed or int(streak.milestone_claimed) < days):
            streak.milestone_claimed = str(days)
            milestone_record = add_score(
                db,
                child.id,
                record_type="score",
                score_delta=bonus,
                reason=f"连续打卡{days}天奖励",
                operator="系统",
            )
            milestone_reward = {
                "milestone": days,
                "bonus": bonus,
                "message": msg,
            }

    # 成就检测
    new_ach = check_achievements(db, child.id, event_type="checkin")
    db.commit()

    return {
        "score_result": {
            "record": {
                "id": record.id,
                "score_delta": record.score_delta,
                "reason": record.reason,
                "created_at": record.created_at,
            },
            "balance": get_child_balance(db, child.id),
            "level": get_level_progress(db, child.id),
            "level_change": level_change,
            "new_achievements": [ach_brief_full(a) for a in new_ach],
        },
        "checkin": {
            "task_rule_id": task_rule_id,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
        },
        "milestone_reward": milestone_reward,
    }


@router.get("/pending")
def get_pending_checkins(
    db: Session = Depends(get_db),
    _: dict = Depends(require_parent),
):
    """家长查看待确认的打卡"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    records = db.execute(
        select(DailyCheckin).where(
            DailyCheckin.child_id == child.id,
            DailyCheckin.status == "pending",
        ).order_by(DailyCheckin.checkin_date.desc(), DailyCheckin.id.desc())
    ).scalars().all()

    result = []
    for r in records:
        task = db.get(TaskRule, r.task_rule_id)
        result.append({
            "id": r.id,
            "task_rule_id": r.task_rule_id,
            "task_name": task.name if task else "?",
            "score_value": task.score_value if task else 0,
            "checkin_date": r.checkin_date.strftime("%Y-%m-%d"),
        })
    return result


@router.get("/history")
def get_history(days: int = 30, db: Session = Depends(get_db)):
    """获取近N天打卡历史"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    today = datetime.now(timezone.utc).date()
    start_date = today.fromordinal(today.toordinal() - days + 1)

    records = db.execute(
        select(DailyCheckin).where(
            DailyCheckin.child_id == child.id,
            DailyCheckin.checkin_date >= start_date,
        ).order_by(DailyCheckin.checkin_date.desc())
    ).scalars().all()

    history = {}
    for r in records:
        task = db.get(TaskRule, r.task_rule_id)
        date_str = r.checkin_date.strftime("%Y-%m-%d")
        if date_str not in history:
            history[date_str] = []
        history[date_str].append({
            "task_rule_id": r.task_rule_id,
            "task_name": task.name if task else "?",
            "score_value": task.score_value if task else 0,
            "status": r.status,
        })

    return [{"date": d, "items": items} for d, items in sorted(history.items(), reverse=True)]

