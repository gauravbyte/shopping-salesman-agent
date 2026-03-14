from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./shop.db"

    # Pine Labs / PinePG
    PINE_LABS_BASE_URL: str = "https://pluraluat.v2.pinepg.in/api"
    PINE_LABS_MID: str = ""
    PINE_LABS_CLIENT_ID: str = ""
    PINE_LABS_CLIENT_SECRET: str = ""
    # Where Pine Labs POSTs the payment result (our backend endpoint)
    PINE_LABS_RETURN_URL: str = "http://localhost:8001/payments/return"
    # Frontend base URL — used to redirect customer after payment
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
