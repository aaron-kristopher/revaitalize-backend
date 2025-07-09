from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
