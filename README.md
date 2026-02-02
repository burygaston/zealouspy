# Zealous-Py

A Python demo project for Harness Code Coverage testing.

## Project Structure

```
zealous-py/
├── src/zealous/
│   ├── models/          # Data models (User, Task, Project)
│   ├── services/        # Business logic services
│   ├── api/             # API handlers (untested)
│   └── utils/           # Utility functions
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── pyproject.toml       # Project configuration
└── requirements.txt     # Dependencies
```

## Expected Coverage

| Module | Expected Coverage | Notes |
|--------|-------------------|-------|
| models/user.py | ~80% | Well tested |
| models/task.py | ~60% | Partially tested |
| models/project.py | ~10% | Poorly tested |
| services/user_service.py | ~50% | Partially tested |
| services/task_service.py | ~20% | Low coverage |
| services/notification_service.py | 0% | Untested |
| api/ | 0% | Untested |
| utils/validators.py | ~30% | Partially tested |
| utils/formatters.py | ~20% | Low coverage |
| utils/crypto.py | 0% | Untested |

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src/zealous --cov-report=term-missing

# Generate LCOV report (for Harness)
pytest --cov=src/zealous --cov-report=lcov:lcov.info
```

## Harness Pipeline

Use the following command in your Harness CI pipeline:

```yaml
- step:
    type: Run
    name: Run Tests with Coverage
    spec:
      shell: Sh
      command: |
        pip install -e ".[dev]"
        pytest --cov=src/zealous --cov-report=lcov:lcov.info --cov-report=term

- step:
    type: Run
    name: Upload Coverage
    spec:
      shell: Sh
      envVariables:
        CI_ENABLE_HCLI_FOR_TESTS: "true"
      command: |
        hcli cov upload --file lcov.info
```
