from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
# from pydantic.v1 import BaseModel
from pydantic import BaseModel

from core.actions.classify_contacts import ClassifyContactsAction
from core.actions.classify_intents import ClassifyIntentsAction
from dependencies import get_run_repository, get_deal_repository, get_openai_client, get_task_repository, get_logger
from models.deal import LLMRun, StatusType, Deal
from repositories import DealRepository, TaskRepository
from repositories.run_repository import RunRepository
from services import OpenAIClient, LoggingService
from utils.html_messages_parser import get_messages_from_html_file, split_email_html_on_messages
from utils.sign import remove_sign_from_message

v2_group = APIRouter()


class ClassifyMessageIntentsDto(BaseModel):
    deal_id: str
    messages_html: str


@v2_group.post("/agent/handle_messages/html")
def classify_intents(request: ClassifyMessageIntentsDto,
                     openai_client: OpenAIClient = Depends(get_openai_client),
                     logger: LoggingService = Depends(get_logger),
                     task_repository: TaskRepository = Depends(get_task_repository),
                     run_repository: RunRepository = Depends(get_run_repository),
                     deal_repository: DealRepository = Depends(get_deal_repository)):
    messages = split_email_html_on_messages(request.messages_html)
    latest_message = messages[0]
    message = latest_message

    deal = deal_repository.get_or_create_deal(request.deal_id, Deal(deal_id=request.deal_id))

    run = run_repository.create_run(run=LLMRun(
        status=StatusType.InProgress.value,
        deal_id=deal.deal_id
    ))

    classify_intents_action = ClassifyIntentsAction(openai_client, task_repository)
    classify_contacts = ClassifyContactsAction(openai_client, task_repository, logger)

    contact_details = classify_contacts.classify_contacts_details(run.run_id, message)

    if contact_details.action.action_status == StatusType.Passed.value and contact_details.data.sign:
        message = remove_sign_from_message(contact_details.data.sign, message)

    intents = classify_intents_action.classify_intents(run.run_id, message)

    return {
        "run": {
            "actions": [
                contact_details.dict(),
                intents.dict()
            ],
            "run": {
                "run_id": run.run_id
            }
        }
    }

