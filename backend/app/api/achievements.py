"""成就接口"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Achievement
from app.schemas.schemas import AchievementOut
from app.services.achievement_service import check_achievements
from app.services.score_service import get_child

# 稀有度光效配置（由段位上限决定）
RARITY_GLOW = {
    "common": {"color": "#fbbf24", "intensity": "low", "label": "普通"},
    "rare": {"color": "#f59e0b", "intensity": "medium", "label": "稀有"},
    "epic": {"color": "#a855f7", "intensity": "high", "label": "史诗"},
    "legendary": {"color": "#ef4444", "intensity": "legendary", "label": "传说"},
}

# 段位元数据
TIER_META = {
    0: {"label": "未解锁", "color": "#9e9e9e", "intensity": "none"},
    1: {"label": "青铜", "color": "#cd7f32", "intensity": "low"},
    2: {"label": "白银", "color": "#c0c0c0", "intensity": "medium"},
    3: {"label": "黄金", "color": "#ffd700", "intensity": "high"},
    4: {"label": "钻石", "color": "#b9f2ff", "intensity": "legendary"},
}

# 成就类别显示信息
CATEGORY_META = {
    "study": {"label": "学习", "icon": "📖"},
    "chore": {"label": "家务", "icon": "🧹"},
    "habit": {"label": "习惯", "icon": "⏰"},
    "score": {"label": "积分", "icon": "💎"},
    "exchange": {"label": "兑换", "icon": "🎁"},
    "challenge": {"label": "挑战", "icon": "⚔️"},
    "checkin": {"label": "打卡", "icon": "📅"},
    "goal": {"label": "目标", "icon": "🚩"},
    "bank": {"label": "银行", "icon": "🐷"},
}


def _parse_thresholds(ach) -> list[int]:
    try:
        thresholds = json.loads(ach.tier_thresholds or "[1]")
        if not isinstance(thresholds, list) or not thresholds:
            return [1]
        return [int(t) for t in thresholds]
    except Exception:
        return [1]


def ach_tier_dict(ach: Achievement) -> dict:
    """将成就对象转换为响应字典（含段位信息）"""
    thresholds = _parse_thresholds(ach)
    max_tier = len(thresholds)

    # 段位稀有度：段位越多越稀有
    rarity = "common"
    if max_tier >= 4:
        rarity = "legendary"
    elif max_tier == 3:
        rarity = "epic"
    elif max_tier == 2:
        rarity = "rare"

    glow = RARITY_GLOW.get(rarity, RARITY_GLOW["common"])
    tier = ach.current_tier
    tier_meta = TIER_META.get(tier, TIER_META[0])

    # 下一个段位阈值
    next_threshold = None
    if tier < max_tier:
        next_threshold = thresholds[tier]  # 索引 tier 对应下一段位

    progress_ratio = 0.0
    if next_threshold and next_threshold > 0:
        progress_ratio = min(ach.progress / next_threshold, 1.0)

    # 目标值 = 最高段位阈值（兼容）
    target_value = thresholds[-1] if thresholds else ach.target_value

    cat = CATEGORY_META.get(ach.category, {"label": "其他", "icon": "🏅"})

    return {
        "id": ach.id,
        "code": ach.code,
        "name": ach.name,
        "description": ach.description,
        "icon": ach.icon,
        "rarity": rarity,
        "rarity_label": glow["label"],
        "rarity_glow": glow["color"],
        "rarity_intensity": glow["intensity"],
        "category": ach.category,
        "category_label": cat["label"],
        "category_icon": cat["icon"],
        "unlocked": ach.unlocked,
        "unlocked_at": ach.unlocked_at,
        "current_tier": tier,
        "tier_label": tier_meta["label"],
        "tier_color": tier_meta["color"],
        "tier_intensity": tier_meta["intensity"],
        "max_tier": max_tier,
        "next_threshold": next_threshold,
        "tier_thresholds": thresholds,
        "progress": ach.progress,
        "target_value": target_value,
        "progress_ratio": round(progress_ratio, 2),
    }


def ach_brief_full(item) -> dict:
    """统一转换 check_achievements 返回的 (ach, old_tier, new_tier) 元组"""
    if isinstance(item, tuple):
        ach, old_tier, new_tier = item
    else:
        ach = item
        old_tier, new_tier = 0, ach.current_tier
    data = ach_tier_dict(ach)
    data["old_tier"] = old_tier
    data["new_tier"] = new_tier
    data["is_upgrade"] = old_tier > 0
    return data


router = APIRouter(prefix="/achievements", tags=["成就"])


@router.get("", response_model=list[dict])
def list_achievements(db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    # 每次访问时重新检测成就（确保进度实时更新）
    check_achievements(db, child.id, event_type="view")
    db.commit()

    achievements = (
        db.query(Achievement)
        .filter(Achievement.child_id == child.id)
        .order_by(Achievement.category, Achievement.target_value)
        .all()
    )

    return [ach_tier_dict(ach) for ach in achievements]