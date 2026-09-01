"""积分业务逻辑：加/减分、兑换、等级计算、统计"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Child, ExchangeRecord, LevelConfig, ParentConfig, ScoreRecord
from app.models.reward import Reward


def get_child(db: Session) -> Child | None:
    """当前仅单孩子，取 slot=0"""
    return db.scalar(select(Child).where(Child.slot == 0))


def get_child_balance(db: Session, child_id: int) -> int:
    """当前积分余额 = 所有积分流水求和"""
    total = db.scalar(
        select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
            ScoreRecord.child_id == child_id
        )
    )
    return int(total or 0)


def get_child_lifetime_score(db: Session, child_id: int) -> int:
    """历史累计积分 = 所有加分之和（用于等级，只升不降）"""
    total = db.scalar(
        select(
            func.coalesce(
                func.sum(ScoreRecord.score_delta).filter(ScoreRecord.score_delta > 0),
                0,
            )
        ).where(ScoreRecord.child_id == child_id)
    )
    return int(total or 0)


def get_parent_config(db: Session) -> ParentConfig | None:
    return db.scalar(select(ParentConfig))


def check_score_limit(db: Session, child_id: int, score_delta: int) -> str | None:
    """检查单日/单周加分上限。返回错误信息或 None（通过）"""
    if score_delta <= 0:
        return None  # 只限制加分，不限制减分/兑换

    config = get_parent_config(db)
    if not config:
        return None

    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())

    # 单日上限
    if config.daily_score_limit > 0:
        daily_added = db.scalar(
            select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
                ScoreRecord.child_id == child_id,
                ScoreRecord.score_delta > 0,
                ScoreRecord.record_type != "exchange",
                ScoreRecord.created_at >= today,
            )
        )
        daily_added = int(daily_added or 0)
        if daily_added + score_delta > config.daily_score_limit:
            return f"今日已加分 {daily_added}，上限 {config.daily_score_limit}，无法继续加分"

    # 单周上限
    if config.weekly_score_limit > 0:
        weekly_added = db.scalar(
            select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
                ScoreRecord.child_id == child_id,
                ScoreRecord.score_delta > 0,
                ScoreRecord.record_type != "exchange",
                ScoreRecord.created_at >= week_start,
            )
        )
        weekly_added = int(weekly_added or 0)
        if weekly_added + score_delta > config.weekly_score_limit:
            return f"本周已加分 {weekly_added}，上限 {config.weekly_score_limit}，无法继续加分"

    return None


def get_level_before_after(
    db: Session, child_id: int, lifetime_before: int, lifetime_after: int
) -> dict:
    """对比加分前后等级变化，返回 level_up 信息"""
    level_before = _match_level(db, lifetime_before)
    level_after = _match_level(db, lifetime_after)

    if level_after and level_before and level_after.level > level_before.level:
        return {
            "level_up": True,
            "old_level": level_before.level,
            "old_level_name": level_before.name,
            "new_level": level_after.level,
            "new_level_name": level_after.name,
            "new_level_icon": level_after.icon,
            "new_level_description": level_after.description,
        }
    return {"level_up": False}


def _match_level(db: Session, lifetime: int):
    """根据累计积分匹配等级"""
    levels = db.execute(
        select(LevelConfig).order_by(LevelConfig.min_score.desc())
    ).scalars()
    for level in levels:
        if lifetime >= level.min_score:
            return level
    return db.scalar(select(LevelConfig).order_by(LevelConfig.level.asc()))


def add_score(
    db: Session,
    child_id: int,
    record_type: str,
    score_delta: int,
    reason: str = "",
    operator: str = "家长",
    task_rule_id: int | None = None,
) -> ScoreRecord:
    """写入积分流水"""
    record = ScoreRecord(
        child_id=child_id,
        task_rule_id=task_rule_id,
        record_type=record_type,
        score_delta=score_delta,
        reason=reason,
        operator=operator,
    )
    db.add(record)
    db.flush()
    return record


def exchange_reward(
    db: Session, child_id: int, reward_id: int, operator: str = "家长"
):
    reward = db.get(Reward, reward_id)
    if not reward or not reward.enabled:
        raise ValueError("奖励不存在或已下架")
    balance = get_child_balance(db, child_id)
    if balance < reward.cost:
        raise ValueError("魔法宝石不足，无法兑换")

    add_score(
        db,
        child_id,
        record_type="exchange",
        score_delta=-reward.cost,
        reason=f"兑换奖励：{reward.name}",
        operator=operator,
    )
    record = ExchangeRecord(
        child_id=child_id,
        reward_id=reward_id,
        reward_name=reward.name,
        cost=reward.cost,
        operator=operator,
    )
    db.add(record)
    db.flush()
    return record


def get_level_progress(db: Session, child_id: int) -> dict:
    """当前等级、下一等级、进度比例"""
    level, lifetime = get_current_level(db, child_id)
    next_level = db.scalar(
        select(LevelConfig).where(LevelConfig.level == level.level + 1)
    )
    result = {
        "level": level.level,
        "level_name": level.name,
        "level_icon": level.icon,
        "description": level.description,
        "min_score": level.min_score,
        "lifetime_score": lifetime,
    }
    if next_level:
        span = next_level.min_score - level.min_score
        cur = lifetime - level.min_score
        progress = cur / span if span > 0 else 0
        result["next_level"] = next_level.level
        result["next_level_name"] = next_level.name
        result["next_icon"] = next_level.icon
        result["next_min_score"] = next_level.min_score
        result["progress"] = min(max(progress, 0), 1)
    else:
        result["next_level"] = None
        result["progress"] = 1.0
    return result


def get_current_level(db: Session, child_id: int):
    """根据历史累计积分确定当前等级"""
    lifetime = get_child_lifetime_score(db, child_id)
    levels = db.execute(
        select(LevelConfig).order_by(LevelConfig.min_score.desc())
    ).scalars()
    for level in levels:
        if lifetime >= level.min_score:
            return level, lifetime
    first = db.scalar(select(LevelConfig).order_by(LevelConfig.level.asc()))
    return first, lifetime


def _period_between(db: Session, child_id: int, start: datetime, end: datetime) -> int:
    total = db.scalar(
        select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
            ScoreRecord.child_id == child_id,
            ScoreRecord.created_at >= start,
            ScoreRecord.created_at < end,
        )
    )
    return int(total or 0)


def get_dashboard(db: Session, child_id: int, days: int = 14) -> dict:
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    balance = get_child_balance(db, child_id)
    lifetime = get_child_lifetime_score(db, child_id)
    level = get_level_progress(db, child_id)

    pos = db.scalar(
        select(func.count()).where(
            ScoreRecord.child_id == child_id, ScoreRecord.score_delta > 0
        )
    )
    neg = db.scalar(
        select(func.count()).where(
            ScoreRecord.child_id == child_id, ScoreRecord.score_delta < 0
        )
    )
    exchange_count = db.scalar(
        select(func.count()).where(ExchangeRecord.child_id == child_id)
    )

    trend = []
    for i in range(days, 0, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_score = _period_between(db, child_id, day_start, day_end)
        trend.append({"date": day_start.strftime("%m-%d"), "score": day_score})

    # 分类统计（按任务类型）
    from app.models import TaskRule
    category_rows = db.execute(
        select(
            TaskRule.task_type,
            func.count().label("cnt"),
            func.sum(ScoreRecord.score_delta).label("total"),
        )
        .select_from(ScoreRecord)
        .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
        .where(
            ScoreRecord.child_id == child_id,
            ScoreRecord.record_type == "reward",
            ScoreRecord.score_delta > 0,
        )
        .group_by(TaskRule.task_type)
    ).all()
    category_breakdown = [
        {"category": r.task_type, "count": int(r.cnt), "total_score": int(r.total or 0)}
        for r in category_rows
    ]

    # 成就统计
    from app.models import Achievement
    ach_total = db.scalar(select(func.count()).where(Achievement.child_id == child_id)) or 0
    ach_unlocked = db.scalar(
        select(func.count()).where(Achievement.child_id == child_id, Achievement.unlocked == True)
    ) or 0
    achievement_stats = {
        "total": int(ach_total),
        "unlocked": int(ach_unlocked),
        "completion_rate": round(int(ach_unlocked) / int(ach_total), 2) if ach_total else 0,
    }

    # 近7天明细
    recent_7d_detail = []
    for i in range(6, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        records = db.execute(
            select(ScoreRecord).where(
                ScoreRecord.child_id == child_id,
                ScoreRecord.created_at >= day_start,
                ScoreRecord.created_at < day_end,
            ).order_by(ScoreRecord.created_at)
        ).scalars().all()
        items = [{"reason": r.reason, "delta": r.score_delta, "type": r.record_type} for r in records]
        recent_7d_detail.append({
            "date": day_start.strftime("%m-%d"),
            "items": items,
        })

    return {
        "total_score": balance,
        "lifetime_score": lifetime,
        "today_score": _period_between(db, child_id, today, now),
        "week_score": _period_between(db, child_id, week_start, now),
        "month_score": _period_between(db, child_id, month_start, now),
        "positive_count": int(pos or 0),
        "negative_count": int(neg or 0),
        "exchange_count": int(exchange_count or 0),
        "trend": trend,
        "level": level,
        "category_breakdown": category_breakdown,
        "achievement_stats": achievement_stats,
        "recent_7d_detail": recent_7d_detail,
    }