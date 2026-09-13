# apps/api/app/core/config.py

from decimal import Decimal
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    APP_NAME: str = Field(default="VendorComply AI Engine")
    PARENT_COMPANY: str = Field(default="asiverticals.me")

    # Allowed CORS Origins & Dynamic Regex
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "https://vendorcomply.asiverticals.me",
            "https://vendorcomply.pages.dev",
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    )
    CORS_ORIGIN_REGEX: str = Field(
        default=r"^https:\/\/([a-zA-Z0-9_-]+\.)*(asiverticals\.me|pages\.dev)$|^http:\/\/localhost(:\d+)?$"
    )

    # Statutory Default Values
    # Section 115BAA corporate tax rate (22% base + 10% surcharge + 4% cess = 25.168%)
    DEFAULT_CORPORATE_TAX_RATE: Decimal = Field(default=Decimal("0.25168"))
    
    # Default GST Rate for ITC disallowance extraction
    DEFAULT_GST_RATE_PERCENT: Decimal = Field(default=Decimal("18.0"))
    
    # RBI Bank Rate (Current baseline: 6.50% p.a.; Section 16 Penal Rate = 3x = 19.50% p.a.)
    CURRENT_RBI_BANK_RATE: Decimal = Field(default=Decimal("0.0650"))

    # Database & Supabase Settings (safe fallback defaults to prevent startup crash)
    DATABASE_URL: str = Field(default="")
    DIRECT_DATABASE_URL: str = Field(default="")
    SUPABASE_URL: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="")
    SUPABASE_JWT_SECRET: str = Field(default="")

    # Groq Cloud OCR Engine Settings
    GROQ_API_KEY: str = Field(default="")
    USE_LOCAL_VLM: bool = Field(default=False)

    # On-Premise Agent Security Salt
    AGENT_HMAC_MASTER_KEY: str = Field(
        default="dev-insecure-hmac-key-replace-in-prod-64chars"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
