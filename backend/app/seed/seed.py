"""预置数据：家长配置、孩子、任务规则、等级、成就、奖励"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.config import settings
from app.models import (
    Achievement,
    Child,
    LevelConfig,
    ParentConfig,
    Reward,
    TaskRule,
)

# (名称, 类型, 分值, 图标, 说明, 是否可打卡)
# —— 现行积分规则（Excel 导入）
PRESET_TASKS = [
    # 2分项
    ("做家务", "家务", 2, "task_clean.png", "选择至少一种家务，时间不低于10分钟", False),
    ("举手回答问题", "学习", 2, "task_homework.png", "当日举手回答问题，每一次+1分", False),
    ("刷牙叠被子", "习惯", 2, "task_early.png", "刷牙、叠被子好习惯养成", True),
    # 3分项
    ("被老师表扬", "品德", 3, "task_honest.png", "被老师表扬，每一次+3分", False),
    ("当日作业全对", "学习", 3, "task_homework.png", "当日作业全对", True),
    ("书写整齐", "学习", 3, "task_review.png", "书写整齐，姿势正确", False),
    ("超前完成任务", "学习", 3, "task_read.png", "安排表当日任务超前完成", False),
    ("房间整洁", "家务", 3, "task_clean.png", "房间内整洁，包括书桌", True),
    ("语文举手回答", "学习", 3, "task_homework.png", "语文举手回答问题", False),
    # 5分项
    ("体重达标", "习惯", 5, "task_sport.png", "体重比最低时降低，一天最多加一次分", False),
    ("优秀作文", "学习", 5, "task_read.png", "一篇优秀作文，老师或者爸爸妈妈批改都可以", False),
    ("游泳", "习惯", 5, "task_sport.png", "游泳10圈", False),
    ("跳绳", "习惯", 5, "task_sport.png", "跳绳1000个", True),
    # 20分项
    ("考试满分", "学习", 20, "task_homework.png", "考试满分", False),
    # 10分项（存积分50满一月，家长手动加分）
    ("存积分满月奖励", "理财", 10, "task_generic.png", "存积分50满一月 +10分", False),
]

PRES_LEVELS = [
    (1, "成长新人", "level_1.png", "踏上冒险之路的第一步", 0),
    (2, "森林探索者", "level_2.png", "探索未知森林，勇敢出发", 50),
    (3, "矿洞学徒", "level_3.png", "深入矿洞，挖掘魔法宝石", 120),
    (4, "铁匠大师", "level_4.png", "锻造装备，成为铁匠大师", 220),
    (5, "魔法师", "level_5.png", "掌握魔法，守护家园", 360),
    (6, "远古守护者", "level_6.png", "远古力量的继承者", 550),
]

# 成就预置数据
# (code, 名称, 描述, 类别, 段位阈值列表, 图标)
PRES_ACHIEVEMENTS = [
    # 学习
    ("study_streak", "学习达人", "连续完成学习任务，坚持不懈", "study", [3, 7, 15, 30], "ach_study.png"),
    ("homework_master", "作业小能手", "累计完成作业，温故知新", "study", [5, 15, 30, 50], "ach_homework.png"),
    ("reading_star", "阅读之星", "坚持阅读，遨游书海", "study", [10, 30, 60, 100], "ach_read.png"),
    # 家务
    ("clean_expert", "整理专家", "整理房间，井井有条", "chore", [5, 15, 30, 50], "ach_clean.png"),
    ("helper", "家务小帮手", "主动帮家人做家务", "chore", [5, 15, 30, 50], "ach_helper.png"),
    # 习惯
    ("early_bird", "早起鸟", "坚持早起，迎接清晨", "habit", [10, 30, 60, 100], "ach_early.png"),
    ("sleep_master", "睡眠卫士", "按时睡觉，养精蓄锐", "habit", [10, 30, 60, 100], "ach_sleep.png"),
    ("early_bird_streak", "早起连胜", "连续早起，毅力可嘉", "habit", [3, 7, 15, 30], "ach_early_streak.png"),
    # 积分
    ("first_score", "首次得分", "获得第一颗魔法宝石", "score", [1], "ach_first.png"),
    ("score_master", "积分大师", "累计获得大量魔法宝石", "score", [50, 100, 200, 500], "ach_score.png"),
    # 兑换
    ("first_exchange", "交易新人", "首次兑换奖励", "exchange", [1], "ach_trade.png"),
    ("exchange_master", "兑换专家", "累计完成多次兑换", "exchange", [3, 10, 20, 50], "ach_exchange.png"),
    # 挑战
    ("challenge_taker", "挑战先锋", "勇敢接下挑战任务", "challenge", [1, 5, 10, 20], "ach_challenge_take.png"),
    ("challenge_master", "挑战大师", "成功完成挑战任务", "challenge", [1, 5, 10, 20], "ach_challenge.png"),
    # 打卡
    ("checkin_streak", "打卡达人", "坚持每日打卡", "checkin", [3, 7, 15, 30], "ach_checkin_streak.png"),
    ("checkin_total", "打卡劳模", "累计打卡次数", "checkin", [10, 30, 60, 100], "ach_checkin.png"),
    # 目标
    ("goal_setter", "目标设定者", "设定自己的成长目标", "goal", [1, 3, 5, 10], "ach_goal_set.png"),
    ("goal_achiever", "目标达成者", "达成自己设定的目标", "goal", [1, 3, 5, 10], "ach_goal.png"),
    # 银行
    ("saver", "储蓄达人", "把宝石存进银行", "bank", [1, 5, 10, 20], "ach_saver.png"),
    ("wealth_master", "财富大师", "银行存有大量宝石", "bank", [10, 30, 50, 100], "ach_wealth.png"),
]

PRES_REWARDS = [
    ("看电视", "看电视或手机，1分兑换1分钟，每次不超过20分钟", 20, "reward_tv.png", False),
    ("兑换现金", "5分兑换1元钱，单次无上限（按元计）", 5, "reward_toy.png", False),
]


def seed_data(db: Session):
    """初始化数据库预置数据（幂等）"""
    # ========== 数据库迁移（增量加列，必须在查询前执行） ==========
    _migrate_db(db)

    # 家长配置
    if db.query(ParentConfig).count() == 0:
        db.add(
            ParentConfig(
                password_hash=hash_password(settings.default_parent_password),
                child_password_hash=hash_password(
                    settings.default_child_password
                ),
            )
        )
    else:
        # 已有配置：若孩子口令未设置则补默认
        config = db.query(ParentConfig).first()
        if not config.child_password_hash:
            config.child_password_hash = hash_password(
                settings.default_child_password
            )
            db.commit()

    # 孩子
    if db.query(Child).count() == 0:
        db.add(
            Child(
                name=settings.default_child_name,
                avatar=settings.default_child_avatar,
                slot=0,
            )
        )
        db.flush()

    child = db.query(Child).filter(Child.slot == 0).first()

    # 任务规则：清空旧的预置任务，按现行规则重建（保留用户自建规则）
    _rebuild_preset_tasks(db)

    # 等级
    if db.query(LevelConfig).count() == 0:
        for lv, name, icon, desc, min_score in PRES_LEVELS:
            db.add(
                LevelConfig(
                    level=lv,
                    name=name,
                    icon=icon,
                    description=desc,
                    min_score=min_score,
                )
            )

    # 成就：检测是否缺少新版成就（缺少 category 字段的旧数据则清空重播种）
    existing = db.query(Achievement).filter(Achievement.child_id == child.id).all()
    if not existing:
        _seed_achievements(db, child.id)
    else:
        # 若存在旧版无 category 的成就，或数量与预置不符，重建为新版20个
        needs_rebuild = any(getattr(a, "category", None) is None for a in existing)
        if needs_rebuild or len(existing) != len(PRES_ACHIEVEMENTS):
            for a in existing:
                db.delete(a)
            db.flush()
            _seed_achievements(db, child.id)

    # 奖励：清空旧的预置奖励，按现行兑换规则重建（保留用户自建）
    _rebuild_preset_rewards(db)

    db.commit()


def _rebuild_preset_tasks(db: Session):
    """清空旧的预置任务，按现行规则重建（保留用户自建任务 is_preset=False）"""
    db.query(TaskRule).filter(TaskRule.is_preset == True).delete()
    db.flush()
    for i, (name, typ, val, icon, desc, is_checkin) in enumerate(PRESET_TASKS):
        db.add(
            TaskRule(
                name=name,
                task_type=typ,
                score_value=val,
                icon=icon,
                sort_order=i,
                description=desc,
                is_preset=True,
                is_checkin=is_checkin,
            )
        )
    db.flush()


def _rebuild_preset_rewards(db: Session):
    """清空奖励，按现行兑换规则重建"""
    db.query(Reward).delete()
    db.flush()
    for i, (name, desc, cost, icon, is_wish) in enumerate(PRES_REWARDS):
        db.add(
            Reward(
                name=name,
                description=desc,
                cost=cost,
                icon=icon,
                sort_order=i,
                is_wish=is_wish,
            )
        )
    db.flush()


def _seed_achievements(db: Session, child_id: int):
    """播种成就（带 category 和 tier_thresholds）"""
    for code, name, desc, category, thresholds, icon in PRES_ACHIEVEMENTS:
        target_value = thresholds[-1] if thresholds else 1
        rarity = "common"
        if len(thresholds) >= 4:
            rarity = "legendary"
        elif len(thresholds) == 3:
            rarity = "epic"
        elif len(thresholds) == 2:
            rarity = "rare"
        db.add(
            Achievement(
                child_id=child_id,
                code=code,
                name=name,
                description=desc,
                icon=icon,
                category=category,
                rarity=rarity,
                current_tier=0,
                tier_thresholds=str(thresholds),
                target_value=target_value,
            )
        )


def _migrate_db(db: Session):
    """为已有数据库增量添加新列（SQLite 不支持 ALTER TABLE ADD COLUMN with default 的某些场景）"""
    # task_rule 表增加 is_checkin 列
    try:
        db.execute(text("SELECT is_checkin FROM task_rule LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE task_rule ADD COLUMN is_checkin BOOLEAN DEFAULT 0"))
        db.commit()
        # 给已有的正向任务默认标记可打卡
        db.execute(text(
            "UPDATE task_rule SET is_checkin = 1 WHERE score_value > 0 AND is_checkin IS NULL"
        ))
        db.commit()

    # achievement 表增加 category 列
    try:
        db.execute(text("SELECT category FROM achievement LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE achievement ADD COLUMN category VARCHAR(20) DEFAULT 'score'"))
        db.commit()

    # achievement 表增加 current_tier 列
    try:
        db.execute(text("SELECT current_tier FROM achievement LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE achievement ADD COLUMN current_tier INTEGER DEFAULT 0"))
        db.commit()

    # achievement 表增加 tier_thresholds 列
    try:
        db.execute(text("SELECT tier_thresholds FROM achievement LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE achievement ADD COLUMN tier_thresholds VARCHAR(100) DEFAULT '[1]'"))
        db.commit()

    # parent_config 表增加 child_password_hash 列
    try:
        db.execute(text("SELECT child_password_hash FROM parent_config LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE parent_config ADD COLUMN child_password_hash VARCHAR(255)"))
        db.commit()

    # parent_config 表增加 bank_interest_rate 列
    try:
        db.execute(text("SELECT bank_interest_rate FROM parent_config LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE parent_config ADD COLUMN bank_interest_rate INTEGER DEFAULT 2"))
        db.commit()

    # parent_config 表增加 last_interest_date 列
    try:
        db.execute(text("SELECT last_interest_date FROM parent_config LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE parent_config ADD COLUMN last_interest_date VARCHAR(20)"))
        db.commit()

    # daily_checkin 表增加 status 列
    try:
        db.execute(text("SELECT status FROM daily_checkin LIMIT 1"))
    except Exception:
        db.execute(text("ALTER TABLE daily_checkin ADD COLUMN status VARCHAR(20) DEFAULT 'confirmed'"))
        db.commit()