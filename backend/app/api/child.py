"""孩子接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Child
from app.schemas.schemas import ChildOut, ChildUpdate
from app.services.score_service import get_child

router = APIRouter(prefix="/child", tags=["孩子"])


@router.get("", response_model=ChildOut)
def read_child(db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    return child


@router.put("", response_model=ChildOut)
def update_child(body: ChildUpdate, db: Session = Depends(get_db)):
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")
    if body.name is not None:
        child.name = body.name
    if body.avatar is not None:
        child.avatar = body.avatar
    db.commit()
    db.refresh(child)
    return child