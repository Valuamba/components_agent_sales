from fastapi import FastAPI, Depends
from config import app_settings
from services import DetailInfoRepository, LoggerService, ClassifyEmailAgent 
from models import EmailRequest

from opentelemetry import trace
from openai import OpenAI
import psycopg2


app = FastAPI()


def get_openai_client():
    return OpenAI(api_key = app_settings.openai_api_key)


class RequestContext:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id


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


def get_request_context() -> RequestContext:
    current_span = trace.get_current_span()
    context = current_span.get_span_context()
    trace_id = format(context.trace_id, "032x")
    return RequestContext(trace_id)

def get_logger(context = Depends(get_request_context)):
    return LoggerService(
        context
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



@app.post("/price/")
async def get_client_request_price(client_request: EmailRequest,
                             classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)):
    
        details = await classify_email_agent.classify_client_response(client_request.body)

        return {
            "count": len(details)
        }




@app.get("/")
async def root(famaga_repo: DetailInfoRepository = Depends(get_famaga_repository)):

    details = famaga_repo.select_detail_by_part_number('snM-98-1E8')

    return {
        "message": "Hello World",
        "key": app_settings.openai_api_key,
        "count": len(details)
    }