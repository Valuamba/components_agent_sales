from fastapi import APIRouter, HTTPException, Depends

from dependencies import get_deal_repository
from repositories import DealRepository
from schemas.v1.messages import DealMessagesResponse, MessageModel, IntentModel

messages_router = APIRouter()


@messages_router.get("/deals/{deal_id}/messages", response_model=DealMessagesResponse)
def get_messages_with_intents(deal_id: int, deal_repository: DealRepository = Depends(get_deal_repository)):
    deal = deal_repository.get_deal_with_messages(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    messages = [
        MessageModel(
            uuid=msg.uuid,
            id=msg.id,
            body=msg.body,
            from_type=msg.from_type,
            intents=[
                IntentModel(
                    uuid=intent.uuid,
                    intent=intent.intent,
                    sub_intent=intent.sub_intent,
                    branch=intent.branch
                ) for intent in msg.intents
            ]
        ) for msg in deal.messages
    ]

    return DealMessagesResponse(deal_uuid=deal.uuid, messages=messages)
