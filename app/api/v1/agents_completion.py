from fastapi import APIRouter, Depends

from agents.pricing_manager.agent import PricingManagerAgent
from dependencies import get_pricing_manager
from schemas.v1.agents_completion import AgentCompletionRequest

agents_router = APIRouter()


@agents_router.post("/agent/completion/create")
def create_agent_completion(request: AgentCompletionRequest,
                            pricing_manager: PricingManagerAgent = Depends(get_pricing_manager)):

    return pricing_manager.classify_messages_metadata_and_intents(request.deal_id, request.deal_info)