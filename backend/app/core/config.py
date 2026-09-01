"""应用配置"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，可通过环境变量或 .env 覆盖"""

    app_name: str = "我的成长世界"
    database_url: str = "sqlite:///./data/growth_world.db"
    default_parent_password: str = "admin123"
    default_child_password: str = "admin123"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 小时
    cors_origins: str = "*"

    default_child_name: str = "小勇士"
    default_child_avatar: str = "miner_default.png"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()