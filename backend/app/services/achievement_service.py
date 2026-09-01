"""成就系统：自动检测解锁 + 段位升级

段位体系：0=未解锁, 1=青铜, 2=白银, 3=黄金, 4=钻石
每个成就通过 tier_thresholds（JSON 数组）定义各段位所需阈值。
当累计进度跨过某个阈值时，成就自动升级到对应段位。
"""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Achievement,
    BankRecord,
    CheckinStreak,
    DailyCheckin,
    ExchangeRecord,
    PersonalGoal,
    ScoreRecord,
    ShopTask,
    TaskRule,
)
from app.services.score_service import get_child_lifetime_score


def _get_achievement(db: Session, child_id: int, code: str) -> Achievement | None:
    return db.scalar(
        select(Achievement).where(
            Achievement.child_id == child_id, Achievement.code == code
        )
    )


def _parse_thresholds(ach: Achievement) -> list[int]:
    """解析段位阈值 JSON，如 '[3,7,15,30]' -> [3,7,15,30]"""
    try:
        thresholds = json.loads(ach.tier_thresholds or "[1]")
        if not isinstance(thresholds, list) or not thresholds:
            return [1]
        return [int(t) for t in thresholds]
    except Exception:
        return [1]


def _tier_for_progress(progress: int, thresholds: list[int]) -> int:
    """根据累计进度计算应达段位"""
    tier = 0
    for i, t in enumerate(thresholds):
        if progress >= t:
            tier = i + 1
        else:
            break
    return tier


def _max_tier(thresholds: list[int]) -> int:
    """段位总数"""
    return len(thresholds)


def upgrade(db: Session, achievement: Achievement, new_tier: int):
    """将成就升级到指定段位"""
    if new_tier > achievement.current_tier:
        if achievement.current_tier == 0:
            # 首次解锁
            achievement.unlocked = True
            achievement.unlocked_at = datetime.now(timezone.utc)
        achievement.current_tier = new_tier


def check_achievements(db: Session, child_id: int, event_type: str = "score"):
    """根据事件触发成就检测。

    返回 [(achievement, old_tier, new_tier), ...]，仅包含本次段位有变化的成就。
    """
    changed = []
    all_ach = db.execute(
        select(Achievement).where(Achievement.child_id == child_id)
    ).scalars()

    for ach in all_ach:
        thresholds = _parse_thresholds(ach)
        prog = _compute_progress(db, child_id, ach)
        ach.progress = prog
        new_tier = _tier_for_progress(prog, thresholds)
        if new_tier > ach.current_tier:
            old_tier = ach.current_tier
            upgrade(db, ach, new_tier)
            changed.append((ach, old_tier, new_tier))
    db.flush()
    return changed


# ---------------------------------------------------------------------------
# 进度计算（按 code 分派）
# ---------------------------------------------------------------------------

def _compute_progress(db: Session, child_id: int, ach: Achievement) -> int:
    code = ach.code
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if code == "first_score":
        return _count_first_score(db, child_id)

    if code == "score_master":
        return get_child_lifetime_score(db, child_id)

    if code == "first_exchange":
        return _count_exchanges(db, child_id)

    if code == "exchange_master":
        return _count_exchanges(db, child_id)

    if code == "study_streak":
        return _task_streak_by_type(db, child_id, today, "学习", days=30)

    if code == "homework_master":
        return _count_task_like(db, child_id, "%作业%")

    if code == "reading_star":
        return _count_task_like(db, child_id, "%阅读%")

    if code == "clean_expert":
        return _count_task_like(db, child_id, "%整理%")

    if code == "helper":
        return _count_task_like(db, child_id, "%帮助%")

    if code == "early_bird":
        return _count_task_like(db, child_id, "%早起%")

    if code == "sleep_master":
        return _count_task_like(db, child_id, "%睡觉%")

    if code == "early_bird_streak":
        return _task_streak_by_like(db, child_id, today, "%早起%", days=30)

    if code == "challenge_taker":
        return _count_shop_tasks(db, child_id, statuses=("accepted", "completed"))

    if code == "challenge_master":
        return _count_shop_tasks(db, child_id, statuses=("completed",))

    if code == "checkin_streak":
        return _longest_checkin_streak(db, child_id)

    if code == "checkin_total":
        return _count_checkins(db, child_id)

    if code == "goal_setter":
        return _count_goals(db, child_id)

    if code == "goal_achiever":
        return _count_goals(db, child_id, completed_only=True)

    if code == "saver":
        return _count_deposits(db, child_id)

    if code == "wealth_master":
        return _max_bank_balance(db, child_id)

    return 0


# ---------------------------------------------------------------------------
# 各类进度计算的辅助函数
# ---------------------------------------------------------------------------

def _count_first_score(db: Session, child_id: int) -> int:
    return 1 if db.scalar(
        select(func.count()).where(
            ScoreRecord.child_id == child_id,
            ScoreRecord.score_delta > 0,
            ScoreRecord.record_type != "exchange",
        )
    ) else 0


def _count_exchanges(db: Session, child_id: int) -> int:
    return db.scalar(
        select(func.count()).where(ExchangeRecord.child_id == child_id)
    ) or 0


def _count_task_like(db: Session, child_id: int, pattern: str) -> int:
    """累计完成名称匹配 pattern 的任务次数"""
    return db.scalar(
        select(func.count())
        .select_from(ScoreRecord)
        .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
        .where(
            ScoreRecord.child_id == child_id,
            ScoreRecord.record_type == "reward",
            TaskRule.name.like(pattern),
        )
    ) or 0


def _task_streak_by_type(
    db: Session, child_id: int, today: datetime, task_type: str, days: int = 30
) -> int:
    """统计最近连续 days 天内，有多少天有指定类型任务的奖励记录"""
    streak = 0
    for i in range(days):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.scalar(
            select(func.count())
            .select_from(ScoreRecord)
            .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
            .where(
                ScoreRecord.child_id == child_id,
                ScoreRecord.record_type == "reward",
                ScoreRecord.created_at >= day_start,
                ScoreRecord.created_at < day_end,
                TaskRule.task_type == task_type,
            )
        )
        if count:
            streak += 1
        else:
            break
    return streak


def _task_streak_by_like(
    db: Session, child_id: int, today: datetime, pattern: str, days: int = 30
) -> int:
    """统计最近连续多少天完成名称匹配 pattern 的任务"""
    streak = 0
    for i in range(days):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.scalar(
            select(func.count())
            .select_from(ScoreRecord)
            .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
            .where(
                ScoreRecord.child_id == child_id,
                ScoreRecord.record_type == "reward",
                ScoreRecord.created_at >= day_start,
                ScoreRecord.created_at < day_end,
                TaskRule.name.like(pattern),
            )
        )
        if count:
            streak += 1
        else:
            break
    return streak


def _count_shop_tasks(
    db: Session, child_id: int, statuses: tuple
) -> int:
    """统计指定状态的挑战任务数量"""
    return db.scalar(
        select(func.count()).where(
            ShopTask.child_id == child_id,
            ShopTask.status.in_(statuses),
        )
    ) or 0


def _count_checkins(db: Session, child_id: int) -> int:
    return db.scalar(
        select(func.count()).where(DailyCheckin.child_id == child_id)
    ) or 0


def _longest_checkin_streak(db: Session, child_id: int) -> int:
    """取所有打卡任务中最长的连续打卡天数"""
    rows = db.scalars(
        select(CheckinStreak).where(CheckinStreak.child_id == child_id)
    ).all()
    return max((r.longest_streak or 0 for r in rows), default=0)


def _count_goals(
    db: Session, child_id: int, completed_only: bool = False
) -> int:
    cond = [PersonalGoal.child_id == child_id]
    if completed_only:
        cond.append(PersonalGoal.status == "completed")
    return db.scalar(select(func.count()).where(*cond)) or 0


def _count_deposits(db: Session, child_id: int) -> int:
    return db.scalar(
        select(func.count()).where(
            BankRecord.child_id == child_id,
            BankRecord.action == "deposit",
        )
    ) or 0


def _max_bank_balance(db: Session, child_id: int) -> int:
    """历史最高银行余额 = 所有存入/利息记录中 balance_after 的最大值"""
    return db.scalar(
        select(func.max(BankRecord.balance_after)).where(
            BankRecord.child_id == child_id,
            BankRecord.action.in_(["deposit", "interest"]),
        )
    ) or 0