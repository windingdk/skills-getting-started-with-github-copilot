# Test Suite for High School Management System

This directory contains comprehensive tests for the High School Management System FastAPI application.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_api.py` - API endpoint tests including CRUD operations
- `test_data_validation.py` - Data structure and validation tests
- `test_edge_cases.py` - Edge cases, performance, and error handling tests

## Running Tests

### Prerequisites

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Basic Test Run

Run all tests:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest tests/ -v
```

### Coverage Reports

Run tests with coverage:
```bash
pytest tests/ --cov=src
```

Run tests with detailed coverage report:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Running Specific Tests

Run a specific test file:
```bash
pytest tests/test_api.py
```

Run a specific test class:
```bash
pytest tests/test_api.py::TestSignupEndpoint
```

Run a specific test method:
```bash
pytest tests/test_api.py::TestSignupEndpoint::test_signup_for_activity_success
```

## Test Categories

### API Tests (`test_api.py`)
- **Root Endpoint Tests**: Tests for the main redirect endpoint
- **Activities Endpoint Tests**: Tests for retrieving activity data
- **Signup Endpoint Tests**: Tests for student registration functionality
- **Remove Participant Tests**: Tests for participant removal functionality
- **Integration Tests**: End-to-end workflow tests

### Data Validation Tests (`test_data_validation.py`)
- **Data Structure Tests**: Validates the activities data structure
- **Activity Names Tests**: Validates activity name constraints
- **Data Consistency Tests**: Validates data integrity and constraints
- **Email Validation Tests**: Validates email format requirements

### Edge Cases Tests (`test_edge_cases.py`)
- **Performance Tests**: Response time and concurrent request handling
- **Edge Cases**: Unusual inputs and boundary conditions
- **Error Handling**: Malformed inputs and security considerations
- **Boundary Conditions**: Capacity limits and empty states

## Test Coverage

The test suite achieves 100% code coverage of the FastAPI application, ensuring all code paths are tested.

## Test Data Management

Tests use fixtures to:
- Reset activity data between tests
- Provide consistent test data
- Isolate tests from each other

The `reset_activities` fixture ensures that each test starts with a clean state and doesn't affect other tests.