"""宝石银行接口

孩子可以将宝石存入银行（锁定余额），需要时取出。
存入不减少累计分（lifetime），只减少可用余额（balance）。
银行余额按周利率计提利息，孩子能看到"存钱会变多"。
"""
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import BankRecord, ParentConfig, ScoreRecord
from app.services.score_service import (
    add_score,
    get_child,
    get_child_balance,
    get_child_lifetime_score,
    get_level_before_after,
    get_level_progress,
)

router = APIRouter(prefix="/bank", tags=["宝石银行"])


def _get_bank_balance(db: Session, child_id: int) -> int:
    """银行余额 = 所有存入 - 所有取出 + 所有利息"""
    deposits = db.scalar(
        select(func.coalesce(func.sum(BankRecord.amount), 0)).where(
            BankRecord.child_id == child_id,
            BankRecord.action.in_(["deposit", "interest"]),
        )
    )
    withdrawals = db.scalar(
        select(func.coalesce(func.sum(BankRecord.amount), 0)).where(
            BankRecord.child_id == child_id,
            BankRecord.action == "withdraw",
        )
    )
    return int((deposits or 0) - (withdrawals or 0))


def _accrue_interest(db: Session, child_id: int):
    """按天累计利息：从上次结算日到今天，每天按 (周利率/7) 计提，存入银行余额。

    利息进银行（BankRecord action=interest），不进入可用余额/积分流水。
    """
    config = db.scalar(select(ParentConfig))
    if not config:
        return None

    rate = config.bank_interest_rate or 0
    if rate <= 0:
        # 利率为 0 或未设置，记录当前日为结算日
        config.last_interest_date = datetime.now(timezone.utc).date().isoformat()
        db.commit()
        return None

    today = datetime.now(timezone.utc).date()
    last = config.last_interest_date
    if not last:
        # 首次：标记结算日，从下次开始计息
        config.last_interest_date = today.isoformat()
        db.commit()
        return None

    try:
        last_date = date.fromisoformat(last)
    except ValueError:
        last_date = today
        config.last_interest_date = today.isoformat()
        db.commit()
        return None

    if today <= last_date:
        return None

    days = (today - last_date).days
    # 结算日推进到今天（防止重复计息）
    config.last_interest_date = today.isoformat()

    bank_balance = _get_bank_balance(db, child_id)
    if bank_balance <= 0:
        db.commit()
        return None

    daily_rate = rate / 100 / 7
    # 每天利滚利
    growth = bank_balance * ((1 + daily_rate) ** days) - bank_balance
    interest = int(growth)  # 向下取整
    if interest <= 0:
        db.commit()
        return None

    balance_after = _get_bank_balance(db, child_id) + interest
    record = BankRecord(
        child_id=child_id,
        action="interest",
        amount=interest,
        balance_after=balance_after,
    )
    db.add(record)
    db.commit()
    return interest


@router.get("")
def get_bank_status(db: Session = Depends(get_db)):
    """获取银行状态：银行余额 + 可用余额 + 利率 + 历史记录"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    # 先结算利息
    _accrue_interest(db, child.id)

    bank_balance = _get_bank_balance(db, child.id)
    wallet_balance = get_child_balance(db, child.id)

    config = db.scalar(select(ParentConfig))
    rate = config.bank_interest_rate if config else 0

    # 最近10条记录
    records = (
        db.execute(
            select(BankRecord)
            .where(BankRecord.child_id == child.id)
            .order_by(BankRecord.created_at.desc())
            .limit(10)
        )
        .scalars()
        .all()
    )

    # 明日预估利息（当日余额 * 日利率，向下取整）
    today_interest = int(bank_balance * (rate / 100 / 7)) if rate > 0 else 0

    return {
        "bank_balance": bank_balance,
        "wallet_balance": wallet_balance,
        "total_balance": bank_balance + wallet_balance,
        "interest_rate": rate,
        "today_interest": today_interest,
        "expected_tomorrow": bank_balance + today_interest,
        "records": [
            {
                "id": r.id,
                "action": r.action,
                "amount": r.amount,
                "balance_after": r.balance_after,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
                if r.created_at
                else None,
            }
            for r in records
        ],
    }


@router.post("/deposit")
def deposit(amount: int, db: Session = Depends(get_db)):
    """存入宝石到银行"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    _accrue_interest(db, child.id)

    if amount <= 0:
        raise HTTPException(400, "存入数量必须大于0")

    wallet = get_child_balance(db, child.id)
    if amount > wallet:
        raise HTTPException(400, f"可用宝石不足（当前{wallet}）")

    # 扣减可用余额（记一笔负数流水）
    add_score(
        db,
        child.id,
        record_type="adjust",
        score_delta=-amount,
        reason="存入宝石银行",
        operator="银行",
    )

    # 写银行记录
    bank_balance_after = _get_bank_balance(db, child.id) + amount
    record = BankRecord(
        child_id=child.id,
        action="deposit",
        amount=amount,
        balance_after=bank_balance_after,
    )
    db.add(record)
    db.commit()

    return {
        "ok": True,
        "bank_balance": bank_balance_after,
        "wallet_balance": get_child_balance(db, child.id),
        "total_balance": bank_balance_after + get_child_balance(db, child.id),
    }


@router.post("/withdraw")
def withdraw(amount: int, db: Session = Depends(get_db)):
    """从银行取出宝石"""
    child = get_child(db)
    if not child:
        raise HTTPException(404, "尚未创建孩子档案")

    _accrue_interest(db, child.id)

    if amount <= 0:
        raise HTTPException(400, "取出数量必须大于0")

    bank_balance = _get_bank_balance(db, child.id)
    if amount > bank_balance:
        raise HTTPException(400, f"银行宝石不足（当前{bank_balance}）")

    # 返还可用余额
    add_score(
        db,
        child.id,
        record_type="adjust",
        score_delta=amount,
        reason="从宝石银行取出",
        operator="银行",
    )

    # 写银行记录
    bank_balance_after = bank_balance - amount
    record = BankRecord(
        child_id=child.id,
        action="withdraw",
        amount=amount,
        balance_after=bank_balance_after,
    )
    db.add(record)
    db.commit()

    return {
        "ok": True,
        "bank_balance": bank_balance_after,
        "wallet_balance": get_child_balance(db, child.id),
        "total_balance": bank_balance_after + get_child_balance(db, child.id),
    }
