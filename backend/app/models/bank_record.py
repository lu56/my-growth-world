"""宝石银行（储蓄系统）

孩子可以将宝石存入银行（锁定余额），需要时取出。
存入 = 扣减可用余额 + 写入 bank_record
取出 = 返还可用余额 + 写入 bank_record
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BankRecord(Base):
    __tablename__ = "bank_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child.id"), nullable=False)
    # deposit(存入) / withdraw(取出) / interest(利息)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # 存入/取出后的银行余额
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
