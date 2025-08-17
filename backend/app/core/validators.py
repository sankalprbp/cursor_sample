"""
Input Validation Utilities
"""

import re
from typing import List, Optional
from fastapi import HTTPException, status


class ValidationUtils:
    """Utility class for common validation patterns"""
    
    PHONE_NUMBER_PATTERN = re.compile(r'^\+[1-9]\d{1,14}$')
    CALL_STATUS_VALUES = ["active", "completed", "failed", "cancelled", "busy", "no-answer"]
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> str:
        """Validate phone number format"""
        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is required"
            )
        
        if not ValidationUtils.PHONE_NUMBER_PATTERN.match(phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format. Must be in E.164 format (e.g., +1234567890)"
            )
        
        return phone_number
    
    @staticmethod
    def validate_call_status(status_value: Optional[str]) -> Optional[str]:
        """Validate call status value"""
        if status_value is None:
            return None
        
        if status_value not in ValidationUtils.CALL_STATUS_VALUES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(ValidationUtils.CALL_STATUS_VALUES)}"
            )
        
        return status_value
    
    @staticmethod
    def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )
        
        return limit, offset
    
    @staticmethod
    def validate_uuid(uuid_string: str, field_name: str = "ID") -> str:
        """Validate UUID format"""
        import uuid
        
        try:
            uuid.UUID(uuid_string)
            return uuid_string
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name} format"
            )