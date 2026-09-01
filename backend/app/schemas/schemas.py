"""Pydantic 校验模型"""
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    password: str


class ChildOut(BaseModel):
    id: int
    name: str
    avatar: str

    class Config:
        from_attributes = True


class ChildUpdate(BaseModel):
    name: str | None = None
    avatar: str | None = None


class TaskRuleCreate(BaseModel):
    name: str
    task_type: str
    score_value: int
    enabled: bool = True
    icon: str = "task_generic.png"
    sort_order: int = 0
    description: str = ""
    is_checkin: bool = False


class TaskRuleUpdate(BaseModel):
    name: str | None = None
    task_type: str | None = None
    score_value: int | None = None
    enabled: bool | None = None
    icon: str | None = None
    sort_order: int | None = None
    description: str | None = None
    is_checkin: bool | None = None


class TaskRuleOut(BaseModel):
    id: int
    name: str
    task_type: str
    score_value: int
    enabled: bool
    icon: str
    description: str
    is_preset: bool
    is_checkin: bool = False

    class Config:
        from_attributes = True


class ScoreRecordCreate(BaseModel):
    task_rule_id: int | None = None
    score_delta: int | None = None  # 未关联任务时手动指定
    reason: str = ""
    operator: str = "家长"


class ScoreRecordOut(BaseModel):
    id: int
    child_id: int
    task_rule_id: int | None
    record_type: str
    score_delta: int
    reason: str
    operator: str
    created_at: object

    class Config:
        from_attributes = True


class LevelConfigOut(BaseModel):
    id: int
    level: int
    name: str
    icon: str
    description: str
    min_score: int

    class Config:
        from_attributes = True


class AchievementOut(BaseModel):
    id: int
    code: str
    name: str
    description: str
    icon: str
    rarity: str
    unlocked: bool
    unlocked_at: object | None = None
    progress: int
    target_value: int

    class Config:
        from_attributes = True


class RewardCreate(BaseModel):
    name: str
    description: str = ""
    cost: int
    icon: str = "reward_generic.png"
    enabled: bool = True
    is_wish: bool = False
    sort_order: int = 0


class RewardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cost: int | None = None
    icon: str | None = None
    enabled: bool | None = None
    is_wish: bool | None = None
    sort_order: int | None = None


class RewardOut(BaseModel):
    id: int
    name: str
    description: str
    cost: int
    icon: str
    enabled: bool
    is_wish: bool

    class Config:
        from_attributes = True


class ExchangeRequest(BaseModel):
    reward_id: int
    operator: str = "家长"


class ExchangeRecordOut(BaseModel):
    id: int
    child_id: int
    reward_id: int
    reward_name: str
    cost: int
    operator: str
    created_at: object

    class Config:
        from_attributes = True


class GrowthLogCreate(BaseModel):
    title: str
    content: str = ""
    photos: str = ""
    score_record_id: int | None = None


class GrowthLogOut(BaseModel):
    id: int
    child_id: int
    title: str
    content: str
    photos: str
    score_record_id: int | None
    created_at: object

    class Config:
        from_attributes = True


class ParentConfigUpdate(BaseModel):
    new_password: str | None = None
    new_child_password: str | None = None
    daily_score_limit: int | None = None
    weekly_score_limit: int | None = None
    bank_interest_rate: int | None = None


class ParentConfigOut(BaseModel):
    daily_score_limit: int
    weekly_score_limit: int
    bank_interest_rate: int = 2


class Dashboard(BaseModel):
    total_score: int
    today_score: int
    week_score: int
    month_score: int
    positive_count: int
    negative_count: int
    exchange_count: int
    trend: list[dict]
    growth_curve: list[dict]


# -------- 打卡 --------
class CheckinOut(BaseModel):
    task_rule_id: int
    task_name: str
    task_type: str
    score_value: int
    is_checkin: bool
    checked_in_today: bool
    current_streak: int
    longest_streak: int


class CheckinResult(BaseModel):
    score_result: dict
    checkin: dict
    milestone_reward: dict | None = None


# -------- 目标 --------
class GoalCreate(BaseModel):
    title: str
    description: str = ""
    target_score: int
    deadline: str | None = None  # YYYY-MM-DD


class GoalOut(BaseModel):
    id: int
    title: str
    description: str
    target_score: int
    bonus_score: int
    status: str
    approved_at: str | None = None
    completed_at: str | None = None
    deadline: str | None = None
    progress_score: int
    progress_ratio: float
    created_at: str

    class Config:
        from_attributes = True


# -------- 惊喜奖励券 --------
class SurpriseTicketCreate(BaseModel):
    name: str
    description: str = ""
    cost: int = 10
    icon: str | None = None


class SurpriseTicketUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cost: int | None = None
    icon: str | None = None
    enabled: bool | None = None


# -------- 亲子任务商店 --------
class ShopTaskCreate(BaseModel):
    title: str
    description: str = ""
    reward: int = 10
    icon: str = "shop_challenge"


class ShopTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    reward: int | None = None
    icon: str | None = None
    enabled: bool | None = None