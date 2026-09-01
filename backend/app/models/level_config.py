"""等级配置（只升不降）"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LevelConfig(Base):
    __tablename__ = "level_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    # 资源键（角色头像）
    icon: Mapped[str] = mapped_column(String(100), default="level_1.png")
    # 解锁描述
    description: Mapped[str] = mapped_column(String(255), default="")
    # 达到该等级所需累计积分
    min_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)