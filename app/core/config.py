from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener API"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = "redis://redis_cache:6379"

    class Config:
        env_file = ".env"

settings = Settings()
