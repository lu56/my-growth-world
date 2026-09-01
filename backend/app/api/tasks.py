"""任务规则接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import TaskRule
from app.schemas.schemas import (
    TaskRuleCreate,
    TaskRuleOut,
    TaskRuleUpdate,
)

router = APIRouter(prefix="/tasks", tags=["任务规则"])


@router.get("", response_model=list[TaskRuleOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(TaskRule).order_by(TaskRule.sort_order).all()


@router.post("", response_model=TaskRuleOut)
def create_task(body: TaskRuleCreate, db: Session = Depends(get_db)):
    task = TaskRule(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRuleOut)
def update_task(task_id: int, body: TaskRuleUpdate, db: Session = Depends(get_db)):
    task = db.get(TaskRule, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(TaskRule, task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    db.delete(task)
    db.commit()
    return {"ok": True}