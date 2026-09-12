# apps/agent/src/config.py

import os
import json
from pathlib import Path
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    tally_host: str = Field(default="http://127.0.0.1")
    tally_port: int = Field(default=9000)
    tally_company_name: str = Field(description="Exact Company Name open in Tally Prime")
    cloud_sync_url: str = Field(default="https://vendorcomply.asiverticals.me/api/v1/sync/push")
    tenant_id: str = Field(description="Tenant UUID issued by asiverticals.me")
    agent_secret_key: str = Field(description="64-character hex secret for HMAC signing")
    sync_interval_seconds: int = Field(default=3600)
    local_db_path: str = Field(default="tally_cache.db")
    historical_days_back: int = Field(default=365)

    @classmethod
    def load_from_file(cls, config_path: str = "agent_config.json") -> "AgentConfig":
        path = Path(config_path)
        if not path.exists():
            default_config = cls(
                tally_company_name="Enter Your Tally Company Name",
                tenant_id="00000000-0000-0000-0000-000000000000",
                agent_secret_key="0" * 64
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(default_config.model_dump_json(indent=2))
            raise FileNotFoundError(
                f"Configuration template generated at '{config_path}'. Populate your tenant credentials."
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return cls(**data)
