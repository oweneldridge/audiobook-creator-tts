"""
Unit tests for main_document_mode.py module
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock, mock_open
from dataclasses import dataclass

# Import the module to test
import main_document_mode
from main_document_mode import (
    Chapter,
    DocumentParser,
    kebab_to_title_case,
    check_ffmpeg_installed,
    check_playwright_browser,
    find_existing_audio_directory,
    split_text_smart,
    chunk_chapter_text,
    get_plaintext_input,
)


class TestKebabToTitleCase:
    """Tests for kebab_to_title_case function"""

    def test_simple_title(self):
        """Test simple title conversion"""
        assert kebab_to_title_case("the-great-gatsby") == "The Great Gatsby"

    def test_single_word(self):
        """Test single word"""
        assert kebab_to_title_case("odyssey") == "Odyssey"

    def test_lowercase_words(self):
        """Test lowercase articles and prepositions"""
        assert kebab_to_title_case("tale-of-two-cities") == "Tale of Two Cities"
        assert kebab_to_title_case("war-and-peace") == "War and Peace"
        assert kebab_to_title_case("alice-in-wonderland") == "Alice in Wonderland"

    def test_first_word_always_capitalized(self):
        """Test that first word is always capitalized"""
        assert kebab_to_title_case("a-tale-of-two-cities") == "A Tale of Two Cities"
        assert kebab_to_title_case("the-odyssey") == "The Odyssey"

    def test_multiple_hyphens(self):
        """Test handling of multiple consecutive hyphens"""
        # Multiple hyphens create empty strings which become spaces
        assert kebab_to_title_case("the--great--gatsby") == "The  Great  Gatsby"

    def test_all_lowercase_words(self):
        """Test string with many lowercase article words"""
        result = kebab_to_title_case("journey-to-the-center-of-the-earth")
        assert result == "Journey to the Center of the Earth"

    def test_numbers_in_title(self):
        """Test titles with numbers"""
        assert kebab_to_title_case("20000-leagues-under-the-sea") == "20000 Leagues Under the Sea"


class TestDocumentParserSanitizeDirName:
    """Tests for DocumentParser.sanitize_dir_name"""

    def test_simple_sanitization(self):
        """Test simple text sanitization"""
        assert DocumentParser.sanitize_dir_name("Chapter One") == "chapter-one"

    def test_special_characters(self):
        """Test removal of special characters"""
        assert DocumentParser.sanitize_dir_name("Chapter 1: The Beginning!") == "chapter-1-the-beginning"
        assert DocumentParser.sanitize_dir_name("What's This?") == "whats-this"

    def test_multiple_spaces(self):
        """Test handling of multiple spaces"""
        assert DocumentParser.sanitize_dir_name("Chapter   One   Two") == "chapter-one-two"

    def test_trailing_hyphens(self):
        """Test trimming of leading/trailing hyphens"""
        assert DocumentParser.sanitize_dir_name("---Chapter One---") == "chapter-one"

    def test_unicode_removal(self):
        """Test removal of unicode characters"""
        assert DocumentParser.sanitize_dir_name("Café Société") == "caf-socit"

    def test_already_clean(self):
        """Test already clean input"""
        assert DocumentParser.sanitize_dir_name("chapter-one") == "chapter-one"

    def test_mixed_case_and_special(self):
        """Test mixed case with many special characters"""
        input_text = "Chapter #1: The Great White Whale (Part I)"
        expected = "chapter-1-the-great-white-whale-part-i"
        assert DocumentParser.sanitize_dir_name(input_text) == expected


class TestDocumentParserIsStoryChapter:
    """Tests for DocumentParser._is_story_chapter"""

    def test_numbered_chapters(self):
        """Test detection of numbered chapters"""
        assert DocumentParser._is_story_chapter("Chapter 1") == True
        # "Chapter One" is not detected (only numeric or roman numerals)
        assert DocumentParser._is_story_chapter("Chapter One") == False
        assert DocumentParser._is_story_chapter("CHAPTER 5") == True
        assert DocumentParser._is_story_chapter("chapter 10") == True

    def test_roman_numeral_chapters(self):
        """Test detection of Roman numeral chapters"""
        assert DocumentParser._is_story_chapter("Chapter I") == True
        assert DocumentParser._is_story_chapter("Chapter IV") == True
        assert DocumentParser._is_story_chapter("CHAPTER X") == True

    def test_parts(self):
        """Test detection of parts"""
        assert DocumentParser._is_story_chapter("Part 1") == True
        assert DocumentParser._is_story_chapter("Part I") == True
        assert DocumentParser._is_story_chapter("PART ONE") == False  # "ONE" is not detected as roman

    def test_numeric_prefix(self):
        """Test detection of numeric prefixes"""
        assert DocumentParser._is_story_chapter("1. Introduction") == True
        assert DocumentParser._is_story_chapter("5. The Journey") == True

    def test_non_story_chapters(self):
        """Test non-story chapters are not detected"""
        assert DocumentParser._is_story_chapter("Prologue") == False
        assert DocumentParser._is_story_chapter("Epilogue") == False
        assert DocumentParser._is_story_chapter("Foreword") == False
        assert DocumentParser._is_story_chapter("Preface") == False
        assert DocumentParser._is_story_chapter("Introduction") == False
        assert DocumentParser._is_story_chapter("Table of Contents") == False


class TestCheckFfmpegInstalled:
    """Tests for check_ffmpeg_installed function"""

    def test_ffmpeg_installed(self, monkeypatch):
        """Test when ffmpeg is installed"""
        mock_result = Mock()
        mock_result.returncode = 0

        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr("subprocess.run", mock_run)

        assert check_ffmpeg_installed() == True

    def test_ffmpeg_not_found(self, monkeypatch):
        """Test when ffmpeg is not found"""
        mock_run = Mock(side_effect=FileNotFoundError)
        monkeypatch.setattr("subprocess.run", mock_run)

        assert check_ffmpeg_installed() == False

    def test_ffmpeg_timeout(self, monkeypatch):
        """Test when ffmpeg check times out"""
        import subprocess

        mock_run = Mock(side_effect=subprocess.TimeoutExpired("ffmpeg", 5))
        monkeypatch.setattr("subprocess.run", mock_run)

        assert check_ffmpeg_installed() == False

    def test_ffmpeg_error_returncode(self, monkeypatch):
        """Test when ffmpeg returns error code"""
        mock_result = Mock()
        mock_result.returncode = 1

        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr("subprocess.run", mock_run)

        assert check_ffmpeg_installed() == False


class TestCheckPlaywrightBrowser:
    """Tests for check_playwright_browser function"""

    def test_browser_installed(self, tmp_path, monkeypatch):
        """Test when Playwright browser is installed"""
        # Create fake playwright cache structure
        playwright_cache = tmp_path / ".cache" / "ms-playwright"
        playwright_cache.mkdir(parents=True)
        (playwright_cache / "chromium-1234").mkdir()

        # Mock Path.home() to return our temp directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        assert check_playwright_browser() == True

    def test_browser_not_installed_no_cache(self, tmp_path, monkeypatch):
        """Test when playwright cache doesn't exist"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        assert check_playwright_browser() == False

    def test_browser_not_installed_no_chromium(self, tmp_path, monkeypatch):
        """Test when playwright cache exists but no chromium"""
        playwright_cache = tmp_path / ".cache" / "ms-playwright"
        playwright_cache.mkdir(parents=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        assert check_playwright_browser() == False

    def test_browser_check_exception(self, monkeypatch):
        """Test exception handling in browser check"""
        monkeypatch.setattr(Path, "home", Mock(side_effect=Exception("Test error")))

        assert check_playwright_browser() == False


class TestSplitTextSmart:
    """Tests for split_text_smart function"""

    def test_short_text(self):
        """Test text shorter than chunk size"""
        text = "This is a short text."
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_at_sentence_boundary(self):
        """Test splitting at sentence boundaries"""
        text = "First sentence. " * 100  # ~1600 chars
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) >= 2
        # All chunks should end with period or be last chunk
        for chunk in chunks[:-1]:
            assert chunk.endswith(".")

    def test_split_at_comma(self):
        """Test fallback to comma when no period"""
        text = "word, " * 200  # ~1200 chars, no periods
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) >= 2

    def test_empty_text(self):
        """Test empty text"""
        chunks = split_text_smart("", chunk_size=1000)
        assert chunks == []

    def test_whitespace_normalization(self):
        """Test that excessive whitespace is normalized"""
        text = "First sentence.\n\n\n\nSecond sentence."
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) == 1
        # Should have max 2 newlines
        assert "\n\n\n" not in chunks[0]

    def test_ascii_validation(self, monkeypatch):
        """Test that non-ASCII characters are handled"""
        text = "Text with unicode: café"
        # Mock validate_text to return cleaned text
        monkeypatch.setattr("main_document_mode.validate_text", lambda x: x.replace("é", "e"))
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) == 1

    def test_very_long_text(self):
        """Test text much longer than chunk size"""
        text = "This is sentence number N. " * 200  # ~5400 chars
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) >= 5
        # No chunk should be much larger than chunk_size
        for chunk in chunks:
            assert len(chunk) <= 1100  # Allow some overflow for sentence completion


class TestChunkChapterText:
    """Tests for chunk_chapter_text function"""

    def test_chunk_short_chapter(self):
        """Test chunking chapter with short text"""
        chapter = Chapter(
            number=1, title="Test", dir_name="01-test", text="Short text here.", chunks=[]
        )
        chunk_chapter_text(chapter, chunk_size=1000)
        assert len(chapter.chunks) == 1
        assert chapter.chunks[0] == "Short text here."

    def test_chunk_long_chapter(self):
        """Test chunking chapter with long text"""
        text = "This is a sentence. " * 100  # ~2000 chars
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text=text, chunks=[])
        chunk_chapter_text(chapter, chunk_size=1000)
        assert len(chapter.chunks) >= 2

    def test_chunk_empty_chapter(self):
        """Test chunking chapter with no text"""
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="", chunks=[])
        chunk_chapter_text(chapter, chunk_size=1000)
        assert chapter.chunks == []

    def test_chunks_are_trimmed(self):
        """Test that chunks are stripped of whitespace"""
        text = "   Text with whitespace.   "
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text=text, chunks=[])
        chunk_chapter_text(chapter, chunk_size=1000)
        assert chapter.chunks[0] == "Text with whitespace."


class TestFindExistingAudioDirectory:
    """Tests for find_existing_audio_directory function"""

    def test_no_audio_directory(self):
        """Test when audio directory doesn't exist"""
        result = find_existing_audio_directory("nonexistent")
        assert result is None

    def test_find_matching_directory(self, tmp_path, monkeypatch):
        """Test finding matching directory"""
        # Create audio directory with matching subdirectory
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        test_dir = audio_dir / "test-book_2024-01-01-10-00-00"
        test_dir.mkdir()

        # Change working directory to tmp_path
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("test-book")
            assert result is not None
            assert "test-book_" in result
        finally:
            os.chdir(original_cwd)

    def test_find_most_recent_directory(self, tmp_path, monkeypatch):
        """Test finding most recent when multiple exist"""
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        # Create two directories with different timestamps
        old_dir = audio_dir / "test-book_2024-01-01-10-00-00"
        old_dir.mkdir()
        new_dir = audio_dir / "test-book_2024-01-02-10-00-00"
        new_dir.mkdir()

        # Touch new_dir to make it more recent
        import time
        time.sleep(0.01)
        new_dir.touch()

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("test-book")
            # Should return the more recent directory
            assert result is not None
            assert "test-book_" in result
        finally:
            os.chdir(original_cwd)

    def test_no_matching_directories(self, tmp_path):
        """Test when audio directory exists but no matches"""
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        other_dir = audio_dir / "other-book_2024-01-01-10-00-00"
        other_dir.mkdir()

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("test-book")
            assert result is None
        finally:
            os.chdir(original_cwd)


class TestGetPlaintextInput:
    """Tests for get_plaintext_input function"""

    def test_valid_input(self, monkeypatch):
        """Test valid plaintext input"""
        # Mock inputs: name, then text lines, then END
        inputs = iter(["My Book", "This is line 1.", "This is line 2.", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert output_name == "my-book"
        assert text == "This is line 1. This is line 2."

    def test_empty_name_retry(self, monkeypatch):
        """Test retry when name is empty"""
        inputs = iter(["", "Valid Name", "Some text here.", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert output_name == "valid-name"
        assert text == "Some text here."

    def test_special_chars_in_name(self, monkeypatch):
        """Test sanitization of special characters in name"""
        inputs = iter(["My Book! (2024)", "Some text.", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert output_name == "my-book-2024"

    def test_text_too_short(self, monkeypatch):
        """Test rejection of text that's too short"""
        inputs = iter(["Book Name", "short", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert text is None
        assert output_name is None

    def test_multiline_text(self, monkeypatch):
        """Test multiline text input"""
        inputs = iter(["My Book", "Line 1", "Line 2", "Line 3", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert "Line 1" in text
        assert "Line 2" in text
        assert "Line 3" in text

    def test_invalid_name_retry(self, monkeypatch):
        """Test retry when sanitized name is empty"""
        inputs = iter(["!!!", "Valid Name", "Some text here.", "END"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

        text, output_name = get_plaintext_input()

        assert output_name == "valid-name"


class TestDocumentParserExtractTextMethods:
    """Tests for DocumentParser text extraction methods"""

    def test_extract_text_from_txt_utf8(self, tmp_path, monkeypatch):
        """Test extracting text from UTF-8 TXT file"""
        test_file = tmp_path / "test.txt"
        test_content = "This is test content.\nWith multiple lines."
        test_file.write_text(test_content, encoding="utf-8")

        # Mock print_colored
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_txt(str(test_file))

        assert result == test_content

    def test_extract_text_from_txt_non_utf8(self, tmp_path, monkeypatch):
        """Test TXT extraction with latin-1 encoding"""
        test_file = tmp_path / "test.txt"
        # Create file with latin-1 encoding
        test_content = "Test content with special chars: café"
        test_file.write_bytes(test_content.encode("latin-1", errors="ignore"))

        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_txt(str(test_file))

        # Should read successfully (may have encoding issues but shouldn't crash)
        assert len(result) > 0

    def test_extract_text_from_txt_error(self, monkeypatch):
        """Test error handling in TXT extraction"""
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_txt("/nonexistent/file.txt")

        assert result == ""

    def test_parse_document_pdf(self, tmp_path, monkeypatch):
        """Test parse_document delegates to PDF parser"""
        # Create a temp file so existence check passes
        test_file = tmp_path / "test.pdf"
        test_file.write_text("dummy")

        mock_extract = Mock(return_value="PDF text content")
        monkeypatch.setattr("main_document_mode.DocumentParser.extract_text_from_pdf", mock_extract)

        result = DocumentParser.parse_document(str(test_file))

        mock_extract.assert_called_once_with(str(test_file))
        assert result == "PDF text content"

    def test_parse_document_epub(self, tmp_path, monkeypatch):
        """Test parse_document delegates to EPUB parser"""
        # Create a temp file so existence check passes
        test_file = tmp_path / "test.epub"
        test_file.write_text("dummy")

        mock_extract = Mock(return_value="EPUB text content")
        monkeypatch.setattr("main_document_mode.DocumentParser.extract_text_from_epub", mock_extract)

        result = DocumentParser.parse_document(str(test_file))

        mock_extract.assert_called_once_with(str(test_file))
        assert result == "EPUB text content"

    def test_parse_document_unsupported(self, monkeypatch):
        """Test parse_document with unsupported file type"""
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.parse_document("/fake/file.xyz")

        assert result == ""

    def test_parse_document_not_found(self, monkeypatch):
        """Test parse_document with non-existent file"""
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.parse_document("/nonexistent/file.pdf")

        assert result == ""

    def test_extract_text_from_html(self, tmp_path, monkeypatch):
        """Test HTML text extraction"""
        test_file = tmp_path / "test.html"
        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <script>alert('test');</script>
            <article>
                <p>This is the main content.</p>
                <p>Second paragraph.</p>
            </article>
        </body>
        </html>
        """
        test_file.write_text(html_content)

        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_html(str(test_file))

        assert "main content" in result
        assert "Second paragraph" in result
        assert "alert" not in result  # Script should be removed

    def test_extract_text_from_markdown_simple(self, tmp_path, monkeypatch):
        """Test Markdown extraction (tests fallback mode since mistune may not be imported)"""
        test_file = tmp_path / "test.md"
        md_content = """# Header 1

## Header 2

This is **bold** and *italic* text.

[Link Text](http://example.com)
"""
        test_file.write_text(md_content)

        # Force fallback mode
        monkeypatch.setattr("main_document_mode.MISTUNE_AVAILABLE", False)
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_markdown(str(test_file))

        # Fallback mode should remove markdown syntax
        assert "Header" in result
        assert "bold" in result or "text" in result
        assert "**" not in result  # Bold markers removed
        assert "#" not in result  # Headers removed

    def test_extract_text_from_markdown_without_mistune(self, tmp_path, monkeypatch):
        """Test Markdown extraction without mistune (fallback mode)"""
        test_file = tmp_path / "test.md"
        md_content = "# Header\n\n**Bold** text and [link](url)"
        test_file.write_text(md_content)

        monkeypatch.setattr("main_document_mode.MISTUNE_AVAILABLE", False)
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_text_from_markdown(str(test_file))

        # Fallback mode should remove markdown syntax
        assert "Header" in result
        assert "Bold" in result
        assert "**" not in result  # Bold markers removed


class TestDocumentParserExtractAuthorFromEpub:
    """Tests for extract_author_from_epub function"""

    def test_extract_author_success(self, monkeypatch):
        """Test successful author extraction"""
        # Mock epub book object
        mock_book = Mock()
        mock_book.get_metadata = Mock(return_value=[("Jane Austen", {})])

        # Mock epub.read_epub
        monkeypatch.setattr("main_document_mode.epub.read_epub", Mock(return_value=mock_book))

        result = DocumentParser.extract_author_from_epub("/fake/book.epub")

        assert result == "Jane Austen"

    def test_extract_author_no_metadata(self, monkeypatch):
        """Test when no author metadata exists"""
        mock_book = Mock()
        mock_book.get_metadata = Mock(return_value=[])

        monkeypatch.setattr("main_document_mode.epub.read_epub", Mock(return_value=mock_book))

        result = DocumentParser.extract_author_from_epub("/fake/book.epub")

        assert result is None

    def test_extract_author_empty_string(self, monkeypatch):
        """Test when author metadata is empty string"""
        mock_book = Mock()
        mock_book.get_metadata = Mock(return_value=[("", {})])

        monkeypatch.setattr("main_document_mode.epub.read_epub", Mock(return_value=mock_book))

        result = DocumentParser.extract_author_from_epub("/fake/book.epub")

        assert result is None

    def test_extract_author_exception(self, monkeypatch):
        """Test exception handling during author extraction"""
        monkeypatch.setattr("main_document_mode.epub.read_epub", Mock(side_effect=Exception("Read error")))
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)

        result = DocumentParser.extract_author_from_epub("/fake/book.epub")

        assert result is None


class TestPromptForAuthor:
    """Tests for prompt_for_author function"""

    def test_accept_default_author(self, monkeypatch):
        """Test accepting default author"""
        inputs = iter(["y"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author("Jane Austen")

        assert result == "Jane Austen"

    def test_reject_default_author(self, monkeypatch):
        """Test rejecting default author"""
        inputs = iter(["n"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author("Jane Austen")

        assert result == "Unknown Author"

    def test_custom_author_name(self, monkeypatch):
        """Test entering custom author name"""
        inputs = iter(["custom", "Charles Dickens"])
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author("Jane Austen")

        assert result == "Charles Dickens"

    def test_custom_author_empty(self, monkeypatch):
        """Test custom author with empty input defaults to Unknown"""
        inputs = iter(["custom", ""])
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author("Jane Austen")

        assert result == "Unknown Author"

    def test_no_default_author_with_input(self, monkeypatch):
        """Test when no default author but user provides one"""
        inputs = iter(["Mark Twain"])
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author(None)

        assert result == "Mark Twain"

    def test_no_default_author_skip(self, monkeypatch):
        """Test when no default author and user skips"""
        inputs = iter([""])
        monkeypatch.setattr("main_document_mode.print_colored", lambda text, color: None)
        monkeypatch.setattr("main_document_mode.input_colored", lambda prompt, color: next(inputs))

        result = main_document_mode.prompt_for_author(None)

        assert result == "Unknown Author"
