# Run Tests

Run tests for the project or specific app.

## Default: Run All Tests
Runs all tests in the backend directory.

## With Argument: Run App Tests
Run tests for a specific app, e.g., `/test products`

## Commands

```bash
cd backend && pytest

# Or for specific app
cd backend && pytest apps/<name>/
```

## Coverage

```bash
cd backend && pytest --cov=apps.<name> --cov-report=term-missing
```

## Exit Codes
- 0: All tests passed
- 1: Tests failed
- 2: Test execution error