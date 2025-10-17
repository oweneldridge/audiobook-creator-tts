# Development Guide

Guide for developers working on Audiobook Creator TTS.

## Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Install development/testing dependencies
pip install -r requirements-test.txt
```

### 2. Verify Installation

```bash
# Check that linters and formatters are installed
black --version
flake8 --version
pytest --version
mypy --version
```

## Pre-Commit Hook

A pre-commit hook is configured to run automatically before each commit. It performs the following checks:

1. **Black** - Code formatting check
2. **Flake8** - Linting and style guide enforcement
3. **Pytest** - Unit tests

### How It Works

The hook runs automatically when you attempt to commit:

```bash
git add .
git commit -m "Your commit message"
# Pre-commit hook runs automatically here
```

If any check fails, the commit will be blocked until you fix the issues.

### Bypassing the Hook

In rare cases where you need to commit without running checks:

```bash
git commit --no-verify -m "Your commit message"
```

**Note:** Use `--no-verify` sparingly and only when absolutely necessary.

### Manual Checks

You can run the checks manually before committing:

```bash
# Run all checks
source venv/bin/activate

# Check code formatting
black --check *.py tests/

# Fix code formatting automatically
black *.py tests/

# Run linting
flake8 *.py tests/

# Run unit tests
pytest tests/unit/

# Run all tests with coverage
pytest --cov=. --cov-report=html
```

## Code Quality Standards

### Formatting (Black)
- Line length: 120 characters
- Automatically formats code to Python community standards
- Run `black .` to auto-format your code before committing

### Linting (Flake8)
- Max line length: 120 characters
- Max complexity: 10 (cyclomatic complexity)
- Enforces PEP 8 style guide with some exceptions

### Type Checking (MyPy)
- Optional but recommended
- Run `mypy *.py --ignore-missing-imports` for type checking
- Currently not enforced by pre-commit hook

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_voice_management.py

# Run with coverage report
pytest --cov=. --cov-report=html

# Run tests in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_voice_management.py
│   ├── test_text_processing.py
│   └── ...
├── integration/       # Integration tests (slower, external dependencies)
│   ├── test_api_interactions.py
│   └── test_workflows.py
└── conftest.py        # Shared fixtures
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_function_name_scenario_expected_result`
- Mock external dependencies in unit tests
- Aim for high test coverage (>80%)

## Configuration Files

- **pytest.ini** - Pytest configuration
- **pyproject.toml** - Black, MyPy, and other tool configurations
- **.flake8** - Flake8 linting rules
- **requirements.txt** - Production dependencies
- **requirements-test.txt** - Development and testing dependencies

## Troubleshooting

### Pre-commit hook not running

1. Ensure the hook is executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

2. Verify you're in the virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Linting errors

1. Auto-fix formatting issues:
   ```bash
   black *.py tests/
   ```

2. Review Flake8 errors and fix manually:
   ```bash
   flake8 *.py tests/
   ```

### Test failures

1. Run tests with verbose output:
   ```bash
   pytest -v
   ```

2. Run specific failing test:
   ```bash
   pytest tests/unit/test_file.py::test_function_name -v
   ```

3. Check test logs and error messages for details

## Best Practices

1. **Always work in virtual environment** - `source venv/bin/activate`
2. **Run tests before committing** - The pre-commit hook will do this automatically
3. **Format code with Black** - Run `black .` before committing
4. **Write tests for new features** - Maintain or improve test coverage
5. **Keep dependencies updated** - Regularly update requirements files
6. **Follow existing code patterns** - Consistency is key

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
