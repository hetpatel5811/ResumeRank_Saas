from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_URL: str = "http://localhost:5173"

    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None
    RAZORPAY_WEBHOOK_SECRET: str | None = None
    RAZORPAY_PLUS_PLAN_ID: str | None = None
    RAZORPAY_PRO_PLAN_ID: str | None = None

    OPENAI_API_KEY: str | None = None
    OPENAI_SUPPORT_MODEL: str = "gpt-5-mini"

    class Config:
        env_file = ".env"


settings = Settings()
