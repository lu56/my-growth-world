"""家长配置接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_parent
from app.core.database import get_db
from app.core.security import hash_password
from app.models import ParentConfig
from app.schemas.schemas import ParentConfigOut, ParentConfigUpdate

router = APIRouter(prefix="/parent", tags=["家长配置"])


@router.get("/config", response_model=ParentConfigOut, dependencies=[Depends(require_parent)])
def get_config(db: Session = Depends(get_db)):
    config = db.query(ParentConfig).first()
    return ParentConfigOut(
        daily_score_limit=config.daily_score_limit if config else 0,
        weekly_score_limit=config.weekly_score_limit if config else 0,
        bank_interest_rate=config.bank_interest_rate if config else 2,
    )


@router.put("/config", response_model=ParentConfigOut, dependencies=[Depends(require_parent)])
def update_config(body: ParentConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(ParentConfig).first()
    if not config:
        raise HTTPException(404, "配置不存在")
    if body.new_password:
        config.password_hash = hash_password(body.new_password)
    if body.new_child_password:
        config.child_password_hash = hash_password(body.new_child_password)
    if body.daily_score_limit is not None:
        config.daily_score_limit = body.daily_score_limit
    if body.weekly_score_limit is not None:
        config.weekly_score_limit = body.weekly_score_limit
    if body.bank_interest_rate is not None:
        config.bank_interest_rate = body.bank_interest_rate
    db.commit()
    return ParentConfigOut(
        daily_score_limit=config.daily_score_limit,
        weekly_score_limit=config.weekly_score_limit,
        bank_interest_rate=config.bank_interest_rate,
    )