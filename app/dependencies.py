from typing import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from configs import config
from database import get_db
from repositories import EmbeddingRepository, DetailInfoRepository
from repositories.deal_repository import DealRepository
from repositories.message import MessageRepository
from repositories.part_inquiry import PartInquiryRepository
from repositories.task import TaskRepository
from services import LoggingService, ClassifyEmailAgent, GoogleSearch, OpenAIClient
from agents.classify_parts.agent import ClassifyEmailAgent as ClassifyEmailAgentV1

from openai import OpenAI
import psycopg2

from configs.config import app_settings


class RequestContext:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id


def get_trace_id(request: Request):
    # Assuming the trace_id is somehow set on the request state
    return request.state.trace_id


def get_openai_client():
    # Make sure to securely manage your API key, e.g., using environment variables or a configuration file
    client = OpenAI(api_key=app_settings.openai_api_key)
    return OpenAIClient(client)


def get_db_connection():
    # Ensure that your database URL is securely managed
    db_connection = psycopg2.connect(app_settings.famaga_db_url)
    db_connection.autocommit = True
    try:
        yield db_connection
    finally:
        db_connection.close()

def get_request_context(trace_id: str = Depends(get_trace_id)) -> RequestContext:
    return RequestContext(trace_id)


def get_logger(context: RequestContext = Depends(get_request_context), name: str = "default_logger_name"):
    # Assuming LoggingService is a custom class for handling logging with context support
    return LoggingService(context, name)

def get_google_search(logger=Depends(get_logger)):
    # Assuming GoogleSearch is a custom class for handling Google searches
    return GoogleSearch(logger, app_settings.serper_api_key)


def get_details_info_repository(db: Session = Depends(get_db)) -> Generator[DetailInfoRepository, None, None]:
    repository = DetailInfoRepository(session=db)
    try:
        yield repository
    finally:
        pass

def get_embedding_repository(db: Session = Depends(get_db)) -> Generator[EmbeddingRepository, None, None]:
    repository = EmbeddingRepository(
        session=db,
        similarity_search_limit=app_settings.similarity_search_limit,
        vector_collection_name=app_settings.vector_collection_name
    )
    try:
        yield repository
    finally:
        pass


def get_deal_repository():
    repository = DealRepository(config.app_settings.famaga_db_url)
    try:
        yield repository
    finally:
        pass

def get_message_repository():
    repository = MessageRepository(config.app_settings.famaga_db_url)
    try:
        yield repository
    finally:
        pass

def get_part_inquiry_repository():
    repository = PartInquiryRepository(config.app_settings.famaga_db_url)
    try:
        yield repository
    finally:
        pass

def get_task_repository():
    repository = TaskRepository(config.app_settings.famaga_db_url)
    try:
        yield repository
    finally:
        pass


def get_classify_email_agent_v1(
        openai_client=Depends(get_openai_client),
        logger=Depends(get_logger),
        details_info_repository: DetailInfoRepository = Depends(get_details_info_repository),
        deal_repository = Depends(get_deal_repository),
        task_repository: TaskRepository = Depends(get_task_repository),
        part_inquiry_repository = Depends(get_part_inquiry_repository),
        message_repository: MessageRepository = Depends(get_message_repository),
        embedding_repository: EmbeddingRepository = Depends(get_embedding_repository)
):
    return ClassifyEmailAgentV1(
        openai_client=openai_client,
        logger=logger,
        detail_info_repository=details_info_repository,
        deal_repository=deal_repository,
        task_repository=task_repository,
        part_inquiry_repository=part_inquiry_repository,
        message_repository=message_repository,
        embeddings_repository=embedding_repository
    )


def get_classify_email_agent(
        openai_client=Depends(get_openai_client),
        logger=Depends(get_logger),
        details_info_repository: DetailInfoRepository = Depends(get_details_info_repository),
        embedding_repository: EmbeddingRepository = Depends(get_embedding_repository)
):
    return ClassifyEmailAgent(
        openai_client=openai_client,
        logger=logger,
        detail_info_repository=details_info_repository,
        embeddings_repository=embedding_repository
    )