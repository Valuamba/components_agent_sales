from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import configs.logger
import uuid

from api.router import api_router

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


app.include_router(api_router)
