"""FastAPI surface for the dashboard. The proxy itself lives in proxy.py."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from customs import __version__, store
from customs.config import settings
from customs.models import QuarantineEntry, ServerRecord

_ROOT = Path(__file__).resolve().parents[1]
_LANDING_INDEX = _ROOT / "landing" / "static" / "index.html"
_DASHBOARD_INDEX = _ROOT / "dashboard" / "static" / "index.html"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    store.init_db(settings.db_url)
    yield


app = FastAPI(title="Customs", version=__version__, lifespan=lifespan)


@app.get("/")
async def landing() -> FileResponse:
    return FileResponse(_LANDING_INDEX)


@app.get("/console")
async def dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD_INDEX)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/servers")
async def list_servers() -> list[ServerRecord]:
    return store.list_servers()


@app.get("/api/quarantine")
async def list_quarantine() -> list[QuarantineEntry]:
    return store.list_quarantine()


@app.get("/api/servers/{server_id}")
async def get_server(server_id: str) -> ServerRecord:
    record = store.get_server(server_id)
    if record is None:
        raise HTTPException(status_code=404, detail="server not found")
    return record
