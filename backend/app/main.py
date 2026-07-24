from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.models import Base
from app.db.session import engine
from app.config import get_settings
from app.routers import audit, dashboard, inventory, matches, recalls


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="RecallRadar AI API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recalls.router)
app.include_router(inventory.router)
app.include_router(matches.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
