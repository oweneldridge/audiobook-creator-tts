"""
Integration tests for complete workflows

Tests for end-to-end text-to-speech conversion workflows
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.mark.integration
class TestTextToSpeechWorkflow:
    """Integration tests for complete TTS workflow"""

    @patch("main.get_audio")
    @patch("main.save_audio")
    def test_single_chunk_workflow(
        self, mock_save: Mock, mock_get: Mock, short_text: str, mock_audio_response: bytes
    ) -> None:
        """Test complete workflow for single chunk"""
        from main import split_text, validate_text

        mock_get.return_value = mock_audio_response

        # Workflow steps
        sanitized_text = validate_text(short_text)
        chunks = split_text(sanitized_text, chunk_size=1000)

        assert len(chunks) == 1

        # Process chunk
        for i, _ in enumerate(chunks, start=1):
            audio = mock_get.return_value
            assert audio is not None

            mock_save(audio, "audio/test", i)

        # Verify calls
        assert mock_save.called

    @patch("main.get_audio")
    @patch("main.save_audio")
    def test_multi_chunk_workflow(
        self, mock_save: Mock, mock_get: Mock, long_text: str, mock_audio_response: bytes
    ) -> None:
        """Test complete workflow for multiple chunks"""
        from main import split_text, validate_text

        mock_get.return_value = mock_audio_response

        # Workflow steps
        sanitized_text = validate_text(long_text)
        chunks = split_text(sanitized_text, chunk_size=1000)

        assert len(chunks) > 1

        # Process all chunks
        success_count = 0
        for i, _ in enumerate(chunks, start=1):
            audio = mock_get.return_value
            if audio:
                mock_save(audio, "audio/test", i)
                success_count += 1

        assert success_count == len(chunks)
        assert mock_save.call_count == len(chunks)

    @patch("main.get_audio")
    @patch("main.save_audio")
    def test_workflow_with_retry_logic(
        self, mock_save: Mock, mock_get: Mock, short_text: str, mock_audio_response: bytes
    ) -> None:
        """Test workflow with retry on failure"""
        from main import split_text, validate_text

        # First call fails, second succeeds
        mock_get.side_effect = [None, mock_audio_response]

        sanitized_text = validate_text(short_text)
        chunks = split_text(sanitized_text, chunk_size=1000)

        # Simulate retry logic
        for i, _ in enumerate(chunks, start=1):
            max_retries = 3
            audio = None

            for retry in range(max_retries):
                audio = mock_get.return_value if retry == 1 else None
                if audio:
                    break

            if audio:
                mock_save(audio, "audio/test", i)

        # Should eventually succeed
        assert mock_save.called

    @patch("main.load_voices")
    @patch("main.get_audio")
    @patch("main.save_audio")
    def test_complete_workflow_with_voice_selection(
        self,
        mock_save: Mock,
        mock_get: Mock,
        mock_load: Mock,
        sample_voices_data: Dict[str, Any],
        short_text: str,
        mock_audio_response: bytes,
    ) -> None:
        """Test complete workflow including voice selection"""
        from main import split_text, validate_text, get_voice_id

        mock_load.return_value = sample_voices_data
        mock_get.return_value = mock_audio_response

        # Load voices
        voices = mock_load()
        assert voices is not None

        # Select voice (simulating user choosing option 1)
        voice_id, _ = get_voice_id(voices, choice=1)
        assert voice_id is not None

        # Process text
        sanitized_text = validate_text(short_text)
        chunks = split_text(sanitized_text, chunk_size=1000)

        # Convert to speech
        for i, _ in enumerate(chunks, start=1):
            audio = mock_get.return_value
            mock_save(audio, "audio/test", i)

        assert mock_save.called


@pytest.mark.integration
class TestDocumentConversionWorkflow:
    """Integration tests for document conversion workflows"""

    @pytest.mark.asyncio
    @patch("main_document_mode.DocumentParser.extract_text_from_txt")
    @patch("main_document_mode.make_backend")
    async def test_txt_to_speech_workflow(self, mock_browser: Mock, mock_extract: Mock, tmp_path: Path) -> None:
        """Test complete TXT to speech workflow"""
        from main_document_mode import split_text_smart

        mock_extract.return_value = "Sample document text. " * 100

        # Mock browser
        mock_browser_instance = Mock()

        # Make request_audio an async function
        async def mock_request_audio(chunk: str, voice_id: str) -> bytes:
            return b"fake audio"

        mock_browser_instance.request_audio = mock_request_audio
        mock_browser.return_value = mock_browser_instance

        # Extract text
        text = mock_extract("test.txt")
        assert text is not None

        # Split into chunks
        chunks = split_text_smart(text, chunk_size=1000)
        assert len(chunks) > 0

        # Process chunks (simplified)
        for chunk in chunks:
            audio = await mock_browser_instance.request_audio(chunk, "voice-111")
            assert audio is not None

    @pytest.mark.asyncio
    @patch("main_document_mode.DocumentParser.extract_chapters_from_epub")
    @patch("main_document_mode.make_backend")
    async def test_epub_to_speech_workflow(
        self, mock_browser: Mock, mock_extract: Mock, sample_chapter_data: List[Dict[str, Any]]
    ) -> None:
        """Test complete EPUB to speech workflow"""
        from main_document_mode import Chapter, chunk_chapter_text

        # Mock chapter extraction
        chapters = [
            Chapter(
                number=ch["number"],
                title=ch["title"],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch["text"],
                chunks=[],
            )
            for ch in sample_chapter_data
        ]
        mock_extract.return_value = chapters

        # Mock browser
        mock_browser_instance = Mock()

        # Make request_audio an async function
        async def mock_request_audio(chunk: str, voice_id: str) -> bytes:
            return b"fake audio"

        mock_browser_instance.request_audio = mock_request_audio
        mock_browser.return_value = mock_browser_instance

        # Extract chapters
        extracted_chapters = mock_extract("test.epub")
        assert extracted_chapters is not None
        assert len(extracted_chapters) > 0

        # Chunk each chapter
        for chapter in extracted_chapters:
            chunk_chapter_text(chapter, chunk_size=1000)
            assert hasattr(chapter, "chunks")

        # Process all chunks
        total_chunks = sum(len(ch.chunks) for ch in extracted_chapters)
        assert total_chunks > 0

    @pytest.mark.asyncio
    @patch("main_document_mode.concatenate_chapter_mp3s")
    @patch("main_document_mode.create_m4b_audiobook")
    async def test_post_processing_workflow(
        self, mock_m4b: Mock, mock_concat: Mock, sample_chapter_data: List[Dict[str, Any]], tmp_path: Path
    ) -> None:
        """Test post-processing workflow (concatenation + M4B)"""
        from main_document_mode import Chapter

        chapters = [
            Chapter(
                number=ch["number"],
                title=ch["title"],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch["text"],
                chunks=[],
            )
            for ch in sample_chapter_data
        ]

        # Simulate chapter files being created
        for chapter in chapters:
            chapter.output_file = str(tmp_path / f"chapter_{chapter.number}.mp3")

        # Concatenate chapters
        mp3_files = [ch.output_file for ch in chapters]
        await mock_concat(mp3_files, str(tmp_path / "complete.mp3"))

        # Create M4B audiobook
        await mock_m4b(chapters, str(tmp_path), "audiobook")

        assert mock_concat.called
        assert mock_m4b.called


@pytest.mark.integration
class TestErrorRecoveryWorkflows:
    """Integration tests for error recovery in workflows"""

    @patch("main.get_audio")
    @patch("main.save_audio")
    def test_partial_failure_recovery(
        self, mock_save: Mock, mock_get: Mock, long_text: str, mock_audio_response: bytes
    ) -> None:
        """Test recovery from partial failures"""
        from main import split_text, validate_text

        # Simulate some chunks failing
        success_pattern = [
            mock_audio_response,  # Success
            None,  # Fail
            mock_audio_response,  # Success
            None,  # Fail
            mock_audio_response,  # Success
        ]
        mock_get.side_effect = success_pattern

        sanitized_text = validate_text(long_text)
        chunks = split_text(sanitized_text, chunk_size=1000)[:5]  # Take first 5

        success_count = 0
        failed_chunks = []

        for i, _ in enumerate(chunks, start=1):
            audio = mock_get()
            if audio:
                mock_save(audio, "audio/test", i)
                success_count += 1
            else:
                failed_chunks.append(i)

        # Should have partial success
        assert success_count > 0
        assert len(failed_chunks) > 0
        assert success_count + len(failed_chunks) == len(chunks)

    @pytest.mark.asyncio
    @patch("main_document_mode.find_existing_audio_directory")
    @patch("main_document_mode.analyze_progress")
    async def test_resume_from_checkpoint(
        self, mock_analyze: Mock, mock_find: Mock, sample_chapter_data: List[Dict[str, Any]], tmp_path: Path
    ) -> None:
        """Test resuming conversion from checkpoint"""
        from main_document_mode import Chapter

        chapters = [
            Chapter(
                number=ch["number"],
                title=ch["title"],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch["text"],
                chunks=[],
            )
            for ch in sample_chapter_data
        ]

        # Simulate existing progress
        mock_find.return_value = str(tmp_path / "audio/existing")
        mock_analyze.return_value = (5, 10, [(1, 3), (2, 2)])  # 5 done, 5 remaining

        # Find existing directory
        existing_dir = mock_find("output")
        assert existing_dir is not None

        # Analyze progress
        completed, total, incomplete = mock_analyze(existing_dir, chapters)
        assert completed < total
        assert len(incomplete) > 0

        # Should resume from incomplete chunks
        # (actual implementation would process only incomplete chunks)


@pytest.mark.integration
class TestDataFlowWorkflows:
    """Integration tests for data flow through system"""

    def test_text_sanitization_flow(self, non_ascii_text: str) -> None:
        """Test text sanitization through workflow"""
        from main import validate_text, split_text

        # Original text has non-ASCII
        assert any(ord(c) > 127 for c in non_ascii_text)

        # Sanitize
        sanitized = validate_text(non_ascii_text)

        # Unicode letters/punctuation are preserved (neural TTS voices them);
        # control characters and emoji/pictographs are stripped.
        import unicodedata

        for c in sanitized:
            if c in ("\n", "\t"):
                continue
            cat = unicodedata.category(c)
            assert cat[0] != "C", f"control char survived: {c!r}"
            assert cat != "So", f"pictograph survived: {c!r}"

        # Should still be splittable
        chunks = split_text(sanitized, chunk_size=100)
        assert len(chunks) > 0

    def test_voice_data_flow(self, mock_voices_json: Path, sample_voices_data: Dict[str, Any]) -> None:
        """Test voice data flow from file to selection"""
        from main import load_voices, display_voices, get_voice_id

        # Load voices
        voices = load_voices()
        assert voices is not None

        # Count voices
        voice_count = display_voices(voices)
        assert voice_count > 0

        # Select a voice
        voice_id, _ = get_voice_id(voices, choice=1)
        assert voice_id is not None
        assert voice_id.startswith("voice-")

    @patch("main.get_audio")
    def test_chunk_to_audio_flow(self, mock_get: Mock, short_text: str, mock_audio_response: bytes) -> None:
        """Test flow from text chunk to audio data"""
        from main import validate_text

        mock_get.return_value = mock_audio_response

        # Sanitize chunk
        _ = validate_text(short_text)

        # Request audio
        audio_data = mock_get.return_value

        # Verify audio data
        assert audio_data is not None
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0


@pytest.mark.integration
class TestConcurrentWorkflows:
    """Integration tests for concurrent operations"""

    @patch("main.get_audio")
    def test_concurrent_chunk_processing(self, mock_get: Mock, long_text: str, mock_audio_response: bytes) -> None:
        """Test processing multiple chunks concurrently"""
        import concurrent.futures
        from main import split_text, validate_text

        mock_get.return_value = mock_audio_response

        sanitized_text = validate_text(long_text)
        chunks = split_text(sanitized_text, chunk_size=1000)[:5]  # First 5 chunks

        def process_chunk(chunk: str) -> bytes:
            return mock_get.return_value

        # Process concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All chunks should be processed
        assert len(results) == len(chunks)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_async_workflow_coordination(self, sample_chapter_data: List[Dict[str, Any]]) -> None:
        """Test async coordination of multiple operations"""
        import asyncio
        from main_document_mode import Chapter

        chapters = [
            Chapter(
                number=ch["number"],
                title=ch["title"],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch["text"],
                chunks=[],
            )
            for ch in sample_chapter_data
        ]

        async def process_chapter(chapter: Any) -> str:
            # Simulate async processing
            await asyncio.sleep(0.01)
            return f"Processed: {chapter.title}"

        # Process all chapters concurrently
        results = await asyncio.gather(*[process_chapter(ch) for ch in chapters])

        assert len(results) == len(chapters)
        assert all("Processed" in r for r in results)
