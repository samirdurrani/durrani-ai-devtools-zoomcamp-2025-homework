"""
Code Execution Service

This service handles safe code execution for different programming languages.
It includes:
- Sandboxed execution with resource limits
- Timeout protection
- Output capture

SECURITY WARNING: This is a simplified implementation for development.
In production, use Docker containers or a dedicated execution service.
"""

import subprocess
import tempfile
import os
import time
import signal
import threading
from typing import Tuple, Optional
from pathlib import Path

from app.core.config import settings
from app.models.domain import Language


class CodeExecutor:
    """
    Executes code safely with resource limits and timeout protection.
    
    This implementation uses subprocess with timeout for simplicity.
    In production, use Docker containers or services like Judge0.
    """
    
    # Language configurations
    LANGUAGE_CONFIG = {
        "python": {
            "command": ["python3", "-u"],
            "extension": ".py",
            "compile": False
        },
        "javascript": {
            "command": ["node"],
            "extension": ".js",
            "compile": False
        },
        "java": {
            "command": ["java"],
            "extension": ".java",
            "compile": True,
            "compile_command": ["javac"]
        },
        "cpp": {
            "command": ["./a.out"],
            "extension": ".cpp",
            "compile": True,
            "compile_command": ["g++", "-o", "a.out"]
        }
    }
    
    def execute(
        self,
        code: str,
        language: str,
        stdin: str = "",
        time_limit_ms: int = 5000
    ) -> Tuple[str, str, int, int, Optional[str]]:
        """
        Execute code in a given language.
        
        Args:
            code: Source code to execute
            language: Programming language
            stdin: Input for the program
            time_limit_ms: Maximum execution time in milliseconds
            
        Returns:
            Tuple of (stdout, stderr, exit_code, duration_ms, error_message)
        """
        if not settings.enable_server_execution:
            return self._mock_execution(code, language)
        
        # Get language configuration
        config = self.LANGUAGE_CONFIG.get(language)
        if not config:
            return "", "", 1, 0, f"Language '{language}' is not supported for execution"
        
        # Create temporary file for code
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_file = Path(tmpdir) / f"code{config['extension']}"
            code_file.write_text(code)
            
            try:
                # Compile if needed
                if config.get("compile"):
                    compile_result = self._compile(code_file, config, tmpdir)
                    if compile_result:
                        return "", compile_result, 1, 0, "Compilation failed"
                
                # Execute the code
                return self._run_code(
                    code_file, 
                    config, 
                    stdin, 
                    time_limit_ms, 
                    tmpdir
                )
                
            except Exception as e:
                return "", str(e), 1, 0, f"Execution error: {str(e)}"
    
    def _compile(
        self,
        code_file: Path,
        config: dict,
        working_dir: str
    ) -> Optional[str]:
        """
        Compile code if required.
        
        Args:
            code_file: Path to source file
            config: Language configuration
            working_dir: Working directory
            
        Returns:
            Error message if compilation fails, None if successful
        """
        compile_cmd = config["compile_command"] + [str(code_file)]
        
        try:
            result = subprocess.run(
                compile_cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=10  # 10 second compile timeout
            )
            
            if result.returncode != 0:
                return result.stderr or "Compilation failed"
            
            return None
            
        except subprocess.TimeoutExpired:
            return "Compilation timed out"
        except Exception as e:
            return f"Compilation error: {str(e)}"
    
    def _run_code(
        self,
        code_file: Path,
        config: dict,
        stdin: str,
        time_limit_ms: int,
        working_dir: str
    ) -> Tuple[str, str, int, int, Optional[str]]:
        """
        Run the code with timeout and resource limits.
        
        Args:
            code_file: Path to code file
            config: Language configuration
            stdin: Program input
            time_limit_ms: Timeout in milliseconds
            working_dir: Working directory
            
        Returns:
            Execution results
        """
        # Prepare command
        if config.get("compile"):
            cmd = config["command"]  # Use compiled binary
        else:
            cmd = config["command"] + [str(code_file)]
        
        # Start timer
        start_time = time.time()
        
        try:
            # Run the process with timeout
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                text=True,
                preexec_fn=self._limit_resources if os.name != 'nt' else None
            )
            
            # Communicate with timeout
            stdout, stderr = process.communicate(
                input=stdin,
                timeout=time_limit_ms / 1000.0
            )
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Truncate output if too long
            stdout = self._truncate_output(stdout)
            stderr = self._truncate_output(stderr)
            
            return stdout, stderr, process.returncode, duration_ms, None
            
        except subprocess.TimeoutExpired:
            # Kill the process
            process.kill()
            process.wait()
            
            duration_ms = time_limit_ms
            return "", "", -1, duration_ms, f"Execution timed out after {time_limit_ms}ms"
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return "", str(e), 1, duration_ms, f"Runtime error: {str(e)}"
    
    def _limit_resources(self):
        """
        Set resource limits for the subprocess (Unix only).
        
        This prevents the subprocess from consuming too many resources.
        """
        if os.name == 'nt':  # Windows doesn't support resource limits
            return
        
        try:
            import resource
            
            # Limit CPU time (seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            
            # Limit memory (bytes) - 128MB
            resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
            
            # Limit file size (bytes) - 1MB
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
            
        except:
            pass  # Resource limiting not available
    
    def _truncate_output(self, output: str) -> str:
        """
        Truncate output if it exceeds maximum size.
        
        Args:
            output: Output string
            
        Returns:
            Truncated output
        """
        max_size = settings.code_max_output_size
        if len(output) > max_size:
            return output[:max_size] + "\n... (output truncated)"
        return output
    
    def _mock_execution(
        self,
        code: str,
        language: str
    ) -> Tuple[str, str, int, int, Optional[str]]:
        """
        Mock execution for when server execution is disabled.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Mock execution results
        """
        # Return a mock response indicating execution would happen client-side
        if language == "javascript":
            return (
                "// JavaScript execution happens in the browser",
                "",
                0,
                10,
                None
            )
        else:
            return (
                f"# Server-side execution is disabled for {language}\n"
                f"# Enable it in settings or use client-side execution",
                "",
                0,
                0,
                None
            )


# Create a global instance
code_executor = CodeExecutor()
