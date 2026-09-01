"""任务规则"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskRule(Base):
    __tablename__ = "task_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 任务类型：学习 / 家务 / 习惯 / 品德 / 临时
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 积分值：正数=奖励，负数=惩罚
    score_value: Mapped[int] = mapped_column(Integer, nullable=False)
    # 是否启用
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # 资源图标键
    icon: Mapped[str] = mapped_column(String(100), default="task_generic.png")
    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # 备注说明
    description: Mapped[str] = mapped_column(String(255), default="")
    # 是否系统预置
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    # 是否可打卡（孩子端每日打卡）
    is_checkin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)