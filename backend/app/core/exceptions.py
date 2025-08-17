"""
Custom Exception Classes and Handlers
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class VoiceAgentException(Exception):
    """Base exception for voice agent operations"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class CallNotFoundException(VoiceAgentException):
    """Raised when a call is not found"""
    
    def __init__(self, call_id: str):
        super().__init__(
            message=f"Call {call_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"call_id": call_id}
        )


class ServiceUnavailableException(VoiceAgentException):
    """Raised when an external service is unavailable"""
    
    def __init__(self, service_name: str, details: Optional[str] = None):
        message = f"{service_name} service is currently unavailable"
        if details:
            message += f": {details}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name, "details": details}
        )


class ValidationException(VoiceAgentException):
    """Raised when validation fails"""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error for {field}: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field": field, "validation_error": message}
        )


async def voice_agent_exception_handler(request: Request, exc: VoiceAgentException) -> JSONResponse:
    """Global exception handler for voice agent exceptions"""
    
    logger.error(f"VoiceAgentException: {exc.message}", extra=exc.details)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unexpected exceptions"""
    
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred",
            "type": "InternalServerError"
        }
    )