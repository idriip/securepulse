from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.routes import health, cves
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SecurePulse starting up...")
    yield
    logger.info("SecurePulse shutting down...")


app = FastAPI(
    title="SecurePulse",
    description="A DevSecOps-hardened CVE vulnerability feed API powered by the NVD.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cves.router)
Instrumentator().instrument(app).expose(app)