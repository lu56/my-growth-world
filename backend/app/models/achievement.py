"""成就系统"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Achievement(Base):
    __tablename__ = "achievement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    # 资源图标键
    icon: Mapped[str] = mapped_column(String(100), default="achievement_common.png")
    # 稀有度：common / rare / epic / legendary（由段位上限决定）
    rarity: Mapped[str] = mapped_column(String(20), default="common")
    # 成就类别：study/chore/habit/score/exchange/challenge/checkin/goal/bank
    category: Mapped[str] = mapped_column(String(20), default="score")
    # 当前段位：0=未解锁, 1=青铜, 2=白银, 3=黄金, 4=钻石
    current_tier: Mapped[int] = mapped_column(Integer, default=0)
    # 各段位阈值 JSON：如 [3,7,15,30]（青铜3/白银7/黄金15/钻石30）
    tier_thresholds: Mapped[str] = mapped_column(String(100), default="[1]")
    # 是否已解锁（逻辑等价于 current_tier > 0，保留字段兼容）
    unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # 自动检测用：累计进度（如连续天数、累计积分）
    progress: Mapped[int] = mapped_column(Integer, default=0)
    # 达成所需进度阈值（兼容：等于最高段位阈值）
    target_value: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)