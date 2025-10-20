from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import os
import traceback
import time

from app.config import API_PREFIX
from app.api import routes_vaults, routes_query
from app.db.session import get_db, engine
from app.db.models import Base
from app.core import get_logger, setup_request_logging

# Get logger for this module
logger = get_logger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Obsidian Chat",
    description="API for querying Obsidian vaults using natural language",
    version="0.1.0",
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Add request logging middleware
setup_request_logging(app)

# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom handler for HTTP exceptions with logging."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for request validation errors with logging."""
    logger.error(f"Validation error: {exc.errors()}")
    return await request_validation_exception_handler(request, exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Generic exception handler with logging."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return HTMLResponse(
        content="Internal server error",
        status_code=500
    )

# API routes
app.include_router(routes_vaults.router, prefix=API_PREFIX)
app.include_router(routes_query.router, prefix=API_PREFIX)

# Web routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/vaults", response_class=HTMLResponse)
async def vaults_page(request: Request):
    """Render the vaults management page."""
    return templates.TemplateResponse("vaults_list.html", {"request": request})

@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request):
    """Render the query page."""
    return templates.TemplateResponse("query.html", {"request": request})

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Obsidian Chat application")
    # Ensure required directories exist
    from app.config import VECTOR_STORE_PATH
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Obsidian Chat application")
