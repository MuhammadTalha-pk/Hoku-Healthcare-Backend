"""Global API error handlers. Original contributor: Faisal Majeed."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "status_code": exc.status_code, "message": exc.detail, "path": request.url.path},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status_code": 422,
                "message": "Invalid request data",
                "path": request.url.path,
                "errors": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        logger.warning("Database integrity error: %s", exc)
        return JSONResponse(
            status_code=409,
            content={"success": False, "status_code": 409, "message": "The data conflicts with an existing record", "path": request.url.path},
        )

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception):
        logger.exception("Unhandled application error")
        return JSONResponse(
            status_code=500,
            content={"success": False, "status_code": 500, "message": "Internal server error", "path": request.url.path},
        )
