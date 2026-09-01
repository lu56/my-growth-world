"""奖励商城接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ExchangeRecord, Reward
from app.schemas.schemas import (
    ExchangeRecordOut,
    ExchangeRequest,
    RewardCreate,
    RewardOut,
    RewardUpdate,
)
from app.services.achievement_service import check_achievements
from app.services.score_service import (
    exchange_reward,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)
from app.api.achievements import ach_brief_full


def _ach_brief(a):
    """成就简要信息（含段位/稀有度光效）"""
    return ach_brief_full(a)

router = APIRouter(prefix="/rewards", tags=["奖励商城"])


@router.get("", response_model=list[RewardOut])
def list_rewards(db: Session = Depends(get_db)):
    return db.query(Reward).order_by(Reward.sort_order).all()


@router.post("", response_model=RewardOut)
def create_reward(body: RewardCreate, db: Session = Depends(get_db)):
    reward = Reward(**body.model_dump())
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


@router.put("/{reward_id}", response_model=RewardOut)
def update_reward(reward_id: int, body: RewardUpdate, db: Session = Depends(get_db)):
    reward = db.get(Reward, reward_id)
    if not reward:
        raise HTTPException(404, "奖励不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(reward, k, v)
    db.commit()
    db.refresh(reward)
    return reward


@router.delete("/{reward_id}")
def delete_reward(reward_id: int, db: Session = Depends(get_db)):
    reward = db.get(Reward, reward_id)
    if not reward:
        raise HTTPException(404, "奖励不存在")
    db.delete(reward)
    db.commit()
    return {"ok": True}


@router.post("/exchange", response_model=dict)
def do_exchange(body: ExchangeRequest, db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    # 记录兑换前的累计积分（兑换不减累计，但记录用于上下文）
    lifetime_before = get_child_lifetime_score(db, child.id)

    try:
        record = exchange_reward(db, child.id, body.reward_id, body.operator)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # 等级变化检测（兑换不减少累计分，所以通常不会降级）
    lifetime_after = get_child_lifetime_score(db, child.id)
    level_change = get_level_before_after(db, child.id, lifetime_before, lifetime_after)

    newly = check_achievements(db, child.id, event_type="exchange")
    db.commit()

    return {
        "record": {
            "id": record.id,
            "reward_name": record.reward_name,
            "cost": record.cost,
            "created_at": record.created_at,
        },
        "balance": get_child_balance(db, child.id),
        "level": get_level_progress(db, child.id),
        "level_change": level_change,
        "new_achievements": [_ach_brief(a) for a in newly],
    }


@router.get("/history", response_model=list[ExchangeRecordOut])
def exchange_history(db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return (
        db.query(ExchangeRecord)
        .filter(ExchangeRecord.child_id == child.id)
        .order_by(ExchangeRecord.created_at.desc())
        .all()
    )
