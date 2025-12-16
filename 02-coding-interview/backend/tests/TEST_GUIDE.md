# 🧪 Integration Testing Guide

Complete guide for testing the client-server interaction of the Online Coding Interview Platform.

## 📚 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The integration tests verify that the React frontend and FastAPI backend work together correctly. They test:

- ✅ Full user workflows (create session → join → collaborate → execute)
- ✅ WebSocket real-time communication
- ✅ Multi-user collaboration scenarios
- ✅ Error handling and recovery
- ✅ Performance under load

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_health.py           # Basic API tests
├── test_sessions.py         # Session management tests
├── test_languages.py        # Language support tests
├── test_execution.py        # Code execution tests
├── test_integration.py      # Client-server integration tests
├── test_e2e.py             # End-to-end React simulation tests
└── TEST_GUIDE.md           # This file
```

### Test Categories

1. **Unit Tests** (`@pytest.mark.unit`)
   - Fast, isolated tests
   - No external dependencies
   - Test individual functions/classes

2. **Integration Tests** (`@pytest.mark.integration`)
   - Test multiple components together
   - Include WebSocket communication
   - Verify data flow between services

3. **End-to-End Tests** (`@pytest.mark.e2e`)
   - Simulate complete React client behavior
   - Test full user workflows
   - Verify production scenarios

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py unit          # Fast unit tests only
python run_tests.py integration   # Integration tests
python run_tests.py e2e          # End-to-end tests
python run_tests.py coverage     # With coverage report
```

### Manual Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_integration.py

# Run specific test
pytest tests/test_integration.py::TestFullWorkflow::test_websocket_collaboration

# Run with markers
pytest -m integration     # Only integration tests
pytest -m "not slow"      # Skip slow tests

# Generate coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Parallel Execution

```bash
# Run tests in parallel (faster for large test suites)
pytest -n auto            # Auto-detect CPU cores
pytest -n 4              # Use 4 workers
```

## 🧪 Test Examples

### 1. Basic Integration Test

```python
def test_create_and_join_session(client):
    """Test creating a session and joining it."""
    # Create session
    response = client.post("/api/v1/sessions", json={"host_name": "Test"})
    session_id = response.json()["session_id"]
    
    # Join session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
```

### 2. WebSocket Collaboration Test

```python
def test_websocket_collaboration(client, ws_url):
    """Test real-time collaboration."""
    # Create WebSocket clients
    client1 = WebSocketClient(session_id, "user1", "Alice")
    client2 = WebSocketClient(session_id, "user2", "Bob")
    
    # Connect both
    client1.connect(ws_url)
    client2.connect(ws_url)
    
    # Client1 updates code
    client1.send_code_update("console.log('Hello');")
    
    # Client2 receives update
    update = client2.wait_for_message("code_update")
    assert update["data"]["code"] == "console.log('Hello');"
```

### 3. End-to-End React Simulation

```python
async def test_interviewer_flow():
    """Simulate complete interviewer workflow."""
    interviewer = ReactClient()
    
    # Create session (like clicking button)
    session = await interviewer.create_session("Interview")
    
    # Connect WebSocket (automatic in React)
    await interviewer.connect_websocket()
    
    # Update code (like typing in editor)
    await interviewer.update_code("def solution(): pass")
    
    # Execute code (like clicking Run)
    result = await interviewer.execute_code()
```

## 📊 Test Coverage

### Current Coverage Areas

✅ **Session Management**
- Creating sessions
- Joining sessions  
- Listing sessions
- Ending sessions

✅ **Real-time Collaboration**
- WebSocket connections
- Code synchronization
- Language changes
- User presence

✅ **Code Execution**
- Python execution
- JavaScript handling
- Rate limiting
- Timeout protection

✅ **Error Scenarios**
- Invalid sessions
- Network interruptions
- Rate limit exceeded
- Malformed requests

### Coverage Report

Generate and view coverage:

```bash
# Generate coverage
python run_tests.py coverage

# View in terminal
pytest --cov=app --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

## 🔧 Writing New Tests

### Integration Test Template

```python
@pytest.mark.integration
class TestNewFeature:
    """Test new feature integration."""
    
    def test_feature_workflow(self, client, ws_url):
        """Test complete feature workflow."""
        # 1. Setup - Create session/connect
        session = create_session(client)
        ws = connect_websocket(ws_url, session["session_id"])
        
        # 2. Action - Perform user actions
        perform_action(ws)
        
        # 3. Verify - Check results
        assert verify_result(client, session["session_id"])
        
        # 4. Cleanup
        ws.disconnect()
```

### E2E Test Template

```python
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_user_journey():
    """Test complete user journey."""
    user = ReactClient()
    
    try:
        # Setup
        await user.create_session()
        await user.connect_websocket()
        
        # User actions
        await user.update_code("// code")
        result = await user.execute_code()
        
        # Assertions
        assert result["success"]
        
    finally:
        # Cleanup
        await user.disconnect()
```

## 🐛 Troubleshooting

### Common Issues

**Server not starting for tests**
```bash
# Start server manually
python -m app.main

# In another terminal
python run_tests.py --no-server
```

**WebSocket connection fails**
```python
# Add delay after connection
client.connect(ws_url)
time.sleep(0.5)  # Wait for connection
```

**Tests timeout**
```python
# Increase timeout for slow tests
@pytest.mark.timeout(10)  # 10 seconds
def test_slow_operation():
    pass
```

**Port already in use**
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Debug Mode

Run tests with detailed output:

```bash
# Maximum verbosity
pytest -vvv

# Show print statements
pytest -s

# Debug on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

## 📈 Performance Testing

### Load Testing WebSockets

```python
def test_concurrent_users(client, ws_url):
    """Test with many concurrent users."""
    clients = []
    for i in range(50):  # 50 concurrent users
        ws = WebSocketClient(session_id, f"user{i}", f"User{i}")
        ws.connect(ws_url)
        clients.append(ws)
    
    # Verify all connected
    session = client.get(f"/api/v1/sessions/{session_id}")
    assert session.json()["participant_count"] == 50
```

### Benchmarking

```python
@pytest.mark.benchmark
def test_execution_performance(benchmark, client):
    """Benchmark code execution."""
    def execute():
        client.post("/api/v1/sessions/test/execute", 
                   json={"code": "print(1)", "language": "python"})
    
    result = benchmark(execute)
    assert result.stats["mean"] < 0.1  # Less than 100ms average
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements-test.txt
    
    - name: Run integration tests
      run: python run_tests.py integration
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      if: success()
```

## 🎯 Test Checklist

Before deploying, ensure:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Coverage > 80%
- [ ] No flaky tests
- [ ] Performance benchmarks met
- [ ] Error scenarios tested
- [ ] Multi-user scenarios tested
- [ ] WebSocket reconnection tested
- [ ] Rate limiting verified

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [WebSocket Testing Guide](https://websockets.readthedocs.io/en/stable/intro/tutorial2.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test-Driven Development](https://testdriven.io/)

---

**Remember**: Good integration tests catch bugs before users do! 🚀
