import time
import uuid
import logging
from typing import Callable, Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from app.core.logging import get_logger, RequestIdFilter

# Initialize logger
logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Add request ID filter to thread's logger
        request_filter = RequestIdFilter(request_id)
        logging.getLogger().handlers[0].addFilter(request_filter)
        
        # Extract request details
        client_host = request.client.host if request.client else "unknown"
        request_path = request.url.path
        query_params = str(dict(request.query_params)) if request.query_params else "{}"
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request_path} "
            f"| Query: {query_params} | Client: {client_host}"
        )
        
        # Measure processing time
        start_time = time.time()
        
        # Create a response object
        try:
            # Process the request and get response
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log the response
            logger.info(
                f"Response: {response.status_code} "
                f"| Processed in {process_time:.4f}s"
            )
            
            # Add request ID header to response
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            # Calculate processing time for error case
            process_time = time.time() - start_time
            
            # Log the exception with traceback
            logger.exception(
                f"Request failed: {str(e)} | Processed in {process_time:.4f}s"
            )
            
            # Re-raise the exception
            raise
        finally:
            # Remove the request filter to avoid memory leaks
            logging.getLogger().handlers[0].removeFilter(request_filter)


def setup_request_logging(app: FastAPI) -> None:
    """
    Add request logging middleware to FastAPI application.
    
    Args:
        app: The FastAPI application.
    """
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("Request logging middleware configured")