"""成长简报接口

生成周报/月报数据汇总，包括：
- 本周积分趋势、分类统计、打卡天数
- 与上周对比
- 最常完成的任务、成就进展
- 鼓励语
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Achievement,
    CheckinStreak,
    DailyCheckin,
    ExchangeRecord,
    ScoreRecord,
    TaskRule,
)
from app.services.score_service import (
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_progress,
)

router = APIRouter(prefix="/report", tags=["成长简报"])

# 鼓励语池
ENCOURAGEMENTS = [
    "继续保持，你正在变得越来越棒！",
    "每一步积累都在让你更强大！",
    "坚持就是胜利，为你的努力点赞！",
    "你的成长速度令人惊叹！",
    "今天的付出，就是明天的收获！",
]

# 周 encouragements 按表现选择
GREAT_MSG = "本周表现非常出色，你是小小冒险家！"
GOOD_MSG = "本周表现不错，继续保持哦！"
NORMAL_MSG = "继续努力，相信你下周会更好！"


@router.get("/weekly")
def get_weekly_report(weeks_ago: int = Query(0, ge=0, le=4), db: Session = Depends(get_db)):
    """获取周报。weeks_ago=0 本周，1=上周，以此类推"""
    child = get_child(db)
    if not child:
        from fastapi import HTTPException
        raise HTTPException(404, "尚未创建孩子档案")

    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # 本周起始（周一）
    this_week_start = today - timedelta(days=today.weekday())
    # 目标周起始
    target_week_start = this_week_start - timedelta(weeks=weeks_ago)
    target_week_end = target_week_start + timedelta(days=7)

    # 上周对比
    prev_week_start = target_week_start - timedelta(days=7)
    prev_week_end = target_week_start

    # 本周加分总分
    def period_sum(start, end):
        total = db.scalar(
            select(func.coalesce(func.sum(ScoreRecord.score_delta), 0)).where(
                ScoreRecord.child_id == child.id,
                ScoreRecord.score_delta > 0,
                ScoreRecord.record_type != "exchange",
                ScoreRecord.created_at >= start,
                ScoreRecord.created_at < end,
            )
        )
        return int(total or 0)

    def period_count(start, end):
        cnt = db.scalar(
            select(func.count()).where(
                ScoreRecord.child_id == child.id,
                ScoreRecord.score_delta > 0,
                ScoreRecord.record_type != "exchange",
                ScoreRecord.created_at >= start,
                ScoreRecord.created_at < end,
            )
        )
        return int(cnt or 0)

    this_score = period_sum(target_week_start, target_week_end)
    prev_score = period_sum(prev_week_start, prev_week_end)
    this_count = period_count(target_week_start, target_week_end)
    prev_count = period_count(prev_week_start, prev_week_end)

    # 周变化
    score_change = this_score - prev_score
    if prev_score > 0:
        score_change_pct = round((score_change / prev_score) * 100)
    else:
        score_change_pct = 100 if this_score > 0 else 0

    # 每日趋势
    daily_trend = []
    for i in range(7):
        day_start = target_week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        daily_trend.append({
            "date": day_start.strftime("%m-%d"),
            "weekday": ["一", "二", "三", "四", "五", "六", "日"][i],
            "score": period_sum(day_start, day_end),
        })

    # 分类统计（本周）
    category_rows = db.execute(
        select(
            TaskRule.task_type,
            func.count().label("cnt"),
            func.sum(ScoreRecord.score_delta).label("total"),
        )
        .select_from(ScoreRecord)
        .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
        .where(
            ScoreRecord.child_id == child.id,
            ScoreRecord.record_type == "reward",
            ScoreRecord.score_delta > 0,
            ScoreRecord.created_at >= target_week_start,
            ScoreRecord.created_at < target_week_end,
        )
        .group_by(TaskRule.task_type)
        .order_by(func.sum(ScoreRecord.score_delta).desc())
    ).all()
    category_breakdown = [
        {"category": r.task_type, "count": int(r.cnt), "total_score": int(r.total or 0)}
        for r in category_rows
    ]

    # 打卡天数（本周有打卡记录的不同日期数）
    checkin_days = db.scalar(
        select(func.count(func.distinct(DailyCheckin.checkin_date))).where(
            DailyCheckin.child_id == child.id,
            DailyCheckin.checkin_date >= target_week_start.date(),
            DailyCheckin.checkin_date < target_week_end.date(),
        )
    ) or 0

    # 兑换次数
    exchange_cnt = db.scalar(
        select(func.count()).where(
            ExchangeRecord.child_id == child.id,
            ExchangeRecord.created_at >= target_week_start,
            ExchangeRecord.created_at < target_week_end,
        )
    ) or 0

    # 成就进展
    ach_total = db.scalar(select(func.count()).where(Achievement.child_id == child.id)) or 0
    ach_unlocked = db.scalar(
        select(func.count()).where(
            Achievement.child_id == child.id,
            Achievement.unlocked == True,
        )
    ) or 0

    # 最常完成的任务 top3
    top_tasks = db.execute(
        select(
            TaskRule.name,
            func.count().label("cnt"),
        )
        .select_from(ScoreRecord)
        .join(TaskRule, ScoreRecord.task_rule_id == TaskRule.id)
        .where(
            ScoreRecord.child_id == child.id,
            ScoreRecord.score_delta > 0,
            ScoreRecord.created_at >= target_week_start,
            ScoreRecord.created_at < target_week_end,
        )
        .group_by(TaskRule.name)
        .order_by(func.count().desc())
        .limit(3)
    ).all()
    top_task_list = [{"name": r.name, "count": int(r.cnt)} for r in top_tasks]

    # 鼓励语
    if this_score >= prev_score and this_score > 0:
        if score_change_pct >= 20:
            encouragement = GREAT_MSG
        else:
            encouragement = GOOD_MSG
    elif this_score > 0:
        encouragement = NORMAL_MSG
    else:
        encouragement = "新的一周，开始你的冒险吧！"

    # 周报日期范围
    date_range = f"{target_week_start.strftime('%m/%d')} - {(target_week_end - timedelta(days=1)).strftime('%m/%d')}"

    # 当前余额和等级
    balance = get_child_balance(db, child.id)
    level = get_level_progress(db, child.id)

    return {
        "date_range": date_range,
        "weeks_ago": weeks_ago,
        "summary": {
            "total_score": this_score,
            "task_count": this_count,
            "checkin_days": int(checkin_days),
            "exchange_count": int(exchange_cnt),
            "balance": balance,
            "level_name": level["level_name"],
            "lifetime_score": level["lifetime_score"],
        },
        "comparison": {
            "prev_score": prev_score,
            "score_change": score_change,
            "score_change_pct": score_change_pct,
            "prev_count": prev_count,
        },
        "daily_trend": daily_trend,
        "category_breakdown": category_breakdown,
        "top_tasks": top_task_list,
        "achievement_stats": {
            "total": int(ach_total),
            "unlocked": int(ach_unlocked),
        },
        "encouragement": encouragement,
    }
