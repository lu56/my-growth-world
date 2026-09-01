"""惊喜奖励券

家长创建惊喜奖励券（非物质奖励），孩子花宝石购买，使用后标记已用。
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SurpriseTicket(Base):
    __tablename__ = "surprise_ticket"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child.id"), nullable=True)
    # 奖励券名称（如"免做家务一次"、"额外看电视30分钟"）
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    # 购买所需宝石数
    cost: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    # 图标键（前端用）
    icon: Mapped[str] = mapped_column(String(50), default="ticket_gift")
    # 状态：available(可购买) / purchased(已购买待使用) / used(已使用)
    status: Mapped[str] = mapped_column(String(20), default="available")
    # 是否启用
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # 购买时间
    purchased_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # 使用时间
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
