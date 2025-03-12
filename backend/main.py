from dotenv import load_dotenv
import os
import logging
from app.context import get_service_context
from fastapi import Depends

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from contextlib import asynccontextmanager
from app.api import chat
from cache_manager import CacheManager
from app.services.any_service import AnyService

# global cache manager for repeat queries
cache_manager = CacheManager()
anyservice = AnyService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")

    yield

    logger.info("Application is shutting down...")


# initialize app with the lifespan
app = FastAPI(
    title="AI Assistant API",
    description="Backend API for AI Assistant ",
    version="1.0.0",
    lifespan=lifespan,
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(chat.router, prefix="/api/chat")



@app.get("/")
async def root():
    return {"message": "Welcome to Stevens AI Assistant API"}

@app.get("/test")
async def test_endpoint():
    return {"status": "ok"}





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
