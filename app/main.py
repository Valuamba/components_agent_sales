from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import uuid

from api.router import api_router
from dependencies import get_logger


app = FastAPI()

origins = [
    "https://famaga",
    "https://crmfamaga.prod",
    "https://famaga.org",
    "https://api.famaga.org",
    "http://localhost:3001",
    "http://famaga",
    "https://crm.haveamint.online",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id

    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id

    return response


@app.get("/health")
async def health_check(logger_service = Depends(get_logger)):
    logger_service.info("Health check endpoint was accessed", extra_info={'request_id': 'N/A', 'extra_info': 'Health check'})

    return {"status": "healthy"}

app.include_router(api_router)
