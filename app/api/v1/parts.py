import json
from email import message_from_bytes
from typing import List, Dict, Any

from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from fastapi.openapi.models import Response
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from agents.classify_intents.agent import ClassifyIntentsAgent
from agents.classify_parts.service import ClassifyEmailAgent
from database import get_db
from dependencies import get_classify_email_agent_v1, get_deal_repository, get_part_inquiry_repository, \
    get_task_repository, get_message_repository, get_logger, get_classify_intents_agent, get_intent_repository
from repositories.intents import IntentRepository
from repositories.message import MessageRepository
from repositories.task import TaskRepository
from schemas.completion import DetailRequest
from fastapi.responses import JSONResponse

from models.deal import Issue, TaskFeedback, IssueGroup, Deal, Message, FromType

from schemas.v1.classify_part import ClassifyAgentResponse
from schemas.v1.email_parser import EmailContent
from schemas.v1.part import ClassifyPartRequest, TaskFeedbackCreate
from schemas.v1.part import IssueModel
from services import LoggingService
from utility import extract_html_from_eml, extract_messages_from_body, content_hash, extract_messages_from_raw_html

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


@parts_router.get("/issues/{group_name}", response_model=List[IssueModel])
def get_issues_by_group_name(group_name: str, db: Session = Depends(get_db)):
    issue_group = db.query(IssueGroup).filter(IssueGroup.name == group_name).first()
    if not issue_group:
        raise HTTPException(status_code=404, detail="Issue group not found")
    return issue_group.issues


@parts_router.post("/task_feedback/")
def create_task_feedback(task_feedback: TaskFeedbackCreate, db: Session = Depends(get_db)):
    task_feedback_obj = TaskFeedback(
        task_id=task_feedback.task_id,
        feedback=task_feedback.feedback,
        is_like=task_feedback.is_like
    )
    db.add(task_feedback_obj)
    db.commit()
    db.refresh(task_feedback_obj)

    # Associate issues with the new TaskFeedback
    for issue_id in task_feedback.issues:
        issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
        if not issue:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Issue with ID {issue_id} not found")
        task_feedback_obj.issues.append(issue)
    db.commit()


@parts_router.post("/upload-eml/")
async def upload_eml_file(deal_id: int, file: UploadFile = File(...),
                          intent_repository: IntentRepository = Depends(get_intent_repository),
                          deal_repository = Depends(get_deal_repository),
                          message_repository = Depends(get_message_repository),
                          logger_service: LoggingService = Depends(get_logger),
                          classify_intents_agent: ClassifyIntentsAgent = Depends(get_classify_intents_agent),
                          session = Depends(get_db)):
    if not file.filename.endswith(".eml"):
        return JSONResponse(status_code=400, content={"message": "File is not an .eml file"})

    contents = await file.read()
    html_content = extract_html_from_eml(contents)
    messages = extract_messages_from_body(html_content)
    messages = [msg for msg in messages if msg and not msg.isspace()]
    message = message_from_bytes(contents)

    existing_messages = session.query(Message).filter_by(deal_id=deal_id).order_by(desc(Message.id)).all()

    existing_index = 0

    new_messages = []
    for eml_message in messages:
        if existing_index >= len(existing_messages) or content_hash(eml_message) != existing_messages[existing_index].hash:
            if existing_index < len(existing_messages):
                raise ValueError("Message mismatch collision detected.")
            new_messages.append(eml_message)
        else:
            existing_index += 1

    logger_service.info(f'There are [{len(new_messages)}] to be appended to messaging', {'deal_id': deal_id})
    if len(new_messages) == 0:
        return JSONResponse(status_code=200, content={"message": "All messages was added earlier."})

    deal = deal_repository.get_or_create_deal(deal_id, Deal(deal_id=deal_id, subject=message.get("Subject")))

    messages_with_intents = classify_intents_agent.classify_messages_metadata_and_intents(deal.deal_id, new_messages)

    if len(new_messages) != len(messages_with_intents):
        logger_service.error(f'Messages from *.eml file [{len(new_messages)}] and messages with intents [{len(messages_with_intents)}] do not match the length.')
        return JSONResponse(status_code=400, content={"message": "Error at parsing intents"})


    for raw_msg, msg in zip(new_messages[::-1], messages_with_intents[::-1]):
        # Хэш какого боди считать, того, что в письме или которе гпт вернул?
        # print(raw_msg)
        # print(f'\n\n---------\n\n{msg.body}')
        message_hash = content_hash(raw_msg)
        new_message = message_repository.append_message_to_deal(
            deal_id, Message(
                deal_id=deal_id,
                from_type=FromType.Manager.value if msg.from_ == 'manager' else FromType.Customer.value,
                body=msg.body,
                sign=msg.sign,
                hash=message_hash
            ))
        logger_service.info(f'Message [{new_message.message_id}] was appended to deal [{deal_id}] with serial number [{new_message.id}]')

        intent_repository.batch_insert_intents_from_models(msg.intents, new_message.message_id)

    return messages_with_intents


@parts_router.post("/upload-html/")
async def upload_eml_file(email_content: EmailContent,
                          intent_repository: IntentRepository = Depends(get_intent_repository),
                          deal_repository = Depends(get_deal_repository),
                          message_repository = Depends(get_message_repository),
                          logger_service: LoggingService = Depends(get_logger),
                          classify_intents_agent: ClassifyIntentsAgent = Depends(get_classify_intents_agent),
                          session = Depends(get_db)):
    deal_id = email_content.deal_id
    html_content = email_content.html_content
    subject = email_content.subject

    messages = extract_messages_from_raw_html(html_content)
    messages = [msg for msg in messages if msg and not msg.isspace()]
    logger_service.info(f'There are [{len(messages)}] total messages.', {'deal_id': deal_id})

    existing_messages = session.query(Message).filter_by(deal_id=deal_id).order_by(desc(Message.id)).all()

    existing_index = 0

    new_messages = []
    for eml_message in messages:
        if existing_index >= len(existing_messages) or content_hash(eml_message) != existing_messages[existing_index].hash:
            if existing_index < len(existing_messages):
                raise ValueError("Message mismatch collision detected.")
            new_messages.append(eml_message)
        else:
            existing_index += 1

    logger_service.info(f'There are [{len(new_messages)}] to be appended to messaging', {'deal_id': deal_id})
    if len(new_messages) == 0:
        return JSONResponse(status_code=200, content={"message": "All messages was added earlier."})

    deal = deal_repository.get_or_create_deal(deal_id, Deal(deal_id=deal_id, subject=subject))

    messages_with_intents = classify_intents_agent.classify_messages_metadata_and_intents(deal.deal_id, new_messages)

    if len(new_messages) != len(messages_with_intents):
        logger_service.error(f'Messages from *.eml file [{len(new_messages)}] and messages with intents [{len(messages_with_intents)}] do not match the length.')
        return JSONResponse(status_code=400, content={"message": "Error at parsing intents"})


    for raw_msg, msg in zip(new_messages[::-1], messages_with_intents[::-1]):
        message_hash = content_hash(raw_msg)
        new_message = message_repository.append_message_to_deal(
            deal_id, Message(
                deal_id=deal_id,
                from_type=FromType.Manager.value if msg.from_ == 'manager' else FromType.Customer.value,
                body=msg.body,
                sign=msg.sign,
                hash=message_hash
            ))
        logger_service.info(f'Message [{new_message.message_id}] was appended to deal [{deal_id}] with serial number [{new_message.id}]')

        intent_repository.batch_insert_intents_from_models(msg.intents, new_message.message_id)

    return messages_with_intents