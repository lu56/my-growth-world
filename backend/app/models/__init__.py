"""SQLAlchemy 数据模型

表结构设计（详见 docs/数据库设计.md）：
- child           孩子信息
- score_record    积分流水
- task_rule       任务规则
- level_config    等级配置
- achievement     成就
- reward          奖励
- exchange_record 兑换记录
- growth_log      成长日志
- parent_config   家长配置（登录/规则上限等）
- daily_checkin   每日打卡记录
- checkin_streak  连续打卡统计
- personal_goal   孩子个人目标
- bank_record     宝石银行记录
- surprise_ticket 惊喜奖励券
- shop_task      亲子任务商店
"""
from app.models.child import Child
from app.models.task_rule import TaskRule
from app.models.score_record import ScoreRecord
from app.models.level_config import LevelConfig
from app.models.achievement import Achievement
from app.models.reward import Reward
from app.models.exchange_record import ExchangeRecord
from app.models.growth_log import GrowthLog
from app.models.parent_config import ParentConfig
from app.models.daily_checkin import DailyCheckin, CheckinStreak
from app.models.personal_goal import PersonalGoal
from app.models.bank_record import BankRecord
from app.models.surprise_ticket import SurpriseTicket
from app.models.shop_task import ShopTask

__all__ = [
    "Child",
    "TaskRule",
    "ScoreRecord",
    "LevelConfig",
    "Achievement",
    "Reward",
    "ExchangeRecord",
    "GrowthLog",
    "ParentConfig",
    "DailyCheckin",
    "CheckinStreak",
    "PersonalGoal",
    "BankRecord",
    "SurpriseTicket",
    "ShopTask",
]