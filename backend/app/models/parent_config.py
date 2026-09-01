"""家长配置：登录口令、单日/单周积分上限、银行利率等"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ParentConfig(Base):
    __tablename__ = "parent_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 家长登录密码（bcrypt 哈希）
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # 孩子登录密码（bcrypt 哈希）
    child_password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    # 单日加分上限（0=不限制）
    daily_score_limit: Mapped[int] = mapped_column(Integer, default=0)
    # 单周加分上限（0=不限制）
    weekly_score_limit: Mapped[int] = mapped_column(Integer, default=0)
    # 银行利率（每周 %，如 2 表示每周 2%）
    bank_interest_rate: Mapped[int] = mapped_column(Integer, default=2)
    # 上次银行利息结算日（YYYY-MM-DD 字符串）
    last_interest_date: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )