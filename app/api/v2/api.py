from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.actions.classify_contacts import ClassifyContactsAction
from core.actions.classify_intents import ClassifyIntentsAction
from core.bot import TelegramBotClient
from core.dispatcher import Task, dispatch
from core.models.action import Action
from database import get_db
from dependencies import get_run_repository, get_deal_repository, get_openai_client, get_task_repository, get_logger, \
    get_telegram_bot_client
from models.deal import LLMRun, StatusType, Deal, TaskFeedback
from repositories import DealRepository, TaskRepository
from repositories.run_repository import RunRepository
from services import OpenAIClient, LoggingService
from utils.html_messages_parser import get_messages_from_html_file, split_email_html_on_messages
from utils.sign import remove_sign_from_message

v2_group = APIRouter()


class ClassifyMessageIntentsDto(BaseModel):
    deal_id: str
    messages_html: str


class RunDetails(BaseModel):
    run_id: int


class Run(BaseModel):
    actions: List[Action]
    run: RunDetails | None = None
    tasks: List[Task]


class RunFeedbackCreate(BaseModel):
    run_id: Optional[int] = None
    feedback: Optional[str] = None
    is_like: int = 0
    issues: List[int] = []

    class Config:
        orm_mode = True

@v2_group.post("/run/feedback/")
def create_task_feedback(run_feedback: RunFeedbackCreate, db: Session = Depends(get_db)):
    task_feedback_obj = TaskFeedback(
        run_id=run_feedback.run_id,
        feedback=run_feedback.feedback,
        is_like=run_feedback.is_like
    )
    db.add(task_feedback_obj)
    db.commit()
    db.refresh(task_feedback_obj)

    db.commit()

@v2_group.post("/agent/handle_messages/html")
def classify_intents(request: ClassifyMessageIntentsDto,
                     openai_client: OpenAIClient = Depends(get_openai_client),
                     logger: LoggingService = Depends(get_logger),
                     telegram_bot: TelegramBotClient = Depends(get_telegram_bot_client),
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

    classify_intents_action = ClassifyIntentsAction(openai_client, task_repository, telegram_bot, logger)
    classify_contacts = ClassifyContactsAction(openai_client, task_repository, telegram_bot, logger)

    contact_details = classify_contacts.classify_contacts_details(run.run_id, message)

    if contact_details.action.action_status == StatusType.Passed.value and contact_details.data.sign:
        message = remove_sign_from_message(contact_details.data.sign, message)

    intents = classify_intents_action.classify_intents(run.run_id, message)

    tasks = dispatch(contact_details.data, intents.data)

    run_data = Run(
        actions=[
            contact_details,
            intents,
        ],
        run=RunDetails(run_id=run.run_id),
        tasks=tasks
    )

    return run_data

