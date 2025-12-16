"""
Code Execution Schemas

Pydantic models for code execution requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ExecuteCodeRequest(BaseModel):
    """
    Request model for executing code.
    
    Contains the code to execute and configuration options.
    """
    code: str = Field(
        ..., 
        max_length=50000, 
        description="Source code to execute"
    )
    language: str = Field(
        ..., 
        description="Programming language"
    )
    stdin: str = Field(
        "", 
        max_length=10000,
        description="Standard input for the program"
    )
    time_limit: int = Field(
        5000, 
        ge=100, 
        le=30000,
        description="Maximum execution time in milliseconds"
    )
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Ensure language is lowercase"""
        return v.lower()
    
    @field_validator('code')
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        """Ensure code is not empty"""
        if not v.strip():
            raise ValueError("Code cannot be empty")
        return v
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "code": "print('Hello, World!')\nfor i in range(5):\n    print(i)",
                "language": "python",
                "stdin": "",
                "time_limit": 5000
            }
        }


class ExecutionResponse(BaseModel):
    """
    Response model for code execution.
    
    Contains output, errors, and metadata about the execution.
    """
    session_id: str = Field(..., description="Session ID where code was executed")
    language: str = Field(..., description="Language used for execution")
    stdout: str = Field(..., description="Standard output from the program")
    stderr: str = Field(..., description="Standard error output")
    exit_code: int = Field(..., description="Process exit code (0 = success)")
    duration: int = Field(..., description="Actual execution time in milliseconds")
    success: bool = Field(..., description="Whether execution completed successfully")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    timestamp: datetime = Field(..., description="When the execution completed")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "session_id": "abc123xyz789",
                "language": "python",
                "stdout": "Hello, World!\n0\n1\n2\n3\n4\n",
                "stderr": "",
                "exit_code": 0,
                "duration": 15,
                "success": True,
                "error": None,
                "timestamp": "2024-01-15T10:45:00Z"
            }
        }
