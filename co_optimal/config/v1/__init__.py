import os

from pydantic_settings import BaseSettings


class BaseSettingsWrapper(BaseSettings):
    class Config:
        env_file = "co_optimal/.env" if os.path.exists("co_optimal/.env") else ".env"
        case_sensitive = True
        extra = "allow"
