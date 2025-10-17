# Audiobook Creator TTS Test Suite Documentation

Comprehensive testing suite for the Audiobook Creator text-to-speech API project.

## Table of Contents

- [Overview](#overview)
- [Test Architecture](#test-architecture)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage](#coverage)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Overview

The Audiobook Creator TTS test suite provides comprehensive functional testing with mocked external dependencies. The suite is designed to achieve 80%+ code coverage while maintaining fast execution times and deterministic results.

**Test Philosophy:**
- **No Browser Testing**: All browser-based functionality is mocked
- **No Real API Calls**: All HTTP requests use mocked responses
- **Deterministic**: Tests produce consistent results across runs
- **Fast**: Complete suite runs in under 1 minute

## Test Architecture

```
tests/
├── unit/                          # Fast, isolated unit tests
│   ├── test_text_processing.py   # Text chunking, validation, sanitization
│   ├── test_voice_management.py  # Voice loading, selection, statistics
│   ├── test_document_parsing.py  # Document format extraction
│   └── test_file_operations.py   # Audio file operations, FFmpeg
│
├── integration/                   # Multi-component tests
│   ├── test_api_interactions.py  # API request/response handling
│   └── test_workflows.py         # End-to-end workflow testing
│
├── fixtures/                      # Test data and samples
│   ├── sample_test.txt           # Text document sample
│   ├── sample_markdown.md        # Markdown sample
│   ├── sample_html.html          # HTML sample
│   └── voices_test.json          # Test voice configuration
│
├── conftest.py                    # Pytest configuration & fixtures
└── __init__.py
```

### Test Framework Stack

- **pytest** (v7.4+) - Main test framework
- **pytest-asyncio** - Async/await test support
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking utilities
- **responses** - HTTP request mocking
- **faker** - Test data generation

## Installation

### 1. Install Test Dependencies

```bash
# Install test requirements
pip install -r requirements-test.txt

# Or install individually
pip install pytest pytest-asyncio pytest-cov pytest-mock responses faker
```

### 2. Verify Installation

```bash
pytest --version
# Should show: pytest 7.4.0 or higher
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_text_processing.py

# Run specific test class
pytest tests/unit/test_text_processing.py::TestSplitText

# Run specific test function
pytest tests/unit/test_text_processing.py::TestSplitText::test_split_text_empty_input
```

### Run by Category

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only document parsing tests
pytest -m document

# Run only voice management tests
pytest -m voice

# Run only audio file operation tests
pytest -m audio
```

### Run with Coverage

```bash
# Run with coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html

# Coverage with missing line details
pytest --cov --cov-report=term-missing

# Fail if coverage below 80%
pytest --cov --cov-fail-under=80
```

### Advanced Options

```bash
# Run tests in parallel (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Quiet mode (minimal output)
pytest -q

# Very verbose with all details
pytest -vv
```

## Test Categories

### Unit Tests (~70% of coverage)

**Fast, isolated tests with no external dependencies**

#### Text Processing (`test_text_processing.py`)
- **TestSplitText**: Text chunking at natural boundaries
- **TestValidateText**: ASCII sanitization and validation
- **TestSplitTextSmart**: Smart chunking with paragraph/sentence awareness
- **TestChunkChapterText**: Chapter-specific text chunking

**Example:**
```bash
pytest tests/unit/test_text_processing.py -v
```

#### Voice Management (`test_voice_management.py`)
- **TestLoadVoices**: Voice JSON loading and validation
- **TestDisplayVoices**: Voice enumeration and display
- **TestGetVoiceId**: Voice selection by index
- **TestCountVoiceStats**: Voice statistics calculation
- **TestSelectVoiceInteractive**: Interactive voice selection

**Example:**
```bash
pytest tests/unit/test_voice_management.py::TestLoadVoices -v
```

#### Document Parsing (`test_document_parsing.py`)
- **TestChapterClass**: Chapter dataclass operations
- **TestDocumentParserTXT**: Plain text extraction
- **TestDocumentParserPDF**: PDF text extraction (mocked)
- **TestDocumentParserEPUB**: EPUB chapter extraction (mocked)
- **TestDocumentParserDOCX**: DOCX paragraph extraction (mocked)
- **TestDocumentParserHTML**: HTML text extraction
- **TestDocumentParserMarkdown**: Markdown to text conversion

**Example:**
```bash
pytest tests/unit/test_document_parsing.py -m document
```

#### File Operations (`test_file_operations.py`)
- **TestSaveAudio**: Audio file saving and directory creation
- **TestCheckFFmpegInstalled**: FFmpeg availability detection
- **TestConcatenateChapterMP3s**: MP3 file concatenation
- **TestCreateM4BAudiobook**: M4B audiobook creation
- **TestFindExistingAudioDirectory**: Resume functionality
- **TestAnalyzeProgress**: Progress tracking and analysis

**Example:**
```bash
pytest tests/unit/test_file_operations.py -m audio
```

### Integration Tests (~30% of coverage)

**Multi-component tests with mocked external services**

#### API Interactions (`test_api_interactions.py`)
- **TestGetAudioIntegration**: Complete API request/response cycles
- **TestAPIRetryLogic**: Retry behavior on failures
- **TestAPIDataSanitization**: Text sanitization before API calls
- **TestAPIHeaderValidation**: Request header validation
- **TestAPIPerformance**: Response time and concurrent calls

**Example:**
```bash
pytest tests/integration/test_api_interactions.py -m api
```

#### Workflows (`test_workflows.py`)
- **TestTextToSpeechWorkflow**: Complete TTS conversion workflows
- **TestDocumentConversionWorkflow**: Document-to-audio pipelines
- **TestErrorRecoveryWorkflows**: Failure recovery and resume
- **TestDataFlowWorkflows**: Data flow through system components
- **TestConcurrentWorkflows**: Parallel processing coordination

**Example:**
```bash
pytest tests/integration/test_workflows.py -m integration
```

## Coverage

### Coverage Targets

- **Overall**: 80% minimum (enforced by pytest.ini)
- **Unit Tests**: 90%+ preferred
- **Integration Tests**: 70%+ acceptable
- **Critical Paths**: 100% required

### Viewing Coverage

```bash
# Terminal report with missing lines
pytest --cov --cov-report=term-missing

# HTML report (detailed, interactive)
pytest --cov --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov --cov-report=xml
```

### Coverage Report Example

```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
main.py                                 200     15    92%   45-47, 123-125
main_document_mode.py                   450     50    89%   234-245, 567-578
main_playwright_persistent.py           120     30    75%   67-89
convert_document.py                      40      5    88%   23-27
-------------------------------------------------------------------
TOTAL                                   810     100   88%
```

### Improving Coverage

If coverage is below target:

1. **Identify uncovered lines**: `pytest --cov --cov-report=term-missing`
2. **Prioritize critical code**: Focus on main logic paths first
3. **Add targeted tests**: Create tests for uncovered branches
4. **Review edge cases**: Ensure error conditions are tested

## Writing New Tests

### Test Structure Template

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit  # or @pytest.mark.integration
@pytest.mark.category  # e.g., @pytest.mark.voice, @pytest.mark.api
class TestFeatureName:
    """Tests for feature_name functionality"""

    def test_basic_functionality(self, fixture_name):
        """Test description"""
        # Arrange
        input_data = "test data"
        expected_output = "expected"

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected_output

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            function_under_test(invalid_input)

    @patch('module.external_dependency')
    def test_with_mocking(self, mock_dependency):
        """Test with mocked dependencies"""
        mock_dependency.return_value = "mocked"

        result = function_under_test()

        assert result is not None
        mock_dependency.assert_called_once()
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py` and automatically available:

```python
def test_with_fixtures(sample_voices_data, short_text, mock_audio_response):
    """Fixtures are injected by pytest"""
    # sample_voices_data: Dictionary of test voices
    # short_text: String with short test content
    # mock_audio_response: Mock HTTP response with audio
    pass
```

### Adding New Fixtures

Add to `tests/conftest.py`:

```python
@pytest.fixture
def my_custom_fixture():
    """Description of fixture"""
    return {"data": "value"}
```

### Test Naming Conventions

- **Test files**: `test_*.py`
- **Test classes**: `Test*` (e.g., `TestSplitText`)
- **Test functions**: `test_*` (e.g., `test_split_text_empty_input`)
- **Descriptive names**: Clearly describe what is being tested

### Markers

Use markers to categorize tests:

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.api          # API-related test
@pytest.mark.document     # Document parsing test
@pytest.mark.voice        # Voice management test
@pytest.mark.audio        # Audio file operations test
@pytest.mark.slow         # Slow-running test
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'main'`

**Solution**:
```bash
# Run from project root
cd /path/to/Audiobook-Creator-TTS
pytest

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/Audiobook-Creator-TTS"
pytest
```

#### 2. Fixture Not Found

**Problem**: `fixture 'sample_voices_data' not found`

**Solution**:
- Verify fixture is defined in `tests/conftest.py`
- Check fixture name matches function parameter
- Ensure conftest.py is in tests/ directory

#### 3. Coverage Below Target

**Problem**: `FAILED: coverage: total of 75 is less than fail-under=80`

**Solution**:
```bash
# Identify missing coverage
pytest --cov --cov-report=term-missing

# Focus on high-value code paths
# Add tests for uncovered lines
```

#### 4. Async Test Failures

**Problem**: `RuntimeWarning: coroutine was never awaited`

**Solution**:
```python
# Mark test as async
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

#### 5. Mock Not Working

**Problem**: Mock not being used; real function called

**Solution**:
```python
# Use correct import path (where it's used, not where it's defined)
@patch('main.get_audio')  # Correct: patch where it's used
# NOT @patch('requests.post')  # Wrong: patch where it's defined

def test_with_mock(mock_get_audio):
    mock_get_audio.return_value = b"fake audio"
    # Test code
```

### Debug Mode

```bash
# Run with Python debugger
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest --showlocals

# Very verbose output
pytest -vv --tb=long
```

### Performance Issues

```bash
# Show slowest tests
pytest --durations=10

# Run in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"
```

## Best Practices

### 1. Test Independence

Each test should be independent and not rely on other tests:

```python
# Good: Self-contained test
def test_function(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("content")
    result = process_file(file)
    assert result == "expected"

# Bad: Depends on external state
def test_function():
    result = process_file("test.txt")  # Assumes file exists
    assert result == "expected"
```

### 2. Use Fixtures for Setup

```python
# Good: Use fixtures
def test_with_fixture(mock_voices_json):
    voices = load_voices()
    assert voices is not None

# Bad: Manual setup in each test
def test_without_fixture(tmp_path):
    # Duplicate setup code
    voices_file = tmp_path / "voices.json"
    with open(voices_file, 'w') as f:
        json.dump({}, f)
    # ... more setup
```

### 3. Clear Test Names

```python
# Good: Descriptive name
def test_split_text_preserves_sentence_boundaries():
    pass

# Bad: Vague name
def test_split():
    pass
```

### 4. Arrange-Act-Assert Pattern

```python
def test_function():
    # Arrange: Set up test data
    input_data = "test"
    expected = "result"

    # Act: Execute function
    result = function_under_test(input_data)

    # Assert: Verify outcome
    assert result == expected
```

### 5. Test One Thing

```python
# Good: Test one aspect
def test_split_text_empty_input():
    result = split_text("")
    assert result == []

def test_split_text_preserves_content():
    text = "content"
    result = split_text(text)
    assert "".join(result) == text

# Bad: Test multiple things
def test_split_text():
    assert split_text("") == []
    assert len(split_text("long text")) > 1
    assert split_text(None) == []
    # ... too many assertions
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

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
        pip install -r requirements-test.txt

    - name: Run tests
      run: |
        pytest --cov --cov-report=xml --cov-fail-under=80

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [responses Documentation](https://github.com/getsentry/responses)

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov --cov-fail-under=80`
4. Update this documentation if adding new test categories

## Support

For issues with tests:

1. Check [Troubleshooting](#troubleshooting) section
2. Review test output with `-vv` flag
3. Use `--pdb` to debug failing tests
4. Check conftest.py for available fixtures

---

**Last Updated**: January 2025
**Test Suite Version**: 1.0.0
**Python Version**: 3.11+
