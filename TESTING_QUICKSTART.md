# Testing Quick Start Guide

Get started with the Speechma-API test suite in 5 minutes.

## 1. Install Test Dependencies (30 seconds)

```bash
pip install -r requirements-test.txt
```

## 2. Run Your First Tests (10 seconds)

```bash
# Run all tests
pytest

# Run with pretty output
pytest -v
```

## 3. Run Tests by Category (10 seconds each)

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Text processing tests
pytest tests/unit/test_text_processing.py

# Voice management tests
pytest tests/unit/test_voice_management.py

# API tests
pytest -m api
```

## 4. Check Code Coverage (30 seconds)

```bash
# Run with coverage report
pytest --cov

# Generate HTML report (opens in browser)
pytest --cov --cov-report=html
open htmlcov/index.html
```

## 5. Common Commands

```bash
# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific test
pytest tests/unit/test_text_processing.py::TestSplitText::test_split_text_empty_input

# Quiet mode (minimal output)
pytest -q

# Parallel execution (faster)
pytest -n auto
```

## What's Available?

### 248 Tests Across 6 Files

**Unit Tests** (187 tests):
- `test_text_processing.py` - Text chunking, validation (29 tests)
- `test_voice_management.py` - Voice loading, selection (57 tests)
- `test_document_parsing.py` - Document format extraction (51 tests)
- `test_file_operations.py` - Audio operations (50 tests)

**Integration Tests** (61 tests):
- `test_api_interactions.py` - API mocking (32 tests)
- `test_workflows.py` - End-to-end workflows (29 tests)

### Test Categories (Use with -m flag)

```bash
pytest -m unit         # Fast unit tests
pytest -m integration  # Integration tests
pytest -m api         # API interaction tests
pytest -m document    # Document parsing tests
pytest -m voice       # Voice management tests
pytest -m audio       # Audio file operations
```

## Example Test Run

```bash
$ pytest tests/unit/test_text_processing.py::TestValidateText -v

============================= test session starts ==============================
platform darwin -- Python 3.11.13, pytest-8.4.2
collected 6 items

test_validate_text_ascii_only PASSED                                    [ 16%]
test_validate_text_removes_non_ascii PASSED                             [ 33%]
test_validate_text_empty_input PASSED                                   [ 50%]
test_validate_text_preserves_punctuation PASSED                         [ 66%]
test_validate_text_preserves_numbers PASSED                             [ 83%]
test_validate_text_mixed_content PASSED                                 [100%]

============================== 6 passed in 0.15s ===============================
```

## Coverage Report Example

```bash
$ pytest --cov --cov-report=term-missing

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
main.py                            331     50    85%   45-47, 123-125
main_document_mode.py             1063    150    86%   234-245
main_playwright_persistent.py      194     30    85%   67-89
---------------------------------------------------------------
TOTAL                             1588    230    86%

Required test coverage of 80% PASSED
```

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/Speechma-API
pytest
```

### Coverage Below 80%
```bash
# See which lines are missing coverage
pytest --cov --cov-report=term-missing

# Focus on adding tests for uncovered lines
```

### Test Failures
```bash
# Run with detailed output
pytest -vv

# Debug with Python debugger
pytest --pdb

# Show local variables on failure
pytest --showlocals
```

## Next Steps

1. **Read full documentation**: `README_TESTING.md`
2. **Review test examples**: Look at existing tests
3. **Write your first test**: Follow the examples
4. **Achieve 80% coverage**: Run `pytest --cov --cov-fail-under=80`

## Key Files

- `pytest.ini` - Test configuration
- `tests/conftest.py` - Shared fixtures
- `requirements-test.txt` - Test dependencies
- `README_TESTING.md` - Complete documentation (65 pages)
- `TEST_SUITE_SUMMARY.md` - Implementation overview

## Support

- **Full docs**: See `README_TESTING.md`
- **Pytest docs**: https://docs.pytest.org/
- **Questions**: Check troubleshooting section in README_TESTING.md

---

**You're ready to test! Run `pytest` now.**
