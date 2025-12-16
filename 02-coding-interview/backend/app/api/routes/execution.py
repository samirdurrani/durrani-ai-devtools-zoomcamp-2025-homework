"""
Code Execution API Routes

Endpoints for executing code safely.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from app.schemas.execution import ExecuteCodeRequest, ExecutionResponse
from app.services.session_manager import session_manager
from app.services.code_executor import code_executor
from app.models.domain import ExecutionResult
from app.core.exceptions import RateLimitExceededException
from app.core.config import settings


# Create a router for execution endpoints
router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["Execution"]
)


@router.post(
    "/{session_id}/execute",
    response_model=ExecutionResponse,
    summary="Execute code",
    description="Executes code for a session with timeout and resource limits"
)
async def execute_code(
    session_id: str,
    request: ExecuteCodeRequest
):
    """
    Execute code safely with resource limits.
    
    The code runs in a sandboxed environment with:
    - Time limit (default 5 seconds)
    - Memory limit
    - No network access
    - Limited file system access
    
    JavaScript can optionally run in the browser instead.
    
    Args:
        session_id: Session where code is being executed
        request: Code and execution parameters
        
    Returns:
        Execution results including output and errors
        
    Raises:
        404: If session doesn't exist
        429: If rate limit exceeded
        500: If execution fails
    """
    # Check session exists
    try:
        session = session_manager.get_session(session_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Check rate limit
    if not session_manager.check_rate_limit(session_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded: {settings.rate_limit_executions_per_minute} executions per minute",
                "limit": settings.rate_limit_executions_per_minute,
                "window": "1 minute"
            }
        )
    
    # Execute the code
    try:
        stdout, stderr, exit_code, duration_ms, error = code_executor.execute(
            code=request.code,
            language=request.language,
            stdin=request.stdin,
            time_limit_ms=request.time_limit
        )
        
        # Create execution result
        result = ExecutionResult(
            session_id=session_id,
            language=request.language,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms,
            success=(exit_code == 0 and error is None),
            error=error,
            timestamp=datetime.now()
        )
        
        # Add to session history
        session_manager.add_execution_result(session_id, result)
        
        # Return response
        return ExecutionResponse(
            session_id=session_id,
            language=request.language,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration=duration_ms,
            success=result.success,
            error=error,
            timestamp=result.timestamp
        )
        
    except Exception as e:
        # Execution failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "EXECUTION_FAILED",
                "message": f"Code execution failed: {str(e)}"
            }
        )
