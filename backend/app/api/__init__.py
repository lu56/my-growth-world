"""API 路由汇总"""
from fastapi import APIRouter

from app.api import (
    achievements,
    auth,
    bank,
    checkin,
    child,
    data,
    goals,
    levels,
    logs,
    parent,
    report,
    rewards,
    scores,
    shop,
    tasks,
    tickets,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(child.router)
api_router.include_router(tasks.router)
api_router.include_router(scores.router)
api_router.include_router(levels.router)
api_router.include_router(achievements.router)
api_router.include_router(rewards.router)
api_router.include_router(logs.router)
api_router.include_router(parent.router)
api_router.include_router(checkin.router)
api_router.include_router(goals.router)
api_router.include_router(bank.router)
api_router.include_router(tickets.router)
api_router.include_router(report.router)
api_router.include_router(shop.router)
api_router.include_router(data.router)