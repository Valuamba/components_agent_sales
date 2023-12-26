from fastapi import FastAPI, Depends, Response, Request
from config import app_settings
from services import OpenAIClient, DetailInfoRepository, LoggingService, ClassifyEmailAgent 
from models import EmailRequest, DetailRequest

from opentelemetry import trace
from openai import OpenAI
import psycopg2

import uuid
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from fastapi.responses import JSONResponse

from typing import List

# Directory where log files will be stored
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

name = 'famaga'

# Logger configuration
logger = logging.getLogger(name)
logger.setLevel(logging.INFO)  # Set to DEBUG, INFO, WARNING, ERROR as needed

# Create a handler that writes log messages to a file, rotating at midnight.
handler = TimedRotatingFileHandler(
    os.path.join(log_directory, f"{name}.log"), 
    when="midnight", 
    interval=1, 
    backupCount=30  # Keep 7 days of logs; adjust as needed
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)



app = FastAPI()


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    response = await call_next(request)
    
    response.headers["X-Trace-ID"] = trace_id

    return response

def get_trace_id(request: Request):
    return request.state.trace_id


class RequestContext:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id


def get_openai_client():
    client = OpenAI(api_key = app_settings.openai_api_key)
    return OpenAIClient(client)


def get_db_connection():
    db_connection = psycopg2.connect(app_settings.famaga_db_url)
    db_connection.autocommit = True
    try:
        yield db_connection
    finally:
        db_connection.close()

def get_famaga_repository(db_connection=Depends(get_db_connection)):
    db_cursor = db_connection.cursor()
    try:
        repository = DetailInfoRepository(
            cursor=db_cursor,
            similarity_search_limit=app_settings.similarity_search_limit,
            vector_collection_name=app_settings.vector_collection_name
        )
        yield repository
    finally:
        db_cursor.close()


def get_request_context(trace_id: str = Depends(get_trace_id)) -> RequestContext:
    return RequestContext(trace_id)

def get_logger(context = Depends(get_request_context)):
    return LoggingService(
        context,
        name
    )

def get_classify_email_agent(
        openai_client = Depends(get_openai_client),
        logger = Depends(get_logger),
        repo = Depends(get_famaga_repository)
):
    return ClassifyEmailAgent(
        openai_client=openai_client,
        logger=logger,
        famaga_repo=repo
    )


@app.post("/price/",response_model=List[DetailRequest])
async def get_client_request_price(client_request: EmailRequest,
                             classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)):
    
        details, usage_cost_usd = await classify_email_agent.classify_client_response(client_request.body)

        details_dicts = [detail.model_dump() for detail in details]

        headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
        return JSONResponse(content=details_dicts, headers=headers)


@app.post("/detail/get_from_famaga_table")
def root(
    detail: DetailRequest,
    logger = Depends(get_logger), 
    classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)):

    presneted_db_details, usage_cost_usd = classify_email_agent.search_detail_at_db(detail)

    if len(presneted_db_details):
        logger.info('<b>Details at company table</b>\n\n' + '\n\n'.join([ 
                f"<b>ID</b>: {detail.id}\n" +
                f"<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Description:</b> {detail.description}"  
                                    for detail in presneted_db_details]))

    details_dicts = [detail.model_dump() for detail in presneted_db_details]

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=details_dicts, headers=headers)