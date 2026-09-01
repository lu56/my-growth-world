"""积分流水（全程可追溯）"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScoreRecord(Base):
    __tablename__ = "score_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("child.id"), nullable=False)
    # 关联任务规则（可为空：临时自定义加减分）
    task_rule_id: Mapped[int] = mapped_column(
        ForeignKey("task_rule.id"), nullable=True
    )
    # 类型：reward(奖励) / penalty(惩罚) / exchange(兑换) / adjust(手动调整)
    record_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 分值：正=加分，负=减分
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    # 原因/备注
    reason: Mapped[str] = mapped_column(String(255), default="")
    # 操作人
    operator: Mapped[str] = mapped_column(String(50), default="家长")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )