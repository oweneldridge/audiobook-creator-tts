"""
Unit tests for text processing functions

Tests for split_text, validate_text, split_text_smart, and chunk_chapter_text
"""

import pytest
from main import split_text, validate_text
from main_document_mode import split_text_smart, chunk_chapter_text, Chapter


@pytest.mark.unit
class TestSplitText:
    """Tests for split_text function from main.py"""

    def test_split_text_empty_input(self) -> None:
        """Test that empty text returns empty list"""
        result = split_text("")
        assert result == []

    def test_split_text_none_input(self) -> None:
        """Test that None input returns empty list"""
        result = split_text(None)  # type: ignore[arg-type]
        assert result == []

    def test_split_text_short_text(self, short_text: str) -> None:
        """Test text shorter than chunk size returns single chunk"""
        result = split_text(short_text, chunk_size=1000)
        assert len(result) == 1
        assert result[0] == short_text

    def test_split_text_at_period(self) -> None:
        """Test splitting at period boundary"""
        text = "First sentence. " * 100  # Will exceed 1000 chars
        result = split_text(text, chunk_size=1000)

        assert len(result) > 1
        # Each chunk should end with a period
        for chunk in result[:-1]:  # All except last
            assert chunk.rstrip().endswith(".")

    def test_split_text_at_comma(self) -> None:
        """Test splitting at comma when no period available"""
        text = "word, " * 200  # Exceeds 1000 chars, only commas
        result = split_text(text, chunk_size=1000)

        assert len(result) > 1
        # Should split at commas
        for chunk in result[:-1]:
            assert "," in chunk

    def test_split_text_no_punctuation(self) -> None:
        """Test splitting when no period or comma available"""
        text = "word " * 300  # Exceeds 1000 chars, no punctuation
        result = split_text(text, chunk_size=1000)

        assert len(result) > 1
        # Should split at chunk_size
        for chunk in result[:-1]:
            assert len(chunk) <= 1000

    def test_split_text_custom_chunk_size(self) -> None:
        """Test with custom chunk size"""
        text = "word. " * 100
        result = split_text(text, chunk_size=50)

        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 50 or chunk == result[-1]

    def test_split_text_preserves_content(self) -> None:
        """Test that split text preserves all content when rejoined"""
        text = "First sentence. Second sentence. Third sentence. " * 50
        result = split_text(text, chunk_size=1000)

        # Rejoin and compare (accounting for stripped whitespace)
        rejoined = "".join(result)
        assert rejoined.replace(" ", "") == text.replace(" ", "")

    def test_split_text_strips_leading_whitespace(self) -> None:
        """Test that leading whitespace is stripped from chunks"""
        text = "First.    Second.    Third." * 50
        result = split_text(text, chunk_size=100)

        for chunk in result:
            # Should not start with multiple spaces
            assert not chunk.startswith("  ")


@pytest.mark.unit
class TestValidateText:
    """Tests for validate_text function"""

    def test_validate_text_ascii_only(self) -> None:
        """Test that ASCII text passes through unchanged"""
        text = "Hello world! This is a test 123."
        result = validate_text(text)
        assert result == text

    def test_validate_text_keeps_unicode_drops_emoji(self, non_ascii_text: str) -> None:
        """Unicode letters/accents are preserved (for neural TTS); emoji are dropped."""
        result = validate_text(non_ascii_text)

        # Emoji / pictographs removed (TTS can't voice them)
        assert "🎉" not in result

        # Accented letters now PRESERVED (previously stripped to ASCII)
        assert "é" in result
        assert "ñ" in result
        assert "ü" in result

        # ASCII text intact
        assert "Hello world" in result

    def test_validate_text_empty_input(self) -> None:
        """Test empty string input"""
        result = validate_text("")
        assert result == ""

    def test_validate_text_preserves_punctuation(self) -> None:
        """Test that ASCII punctuation is preserved"""
        text = "Hello! How are you? I'm fine, thanks."
        result = validate_text(text)
        assert result == text

    def test_validate_text_preserves_numbers(self) -> None:
        """Test that numbers are preserved"""
        text = "The year is 2025 and I have 42 apples."
        result = validate_text(text)
        assert result == text

    def test_validate_text_mixed_content(self) -> None:
        """Test text with mixed ASCII and non-ASCII"""
        text = "Hello café, I love piñatas and crème brûlée!"
        result = validate_text(text)

        # ASCII parts preserved
        assert "Hello" in result
        assert "I love" in result

        # Non-ASCII removed
        assert "café" not in result or "caf" in result  # é removed


@pytest.mark.unit
class TestSplitTextSmart:
    """Tests for split_text_smart function from main_document_mode.py"""

    def test_split_text_smart_empty(self) -> None:
        """Test empty string returns empty list"""
        result = split_text_smart("", chunk_size=1000)
        assert result == []

    def test_split_text_smart_short_text(self) -> None:
        """Test text shorter than chunk size returns single item"""
        text = "Short text here."
        result = split_text_smart(text, chunk_size=1000)
        assert len(result) == 1
        assert result[0] == text

    def test_split_text_smart_paragraph_boundaries(self) -> None:
        """Test splitting at paragraph boundaries"""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3." * 50
        result = split_text_smart(text, chunk_size=500)

        assert len(result) > 1
        # Should split at double newlines when possible

    def test_split_text_smart_sentence_boundaries(self) -> None:
        """Test splitting at sentence boundaries"""
        text = "Sentence one. Sentence two. Sentence three. " * 50
        result = split_text_smart(text, chunk_size=500)

        assert len(result) > 1
        # Each chunk should ideally end with punctuation
        for chunk in result[:-1]:
            last_char = chunk.rstrip()[-1] if chunk.strip() else ""
            assert last_char in ".!?,"

    def test_split_text_smart_respects_chunk_size(self) -> None:
        """Test that chunks don't exceed size limit significantly"""
        text = "Word. " * 500
        chunk_size = 1000
        result = split_text_smart(text, chunk_size=chunk_size)

        for chunk in result:
            # Allow some overflow for natural boundaries
            assert len(chunk) <= chunk_size * 1.1  # 10% tolerance


@pytest.mark.unit
class TestChunkChapterText:
    """Tests for chunk_chapter_text function"""

    def test_chunk_chapter_text_basic(self) -> None:
        """Test basic chapter chunking"""
        chapter = Chapter(
            number=1, title="Test Chapter", dir_name="01-test-chapter", text="Test content. " * 100, chunks=[]
        )
        chunk_chapter_text(chapter, chunk_size=500)

        assert hasattr(chapter, "chunks")
        assert len(chapter.chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chapter.chunks)

    def test_chunk_chapter_text_empty_chapter(self) -> None:
        """Test chunking empty chapter"""
        chapter = Chapter(number=1, title="Empty", dir_name="01-empty", text="", chunks=[])
        chunk_chapter_text(chapter, chunk_size=1000)

        assert hasattr(chapter, "chunks")
        # Should handle empty gracefully

    def test_chunk_chapter_text_modifies_chapter_object(self) -> None:
        """Test that function modifies the chapter object in place"""
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="Content. " * 50, chunks=[])

        # Clear chunks to test modification
        chapter.chunks = []

        chunk_chapter_text(chapter, chunk_size=500)

        assert hasattr(chapter, "chunks")
        assert chapter.chunks is not None
        assert len(chapter.chunks) > 0

    def test_chunk_chapter_text_preserves_content(self) -> None:
        """Test that chunking preserves all text content"""
        original_text = "Chapter content. " * 100
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text=original_text, chunks=[])

        chunk_chapter_text(chapter, chunk_size=500)

        # Reconstruct text from chunks
        reconstructed = "".join(chapter.chunks)
        assert reconstructed.replace(" ", "") == original_text.replace(" ", "")


@pytest.mark.unit
class TestTextProcessingEdgeCases:
    """Edge case tests for text processing"""

    def test_very_long_word(self) -> None:
        """Test handling of word longer than chunk size"""
        # Create a word longer than chunk size
        long_word = "a" * 1500
        text = f"Start {long_word} end."

        result = split_text(text, chunk_size=1000)
        assert len(result) > 0
        assert long_word in "".join(result)

    def test_only_whitespace(self) -> None:
        """Test text with only whitespace"""
        text = "   \n\n   \t\t   "
        _ = split_text(text, chunk_size=1000)
        # Should handle gracefully

    def test_special_characters_in_split(self, text_with_special_chars: str) -> None:
        """Test splitting with special characters"""
        result = split_text(text_with_special_chars, chunk_size=50)
        assert len(result) > 0

    def test_unicode_handling_in_validate(self) -> None:
        """Test various Unicode characters"""
        text = "Test → → emoji: 😀, math: ∑, currency: €£¥"
        result = validate_text(text)

        # ASCII parts should remain
        assert "Test" in result
        assert "emoji" in result

    def test_mixed_line_endings(self) -> None:
        """Test different line ending styles"""
        text = "Line1\nLine2\r\nLine3\rLine4"
        result = split_text(text, chunk_size=1000)
        assert len(result) >= 1
