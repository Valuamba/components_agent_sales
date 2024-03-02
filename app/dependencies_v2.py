from dependency_injector import containers, providers
from fastapi import Depends
from sqlalchemy.orm import Session

from configs import config
from database import get_db
from repositories import (
    EmbeddingRepository, DetailInfoRepository, DealRepository,
    MessageRepository, PartInquiryRepository, TaskRepository
)
from services import LoggingService, ClassifyEmailAgent, GoogleSearch, OpenAIClient
from agents.classify_parts.service import ClassifyEmailAgent as ClassifyEmailAgentV1
from fastapi import Depends, Request

from openai import OpenAI
import psycopg2


class RequestContext:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id


def get_trace_id(request: Request):
    return request.state.trace_id


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])  # Adjust this as per your application structure

    app_settings = providers.Configuration()

    openai_client = providers.Singleton(OpenAIClient, client=OpenAI(api_key=app_settings.openai_api_key))

    db_connection = providers.Resource(
        psycopg2.connect,
        dsn=app_settings.famaga_db_url,
        on_get=lambda db_connection: db_connection.autocommit(True),
        on_release=lambda db_connection: db_connection.close()
    )

    db = providers.Resource(get_db, db_url=app_settings.famaga_db_url)

    request_context = providers.Factory(
        RequestContext,
        trace_id=Depends(get_trace_id)  # Ensure to adjust the usage of Depends here as required
    )

    logger = providers.Factory(
        LoggingService,
        context=request_context
    )

    google_search = providers.Factory(
        GoogleSearch,
        logger=logger,
        api_key=app_settings.serper_api_key
    )

    detail_info_repository = providers.Factory(
        DetailInfoRepository,
        session_factory=db.provided.session
    )

    embedding_repository = providers.Factory(
        EmbeddingRepository,
        session_factory=db.provided.session,
        similarity_search_limit=app_settings.similarity_search_limit,
        vector_collection_name=app_settings.vector_collection_name
    )

    # Define additional repositories and services in a similar manner
    # ...

    classify_email_agent_v1 = providers.Factory(
        ClassifyEmailAgentV1,
        openai_client=openai_client,
        logger=logger,
        detail_info_repository=detail_info_repository,
        # Include additional dependencies as required
        # ...
    )

    classify_email_agent = providers.Factory(
        ClassifyEmailAgent,
        openai_client=openai_client,
        logger=logger,
        detail_info_repository=detail_info_repository,
        embeddings_repository=embedding_repository
        # Include additional dependencies as required
        # ...
    )

    # Define other services and their dependencies in a similar manner
