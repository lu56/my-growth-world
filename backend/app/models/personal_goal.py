"""孩子个人目标设定"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PersonalGoal(Base):
    __tablename__ = "personal_goal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    # 目标积分数
    target_score: Mapped[int] = mapped_column(Integer, nullable=False)
    # 达成奖励（自动算 target_score * 10% 向上取整）
    bonus_score: Mapped[int] = mapped_column(Integer, default=0)
    # 状态：pending / approved / rejected / completed
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    # 通过后开始累计的积分
    progress_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
