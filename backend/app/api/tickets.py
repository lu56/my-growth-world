"""惊喜奖励券接口

家长创建奖励券 -> 孩子花宝石购买 -> 使用后标记已用。
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SurpriseTicket
from app.schemas.schemas import (
    SurpriseTicketCreate,
    SurpriseTicketUpdate,
)
from app.services.achievement_service import check_achievements
from app.services.score_service import (
    add_score,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)
from app.api.achievements import ach_brief_full


def _ach_brief(a):
    return ach_brief_full(a)


def _ticket_to_dict(t: SurpriseTicket) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "cost": t.cost,
        "icon": t.icon,
        "status": t.status,
        "enabled": t.enabled,
        "purchased_at": t.purchased_at.strftime("%Y-%m-%d %H:%M")
        if t.purchased_at
        else None,
        "used_at": t.used_at.strftime("%Y-%m-%d %H:%M") if t.used_at else None,
        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
        if t.created_at
        else None,
    }


router = APIRouter(prefix="/tickets", tags=["惊喜奖励券"])


@router.get("")
def list_tickets(db: Session = Depends(get_db)):
    """获取所有奖励券"""
    tickets = (
        db.execute(
            select(SurpriseTicket).order_by(SurpriseTicket.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_ticket_to_dict(t) for t in tickets]


@router.post("")
def create_ticket(body: SurpriseTicketCreate, db: Session = Depends(get_db)):
    """家长创建奖励券"""
    ticket = SurpriseTicket(
        name=body.name,
        description=body.description,
        cost=body.cost,
        icon=body.icon or "ticket_gift",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return _ticket_to_dict(ticket)


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int, body: SurpriseTicketUpdate, db: Session = Depends(get_db)
):
    """家长修改奖励券"""
    ticket = db.get(SurpriseTicket, ticket_id)
    if not ticket:
        raise HTTPException(404, "奖励券不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ticket, k, v)
    db.commit()
    db.refresh(ticket)
    return _ticket_to_dict(ticket)


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """家长删除奖励券"""
    ticket = db.get(SurpriseTicket, ticket_id)
    if not ticket:
        raise HTTPException(404, "奖励券不存在")
    db.delete(ticket)
    db.commit()
    return {"ok": True}


@router.post("/{ticket_id}/purchase")
def purchase_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """孩子花宝石购买奖励券"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    ticket = db.get(SurpriseTicket, ticket_id)
    if not ticket or not ticket.enabled:
        raise HTTPException(404, "奖励券不存在或已下架")
    if ticket.status != "available":
        raise HTTPException(400, "奖励券已被购买")

    balance = get_child_balance(db, child.id)
    if balance < ticket.cost:
        raise HTTPException(400, f"宝石不足（需要{ticket.cost}，当前{balance}）")

    # 扣减宝石
    lifetime_before = get_child_lifetime_score(db, child.id)
    add_score(
        db,
        child.id,
        record_type="exchange",
        score_delta=-ticket.cost,
        reason=f"购买奖励券：{ticket.name}",
        operator="奖励券",
    )
    lifetime_after = get_child_lifetime_score(db, child.id)
    level_change = get_level_before_after(
        db, child.id, lifetime_before, lifetime_after
    )

    # 更新券状态
    ticket.status = "purchased"
    ticket.child_id = child.id
    ticket.purchased_at = datetime.now(timezone.utc)

    # 成就检测
    new_ach = check_achievements(db, child.id, event_type="exchange")
    db.commit()

    return {
        "ticket": _ticket_to_dict(ticket),
        "balance": get_child_balance(db, child.id),
        "level": get_level_progress(db, child.id),
        "level_change": level_change,
        "new_achievements": [_ach_brief(a) for a in new_ach],
    }


@router.post("/{ticket_id}/use")
def use_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """使用奖励券（标记已用）"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    ticket = db.get(SurpriseTicket, ticket_id)
    if not ticket:
        raise HTTPException(404, "奖励券不存在")
    if ticket.status != "purchased":
        raise HTTPException(400, "奖励券不在待使用状态")

    ticket.status = "used"
    ticket.used_at = datetime.now(timezone.utc)
    db.commit()

    return _ticket_to_dict(ticket)
