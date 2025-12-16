#!/usr/bin/env python
"""
Test Runner Script

This script helps run different types of tests for the backend application.
It ensures the server is running and properly configured for testing.
"""

import sys
import subprocess
import time
import signal
import os
from typing import Optional


class TestRunner:
    """Manages test execution and server lifecycle."""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.original_dir = os.getcwd()
        
    def start_server(self):
        """Start the backend server for testing."""
        print("🚀 Starting test server...")
        
        # Set test environment variables
        env = os.environ.copy()
        env.update({
            "DEBUG": "false",
            "ENABLE_SERVER_EXECUTION": "true",
            "LOG_LEVEL": "WARNING",  # Reduce noise during tests
        })
        
        # Start server in background
        self.server_process = subprocess.Popen(
            ["python", "-m", "app.main"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(2)
        
        # Check if server is responding
        try:
            import httpx
            response = httpx.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                print("✅ Server is ready!\n")
                return True
        except:
            pass
        
        print("⚠️  Server might not be ready, continuing anyway...\n")
        return False
    
    def stop_server(self):
        """Stop the test server."""
        if self.server_process:
            print("\n🛑 Stopping test server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
    
    def run_tests(self, test_type: str = "all"):
        """
        Run tests based on type.
        
        Args:
            test_type: Type of tests to run (all, unit, integration, e2e)
        """
        print(f"🧪 Running {test_type} tests...\n")
        
        # Build pytest command
        cmd = ["pytest", "-v", "--tb=short"]
        
        if test_type == "unit":
            cmd.extend(["-m", "unit"])
        elif test_type == "integration":
            cmd.extend(["-m", "integration", "tests/test_integration.py"])
        elif test_type == "e2e":
            cmd.extend(["-m", "e2e", "tests/test_e2e.py"])
        elif test_type == "coverage":
            cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
        elif test_type == "fast":
            cmd.extend(["-m", "not slow", "-x"])  # Stop on first failure
        
        # Run tests
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    def run_specific_test(self, test_path: str):
        """
        Run a specific test file or function.
        
        Args:
            test_path: Path to test (e.g., tests/test_sessions.py::test_create_session)
        """
        print(f"🧪 Running specific test: {test_path}\n")
        
        cmd = ["pytest", "-v", "--tb=short", test_path]
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_server()
        os.chdir(self.original_dir)


def print_usage():
    """Print usage instructions."""
    print("""
Test Runner for Coding Interview Platform Backend

Usage: python run_tests.py [command] [options]

Commands:
    all         Run all tests (default)
    unit        Run only unit tests (fast)
    integration Run integration tests
    e2e         Run end-to-end tests
    coverage    Run with coverage report
    fast        Run fast tests only, stop on first failure
    specific    Run specific test file or function
    
Options for 'specific' command:
    python run_tests.py specific tests/test_sessions.py
    python run_tests.py specific tests/test_sessions.py::test_create_session

Flags:
    --no-server  Don't start the test server (assumes it's already running)
    --help       Show this help message

Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py unit               # Run unit tests only
    python run_tests.py integration        # Run integration tests
    python run_tests.py coverage           # Generate coverage report
    python run_tests.py specific tests/test_websocket.py
    python run_tests.py --no-server unit   # Run without starting server
""")


def main():
    """Main entry point."""
    # Parse arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print_usage()
        return 0
    
    # Check for no-server flag
    no_server = "--no-server" in args
    if no_server:
        args.remove("--no-server")
    
    # Determine test type
    if not args:
        test_type = "all"
        specific_test = None
    elif args[0] == "specific" and len(args) > 1:
        test_type = "specific"
        specific_test = args[1]
    else:
        test_type = args[0]
        specific_test = None
    
    # Validate test type
    valid_types = ["all", "unit", "integration", "e2e", "coverage", "fast", "specific"]
    if test_type not in valid_types:
        print(f"❌ Invalid test type: {test_type}")
        print_usage()
        return 1
    
    # Create test runner
    runner = TestRunner()
    
    try:
        # Start server if needed
        if not no_server and test_type in ["integration", "e2e", "all"]:
            runner.start_server()
        
        # Run tests
        print("="*60)
        if test_type == "specific":
            success = runner.run_specific_test(specific_test)
        else:
            success = runner.run_tests(test_type)
        print("="*60)
        
        # Print results
        if success:
            print("\n✅ All tests passed!")
            
            if test_type == "coverage":
                print("\n📊 Coverage report generated: htmlcov/index.html")
                print("   Open it with: open htmlcov/index.html")
            
            return 0
        else:
            print("\n❌ Some tests failed. Check the output above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        return 1
        
    finally:
        # Clean up
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())
