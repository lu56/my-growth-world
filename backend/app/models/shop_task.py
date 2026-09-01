"""亲子任务商店

家长发布额外挑战任务（带宝石奖励），孩子可以选择接受并完成。
状态流：available(可接) -> accepted(已接受) -> completed(已完成,家长确认)
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ShopTask(Base):
    __tablename__ = "shop_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 任务标题
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    # 任务描述
    description: Mapped[str] = mapped_column(String(255), default="")
    # 奖励宝石数
    reward: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    # 任务类型图标键
    icon: Mapped[str] = mapped_column(String(50), default="shop_challenge")
    # 状态：available / accepted / completed / expired
    status: Mapped[str] = mapped_column(String(20), default="available")
    # 接受的孩子ID
    child_id: Mapped[int] = mapped_column(ForeignKey("child.id"), nullable=True)
    # 是否启用
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    accepted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
