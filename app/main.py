from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from api.router import api_router
from configs.config import app_settings
from dependencies import get_logger, get_telegram_bot_client, get_request_context, get_trace_id

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


class AddTraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a new trace ID and attach it to the request state
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id

        # Continue processing the request
        response = await call_next(request)

        # Add the trace ID to the response header
        response.headers["X-Trace-ID"] = trace_id
        return response

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Resolve the trace_id dependency
        trace_id = get_trace_id(request)
        request.state.trace_id = trace_id  # Set trace_id in request state if not already set

        # Resolve RequestContext and Logger dependencies
        request_context = get_request_context(trace_id=trace_id)
        logger = get_logger(context=request_context)

        # Resolve the TelegramBotClient dependency
        telegram_bot_client = get_telegram_bot_client(logger=logger)

        try:
            response = await call_next(request)
        except Exception as e:
            # Log and notify about the error
            error_message = f"Unhandled exception occurred: {str(e)}"
            logger.error(error_message)
            for user_id in app_settings.notify_users_ids:
                try:
                    telegram_bot_client.notify_admin(user_id, error_message)
                except Exception as e:
                    error_message = f"Unhandled exception occurred when send message to bot [{user_id}]: {str(e)}"
                    logger.error(error_message)

            # Return a generic error response
            return JSONResponse(
                content={"detail": "Internal Server Error"},
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
        return response

# @app.middleware("http")
# async def add_trace_id(request: Request, call_next):
#     trace_id = str(uuid.uuid4())
#     request.state.trace_id = trace_id
#
#     response = await call_next(request)
#     response.headers["X-Trace-ID"] = trace_id
#
#     return response


app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(AddTraceIDMiddleware)


@app.get("/health")
async def health_check(logger_service = Depends(get_logger)):
    logger_service.info("Health check endpoint was accessed", extra_info={'request_id': 'N/A', 'extra_info': 'Health check'})

    return {"status": "healthy"}

app.include_router(api_router)
