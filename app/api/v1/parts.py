from typing import List

from fastapi import Depends, APIRouter

from agents.classify_parts.agent import ClassifyEmailAgent
from dependencies import get_classify_email_agent_v1, get_deal_repository, get_part_inquiry_repository, \
    get_task_repository, get_message_repository
from repositories.message import MessageRepository
from repositories.task import TaskRepository
from schemas.completion import DetailRequest
from schemas.v1.part import ClassifyPartRequest
from fastapi.responses import JSONResponse


parts_router = APIRouter()


@parts_router.post("/request/classify", response_model=List[DetailRequest])
async def get_client_request_price(client_request: ClassifyPartRequest,
                                   classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent_v1)
                                   ):
    order, usage_cost_usd = await classify_email_agent.classify_client_response(client_request)

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=order.model_dump(), headers=headers)
