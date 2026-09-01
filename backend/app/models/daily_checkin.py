"""每日打卡记录"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DailyCheckin(Base):
    __tablename__ = "daily_checkin"
    __table_args__ = (
        UniqueConstraint("child_id", "task_rule_id", "checkin_date", name="uq_checkin_daily"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    task_rule_id: Mapped[int] = mapped_column(Integer, nullable=False)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    # pending=孩子已申请（未加分） / confirmed=家长已确认（已加分）
    status: Mapped[str] = mapped_column(String(20), default="pending")
    score_record_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CheckinStreak(Base):
    """连续打卡统计"""
    __tablename__ = "checkin_streak"
    __table_args__ = (
        UniqueConstraint("child_id", "task_rule_id", name="uq_streak_task"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    task_rule_id: Mapped[int] = mapped_column(Integer, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_checkin_date: Mapped[date] = mapped_column(Date, nullable=True)
    # 已领取的最高里程碑："3" / "7" / "15" / "30" / ""
    milestone_claimed: Mapped[str] = mapped_column(String(50), default="")
