from fastapi import APIRouter
from .completion import completion_router
from api.v1.parts import parts_router

api_router = APIRouter()

router_v1 = APIRouter()
router_v1.include_router(parts_router, tags=["completion-v1"])

api_router.include_router(router_v1, prefix="/v1")
api_router.include_router(completion_router, tags=["parts"])


