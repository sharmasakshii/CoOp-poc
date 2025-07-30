import logging
import logging.config
import random
import string
import time


from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse


from starlette.middleware.cors import CORSMiddleware

from co_optimal.config.v1.api_config import api_config


from co_optimal.core.fastapi_blueprints import (
    connect_router as connect_router_v1,
)


from co_optimal.utils.v1.connections import (
    check_connections,
    create_connections,
    remove_connections,
)


from co_optimal.utils.v1.errors import InternalServerException


project_root = Path(__file__).parent.absolute()
log_config_path = project_root / "config" / "v1" / "logging.conf"
if log_config_path.exists():
    logging.config.fileConfig(str(log_config_path), disable_existing_loggers=False)
else:
    print(f"Warning: Logging config file not found at {log_config_path}")

logger = logging.getLogger("co_optimal")

# Configure FastAPI logger to use our configuration
fastapi_logger.handlers = logger.handlers


logger = logging.getLogger(__name__)

fastapi_logger.handlers = logger.handlers

application = FastAPI(title=api_config.PROJECT_NAME, openapi_url=f"/openapi.json")


@application.exception_handler(InternalServerException)
async def internal_server_exception_handler(
    _request: Request, exception: InternalServerException
):
    message = exception.message or "Internal Server Error"
    return JSONResponse(status_code=500, content={"message": message})


@application.middleware("http")
async def log_requests(request: Request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


if api_config.BACKEND_CORS_ORIGINS:
    logger.info("Adding CORS Origins")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in api_config.BACKEND_CORS_ORIGINS.split(",")
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@application.on_event("startup")
def startup():
    create_connections()
    check_connections()


@application.on_event("shutdown")
def shutdown():
    remove_connections()


application.include_router(connect_router_v1, prefix=api_config.API_VER_STR_V1)


@application.post("/health-check")
def health_check():
    return "AI Assistant Backend V1 APIs"
