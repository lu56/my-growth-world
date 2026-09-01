"""成长日志（家庭成长档案）"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GrowthLog(Base):
    __tablename__ = "growth_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), default="")
    # 照片路径/资源键，逗号分隔（本阶段预留）
    photos: Mapped[str] = mapped_column(String(1000), default="")
    # 关联积分流水（可选）
    score_record_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)