from fastapi import APIRouter
from .completion import completion_router
from api.v1.parts import parts_router
from .v1.agents_completion import agents_router
from .v1.messages import messages_router
from .v2.api import v2_group
from .v2.discount import discount, discount_v3

api_router = APIRouter()

router_v1 = APIRouter()
router_v1.include_router(parts_router, tags=["completion-v1"])
router_v1.include_router(messages_router, tags=["completion-v1"])
router_v1.include_router(agents_router, tags=["completion-v1"])
api_router.include_router(router_v1, prefix="/v1")
api_router.include_router(v2_group, prefix="/v2", tags=['v2'])
api_router.include_router(discount, prefix="/v2", tags=['v2'])
api_router.include_router(discount_v3, prefix="/v3", tags=['v3'])


api_router.include_router(completion_router, tags=["parts"])


