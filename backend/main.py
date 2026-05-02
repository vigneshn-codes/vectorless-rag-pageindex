import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.init_db import init_db, close_db
from backend.api.routes import health, ingest, query, documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down — closing DB connections...")
    await close_db()


app = FastAPI(
    title="Vectorless RAG API",
    description="A production-ready RAG system using PostgreSQL FTS (no vector embeddings).",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])


@app.get("/")
async def root():
    return {"message": "Vectorless RAG API is running. Visit /docs for the API reference."}
