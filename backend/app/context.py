from functools import lru_cache
from app.db.database import get_cosmos_database
from app.services.any_service import AnyService
from typing import AsyncGenerator


@lru_cache()
def get_services(cosmos_db):
    """Create singleton instances of services with injected dependencies"""
    return {
        
        "any_service": AnyService()
    }


async def get_service_context() -> AsyncGenerator[dict, None]:
    """Dependency that provides service instances"""
    cosmos_db = await get_cosmos_database()
    services = get_services(cosmos_db)
    yield services
