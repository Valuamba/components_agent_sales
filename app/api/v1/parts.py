from typing import List

from fastapi import Depends, APIRouter, HTTPException

from agents.classify_parts.agent import ClassifyEmailAgent
from dependencies import get_classify_email_agent_v1, get_deal_repository, get_part_inquiry_repository, \
    get_task_repository, get_message_repository
from repositories.message import MessageRepository
from repositories.task import TaskRepository
from schemas.completion import DetailRequest
from fastapi.responses import JSONResponse

from schemas.v1.classify_part import ClassifyAgentResponse
from schemas.v1.part import ClassifyPartRequest

parts_router = APIRouter()


@parts_router.post("/request/classify", response_model=ClassifyAgentResponse)
async def get_client_request_price(client_request: ClassifyPartRequest,
                                   classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent_v1)
                                   ):
    """
    Поиск информации о деталях из сообщения клиента
    """
    order, usage_cost_usd = await classify_email_agent.classify_client_response(client_request)
    if not order:
        raise HTTPException(status_code=404, detail="Completion error")

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=order.model_dump(), headers=headers)
