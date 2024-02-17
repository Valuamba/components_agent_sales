from typing import List

from fastapi import Depends, APIRouter, HTTPException
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session

from agents.classify_parts.agent import ClassifyEmailAgent
from database import get_db
from dependencies import get_classify_email_agent_v1, get_deal_repository, get_part_inquiry_repository, \
    get_task_repository, get_message_repository
from repositories.message import MessageRepository
from repositories.task import TaskRepository
from schemas.completion import DetailRequest
from fastapi.responses import JSONResponse

from models.deal import Issue, TaskFeedback, IssueGroup

from schemas.v1.classify_part import ClassifyAgentResponse
from schemas.v1.part import ClassifyPartRequest, TaskFeedbackCreate
from schemas.v1.part import IssueModel

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
