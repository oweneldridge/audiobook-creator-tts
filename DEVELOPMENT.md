# Development Guide

Guide for developers working on this project.

## Setup

Install dependencies:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-test.txt
```

Verify installation:

```bash
black --version
flake8 --version
pytest --version
mypy --version
```

## Pre-Commit Hook

A pre-commit hook runs automatically before each commit and checks:

- Black (code formatting)
- Flake8 (linting)
- Pytest (unit tests)

```bash
git add .
git commit -m "Your commit message"
# Hook runs automatically here
```

If checks fail, the commit is blocked until you fix the issues.

To bypass the hook (use sparingly):

```bash
git commit --no-verify -m "Your commit message"
```

Manual checks:

```bash
source venv/bin/activate

# Check formatting
black --check *.py tests/

# Fix formatting
black *.py tests/

# Run linting
flake8 *.py tests/

# Run tests
pytest tests/unit/

# Run with coverage
pytest --cov=. --cov-report=html
```

## Code Quality Standards

**Black**: Line length 120 characters. Run `black .` to auto-format.

**Flake8**: Max line length 120, max complexity 10.

**MyPy**: Optional type checking. Run `mypy *.py --ignore-missing-imports`.

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_voice_management.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Verbose output
pytest -v
```

Test structure:

```filetree
tests/
├── unit/              # Fast, isolated unit tests
├── integration/       # Integration tests with external dependencies
└── conftest.py        # Shared fixtures
```

Write tests with descriptive names like `test_function_name_scenario_expected_result`. Mock external dependencies in unit tests. Aim for >80% coverage.

Table-driven test pattern:

```python
testCases = []struct {
    name   string
    mockDB func(t *testing.T) *mocks.YourDAO
}{
    {
        name: "success",
        mockDB: func(t *testing.T) *mocks.YourDAO {
            m := mocks.NewYourDAO(t)
            m.On("Method", context.Background(), "x").Return("y", nil)
            return m
        },
    },
}
for _, tc := range testCases {
    t.Run(tc.name, func(t *testing.T) { ... })
}
```

## Configuration Files

- **pytest.ini** - Pytest configuration
- **pyproject.toml** - Black, MyPy configuration
- **.flake8** - Flake8 linting rules
- **requirements.txt** - Production dependencies
- **requirements-test.txt** - Development dependencies

## Troubleshooting

**Pre-commit hook not running:**

```bash
chmod +x .git/hooks/pre-commit
source venv/bin/activate
```

**Linting errors:**

```bash
black *.py tests/
flake8 *.py tests/
```

**Test failures:**

```bash
pytest -v
pytest tests/unit/test_file.py::test_function_name -v
```

## Best Practices

1. Always work in virtual environment: `source venv/bin/activate`
2. Run tests before committing (pre-commit hook does this automatically)
3. Format code with Black before committing
4. Write tests for new features
5. Keep dependencies updated
6. Follow existing code patterns

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
