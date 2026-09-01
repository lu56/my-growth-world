"""兑换记录"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExchangeRecord(Base):
    __tablename__ = "exchange_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child.id"), nullable=False)
    reward_id: Mapped[int] = mapped_column(ForeignKey("reward.id"), nullable=False)
    reward_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    operator: Mapped[str] = mapped_column(String(50), default="家长")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)