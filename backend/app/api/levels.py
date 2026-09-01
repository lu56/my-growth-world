"""等级接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import LevelConfig
from app.schemas.schemas import LevelConfigOut
from app.services.score_service import get_child, get_level_progress

router = APIRouter(prefix="/levels", tags=["等级"])


@router.get("", response_model=list[LevelConfigOut])
def list_levels(db: Session = Depends(get_db)):
    return db.query(LevelConfig).order_by(LevelConfig.level).all()


@router.get("/progress")
def level_progress(db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return get_level_progress(db, child.id)