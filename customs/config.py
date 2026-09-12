"""Runtime configuration, read once at startup."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_url: str = os.getenv("CUSTOMS_DB_URL", "sqlite:///customs.db")
    port: int = int(os.getenv("CUSTOMS_PORT", "8787"))
    fail_mode: str = os.getenv("CUSTOMS_FAIL_MODE", "closed")


settings = Settings()
