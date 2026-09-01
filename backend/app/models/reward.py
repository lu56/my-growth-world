"""奖励商城配置"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reward(Base):
    __tablename__ = "reward"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    # 所需积分
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    # 资源图标键
    icon: Mapped[str] = mapped_column(String(100), default="reward_generic.png")
    # 是否启用
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # 是否为大额心愿目标
    is_wish: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)