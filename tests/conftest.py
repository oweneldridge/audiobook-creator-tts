"""
Pytest configuration and shared fixtures for Speechma-API tests
"""
import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_dir():
    """Return the tests directory"""
    return Path(__file__).parent


@pytest.fixture
def fixtures_dir(tests_dir):
    """Return the fixtures directory"""
    return tests_dir / "fixtures"


@pytest.fixture
def temp_audio_dir():
    """Create a temporary directory for audio output"""
    temp_dir = tempfile.mkdtemp(prefix="speechma_test_audio_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Voice Data Fixtures
# ============================================================================

@pytest.fixture
def sample_voices_data() -> Dict[str, Any]:
    """Return minimal voice configuration for testing"""
    return {
        "English": {
            "United States": {
                "female": {
                    "Ava": "voice-111",
                    "Emma": "voice-115"
                },
                "male": {
                    "Andrew": "voice-107",
                    "Brian": "voice-112"
                }
            },
            "United Kingdom": {
                "female": {
                    "Sonia": "voice-35",
                    "Maisie": "voice-30"
                },
                "male": {
                    "Oliver": "voice-20"
                }
            }
        },
        "Spanish": {
            "Spain": {
                "female": {
                    "Lucia": "voice-200"
                },
                "male": {
                    "Diego": "voice-201"
                }
            },
            "Mexico": {
                "female": {
                    "Sofia": "voice-210"
                }
            }
        }
    }


@pytest.fixture
def voices_json_file(tmp_path, sample_voices_data):
    """Create a temporary voices.json file"""
    voices_file = tmp_path / "voices.json"
    with open(voices_file, 'w', encoding='utf-8') as f:
        json.dump(sample_voices_data, f, indent=2)
    return voices_file


@pytest.fixture
def mock_voices_json(tmp_path, sample_voices_data, monkeypatch):
    """Mock voices.json in the current directory"""
    voices_file = tmp_path / "voices.json"
    with open(voices_file, 'w', encoding='utf-8') as f:
        json.dump(sample_voices_data, f, indent=2)

    # Change to temp directory so load_voices() finds our test file
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    yield voices_file

    # Restore original directory
    os.chdir(original_dir)


# ============================================================================
# Text Content Fixtures
# ============================================================================

@pytest.fixture
def short_text():
    """Short text sample (under chunk size)"""
    return "This is a short test message for text-to-speech conversion."


@pytest.fixture
def medium_text():
    """Medium text sample (around 1-2 chunks)"""
    return """
    This is a medium-length text sample that will be used for testing.
    It contains multiple sentences and should be split into chunks.
    The text processing system should handle this gracefully.
    We want to ensure that sentence boundaries are preserved when possible.
    This helps maintain natural speech flow in the audio output.
    """ * 10


@pytest.fixture
def long_text():
    """Long text sample (multiple chunks)"""
    return """
    Chapter 1: The Beginning

    This is a long text that spans multiple paragraphs and will definitely
    require chunking. The system should split this at natural boundaries
    like periods or commas to maintain readability and speech quality.

    Each paragraph contains meaningful content that should be preserved
    in the audio output. The chunking algorithm must be smart enough to
    avoid splitting in the middle of sentences whenever possible.

    Chapter 2: The Middle

    As we continue through the text, we want to ensure that the system
    handles various edge cases properly. This includes dealing with
    special characters, numbers, and punctuation marks.

    The text may also contain apostrophes, quotation marks, and other
    symbols that need to be sanitized before sending to the API.
    """ * 20


@pytest.fixture
def text_with_special_chars():
    """Text with special characters that need sanitization"""
    return "Hello! This text has 'quotes' and \"double quotes\" and special chars: @#$%^&*()."


@pytest.fixture
def non_ascii_text():
    """Text with non-ASCII characters"""
    return "Hello world! This has émojis 🎉 and spëcial çharacters like ñ and ü."


# ============================================================================
# API Response Fixtures
# ============================================================================

@pytest.fixture
def mock_audio_response():
    """Mock successful audio response"""
    # Minimal valid MP3 header
    return b'\xff\xfb\x90\x00' + b'\x00' * 100


@pytest.fixture
def mock_api_success_response(mock_audio_response):
    """Mock successful API response object"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'audio/mpeg'}
    mock_response.content = mock_audio_response
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def mock_api_error_response():
    """Mock error API response object"""
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_response.text = "Forbidden - CAPTCHA required"
    mock_response.raise_for_status = Mock(side_effect=Exception("403 Forbidden"))
    return mock_response


@pytest.fixture
def mock_api_rate_limit_response():
    """Mock rate limit response"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.text = '{"error": "Rate limit exceeded"}'
    mock_response.raise_for_status = Mock(side_effect=Exception("429 Too Many Requests"))
    return mock_response


# ============================================================================
# Document Fixtures
# ============================================================================

@pytest.fixture
def sample_chapter_data():
    """Sample chapter data for testing"""
    return [
        {"number": 1, "title": "Chapter 1: Introduction", "text": "This is the introduction. " * 50},
        {"number": 2, "title": "Chapter 2: Main Content", "text": "This is the main content. " * 100},
        {"number": 3, "title": "Chapter 3: Conclusion", "text": "This is the conclusion. " * 30},
    ]


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content"""
    return """
    Sample PDF Document

    Chapter 1: Introduction
    This is a sample PDF document used for testing the document parsing functionality.

    Chapter 2: Content
    The parser should be able to extract text from various document formats including
    PDF, EPUB, DOCX, and plain text files.
    """


@pytest.fixture
def sample_epub_content():
    """Sample EPUB chapter structure"""
    return {
        "title": "Sample EPUB Book",
        "chapters": [
            {"title": "Chapter 1", "content": "First chapter content. " * 50},
            {"title": "Chapter 2", "content": "Second chapter content. " * 50},
        ]
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent timestamps in tests"""
    from datetime import datetime

    class MockDateTime:
        @staticmethod
        def now():
            mock_dt = Mock()
            mock_dt.strftime = Mock(return_value="2025-01-15 10-30-00")
            return mock_dt

    import main
    monkeypatch.setattr(main, "datetime", MockDateTime)
    return MockDateTime


@pytest.fixture
def capture_print_output(monkeypatch):
    """Capture print_colored output for testing"""
    printed_messages = []

    def mock_print_colored(text, color):
        printed_messages.append({"text": text, "color": color})

    import main
    monkeypatch.setattr(main, "print_colored", mock_print_colored)

    return printed_messages


@pytest.fixture
def mock_os_makedirs(monkeypatch):
    """Mock os.makedirs to prevent actual directory creation"""
    created_dirs = []

    def mock_makedirs(path, exist_ok=False):
        created_dirs.append({"path": path, "exist_ok": exist_ok})

    monkeypatch.setattr(os, "makedirs", mock_makedirs)
    return created_dirs


@pytest.fixture
def mock_file_operations(monkeypatch, tmp_path):
    """Mock file read/write operations"""
    files_written = {}
    files_read = {}

    original_open = open

    def mock_open(file, mode='r', *args, **kwargs):
        if 'w' in mode or 'a' in mode:
            # Track writes
            files_written[file] = {'mode': mode}
            return original_open(tmp_path / Path(file).name, mode, *args, **kwargs)
        elif 'r' in mode:
            # Track reads
            files_read[file] = {'mode': mode}
            if file in files_written:
                return original_open(tmp_path / Path(file).name, mode, *args, **kwargs)
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    return {"written": files_written, "read": files_read}
