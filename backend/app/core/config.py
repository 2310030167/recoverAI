from typing import Dict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RecoverySettings(BaseModel):
    """Centralized business, operational horizon, policy, and cost settings."""
    cooldown_hours: float = 24.0
    max_retry_attempts: int = 3
    max_interventions: int = 5
    macro_horizon_days: int = 30
    primary_window_days: int = 3
    secondary_window_days: int = 7
    escalation_amount_threshold: float = 100000.0
    escalation_days_overdue: int = 14
    min_expected_value: float = 0.0

    # Default action costs in INR
    action_costs: Dict[str, float] = Field(
        default_factory=lambda: {
            "NO_ACTION": 0.00,
            "REMINDER": 0.50,
            "RETRY": 2.00,
            "ESCALATE": 50.00,
        }
    )

    # Action-conditioned multiplier bounds (Simulation assumptions)
    action_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {
            "NO_ACTION": 1.00,
            "REMINDER": 1.20,
            "RETRY": 1.35,
            "ESCALATE": 1.15,
        }
    )


class ExecutionSettings(BaseModel):
    """Centralized provider & infrastructure configuration."""
    provider_timeout_ms: int = 3000
    default_provider: str = "TEST_MODE"
    RAZORPAY_PROVIDER_TYPE: str = "TEST_MODE"
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""


class Settings(BaseSettings):
    """
    Application settings powered by Pydantic v2 BaseSettings.
    Reads environment variables from system or .env file.
    """
    APP_NAME: str = "RecoverAI"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/recoverai_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/recoverai_db"

    # Redis Cache Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # Centralized Recovery & Execution Settings
    recovery: RecoverySettings = Field(default_factory=RecoverySettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )


settings = Settings()
