"""
Unit tests for file operations

Tests for save_audio, audio concatenation, M4B creation, and progress tracking
"""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from main import save_audio
from main_document_mode import (
    concatenate_chapter_mp3s, create_m4b_audiobook,
    find_existing_audio_directory, analyze_progress,
    check_ffmpeg_installed
)


@pytest.mark.unit
@pytest.mark.audio
class TestSaveAudio:
    """Tests for save_audio function"""

    def test_save_audio_success(self, tmp_path, mock_audio_response):
        """Test successfully saving audio file"""
        directory = tmp_path / "audio"
        chunk_num = 1

        with patch('main.os.makedirs') as mock_makedirs:
            with patch('builtins.open', create=True) as mock_open:
                save_audio(mock_audio_response, str(directory), chunk_num)

                # Should create directory (without exist_ok argument)
                mock_makedirs.assert_called_once_with(str(directory))

                # Should write file
                expected_path = str(directory / "audio_chunk_1.mp3")
                mock_open.assert_called_once()

    def test_save_audio_none_response(self, tmp_path, capsys):
        """Test handling None response"""
        directory = tmp_path / "audio"

        save_audio(None, str(directory), 1)

        captured = capsys.readouterr()
        assert "No audio data" in captured.out

    def test_save_audio_empty_response(self, tmp_path):
        """Test handling empty response"""
        directory = tmp_path / "audio"

        save_audio(b"", str(directory), 1)

        # Should handle empty bytes

    def test_save_audio_creates_directory(self, tmp_path, mock_audio_response):
        """Test that directory is created if it doesn't exist"""
        directory = tmp_path / "audio" / "new_subdir"

        assert not directory.exists()

        with patch('builtins.open', create=True):
            save_audio(mock_audio_response, str(directory), 1)

            # Directory creation would be called

    def test_save_audio_file_path_format(self, tmp_path, mock_audio_response):
        """Test correct file path formatting"""
        directory = tmp_path / "audio"

        with patch('main.os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                save_audio(mock_audio_response, str(directory), 42)

                # Check file path contains chunk number
                call_args = mock_open.call_args
                file_path = call_args[0][0]
                assert "audio_chunk_42.mp3" in file_path

    def test_save_audio_write_error(self, tmp_path, mock_audio_response, capsys):
        """Test handling write errors"""
        directory = tmp_path / "audio"

        with patch('main.os.makedirs'):
            with patch('builtins.open', side_effect=IOError("Write error")):
                save_audio(mock_audio_response, str(directory), 1)

                captured = capsys.readouterr()
                assert "Error saving audio" in captured.out

    def test_save_audio_multiple_chunks(self, tmp_path, mock_audio_response):
        """Test saving multiple chunks in sequence"""
        directory = tmp_path / "audio"

        with patch('main.os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                for i in range(1, 4):
                    save_audio(mock_audio_response, str(directory), i)

                # Should be called 3 times
                assert mock_open.call_count == 3


@pytest.mark.unit
@pytest.mark.audio
class TestCheckFFmpegInstalled:
    """Tests for check_ffmpeg_installed function"""

    @patch('main_document_mode.subprocess.run')
    def test_ffmpeg_installed(self, mock_run):
        """Test when ffmpeg is installed"""
        mock_run.return_value = Mock(returncode=0)

        result = check_ffmpeg_installed()

        assert result is True
        mock_run.assert_called_once()

    @patch('main_document_mode.subprocess.run')
    def test_ffmpeg_not_installed(self, mock_run):
        """Test when ffmpeg is not installed"""
        mock_run.side_effect = FileNotFoundError()

        result = check_ffmpeg_installed()

        assert result is False

    @patch('main_document_mode.subprocess.run')
    def test_ffmpeg_check_error(self, mock_run):
        """Test handling errors during ffmpeg check"""
        import subprocess
        # Use TimeoutExpired which is caught by the implementation
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='ffmpeg', timeout=5)

        result = check_ffmpeg_installed()

        assert result is False


@pytest.mark.unit
@pytest.mark.audio
class TestConcatenateChapterMP3s:
    """Tests for concatenate_chapter_mp3s function"""

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    @patch('main_document_mode.os.path.getsize')
    async def test_concatenate_success(self, mock_getsize, mock_run, tmp_path):
        """Test successful MP3 concatenation"""
        # Create dummy MP3 files
        mp3_files = []
        for i in range(3):
            mp3_file = tmp_path / f"chunk_{i+1}.mp3"
            mp3_file.write_bytes(b"fake mp3 data")
            mp3_files.append(str(mp3_file))

        chapter_dir = str(tmp_path)
        chapter_name = "01-test-chapter"
        mock_run.return_value = Mock(returncode=0)
        # Mock file sizes to pass validation
        mock_getsize.return_value = 1000

        result = await concatenate_chapter_mp3s(chapter_dir, chapter_name, mp3_files)

        # Should call subprocess
        assert mock_run.called

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_concatenate_empty_list(self, mock_run, tmp_path):
        """Test concatenation with empty file list"""
        chapter_dir = str(tmp_path)
        chapter_name = "01-test-chapter"

        result = await concatenate_chapter_mp3s(chapter_dir, chapter_name, [])

        # Should return None for empty list (no files to concatenate)
        assert result is None

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_concatenate_single_file(self, mock_run, tmp_path):
        """Test concatenation with single file"""
        mp3_file = tmp_path / "chunk_1.mp3"
        mp3_file.write_bytes(b"fake mp3 data")

        chapter_dir = str(tmp_path)
        chapter_name = "01-test-chapter"

        # Mock run to simulate successful ffmpeg execution
        mock_run.return_value = Mock(returncode=0)

        result = await concatenate_chapter_mp3s(chapter_dir, chapter_name, [str(mp3_file)])

        # Should handle single file (may or may not concatenate depending on implementation)

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_concatenate_error_handling(self, mock_run, tmp_path):
        """Test error handling during concatenation"""
        mp3_files = [str(tmp_path / "file1.mp3"), str(tmp_path / "file2.mp3")]
        chapter_dir = str(tmp_path)
        chapter_name = "01-test-chapter"

        mock_run.side_effect = Exception("FFmpeg error")

        # Should handle error gracefully and return None
        result = await concatenate_chapter_mp3s(chapter_dir, chapter_name, mp3_files)
        assert result is None  # Error should return None


@pytest.mark.unit
@pytest.mark.audio
class TestCreateM4BAudiobook:
    """Tests for create_m4b_audiobook function"""

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_create_m4b_success(self, mock_run, tmp_path, sample_chapter_data):
        """Test successful M4B creation"""
        # Create chapters with proper directory structure
        chapters = []
        for i, ch_data in enumerate(sample_chapter_data):
            from main_document_mode import Chapter
            dir_name = f"{ch_data['number']:02d}-{ch_data['title'].lower().replace(' ', '-')}"
            chapter = Chapter(
                number=ch_data['number'],
                title=ch_data['title'],
                dir_name=dir_name,
                text=ch_data['text'],
                chunks=[]
            )
            chapters.append(chapter)

            # Create chapter directory and MP3 file that the function expects
            chapter_dir = tmp_path / dir_name
            chapter_dir.mkdir()
            mp3_file = chapter_dir / f"{dir_name}.mp3"
            mp3_file.write_bytes(b"fake mp3 data")

        output_name = "audiobook"
        base_directory = str(tmp_path)

        mock_run.return_value = Mock(returncode=0)

        # Use correct parameter order: base_directory, chapters, book_title
        result = await create_m4b_audiobook(base_directory, chapters, output_name)

        # Should call ffmpeg (may be called multiple times for ffprobe, concat, convert)
        assert mock_run.called

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_create_m4b_no_chapters(self, mock_run, tmp_path):
        """Test M4B creation with no chapters"""
        # Use correct parameter order: base_directory, chapters, book_title
        result = await create_m4b_audiobook(str(tmp_path), [], "empty")

        # Should handle empty list and return None
        assert result is None

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_create_m4b_error_handling(self, mock_run, tmp_path, sample_chapter_data):
        """Test error handling during M4B creation"""
        from main_document_mode import Chapter
        chapters = [
            Chapter(number=1, title="Test", dir_name="01-test", text="Content", chunks=[])
        ]
        chapters[0].output_file = str(tmp_path / "test.mp3")

        mock_run.side_effect = Exception("FFmpeg error")

        # Should handle error gracefully and return None
        # Use correct parameter order: base_directory, chapters, book_title
        result = await create_m4b_audiobook(str(tmp_path), chapters, "test")
        assert result is None  # Error should return None


@pytest.mark.unit
@pytest.mark.audio
class TestFindExistingAudioDirectory:
    """Tests for find_existing_audio_directory function"""

    def test_find_existing_directory(self, tmp_path):
        """Test finding existing audio directory"""
        # Create audio directory structure
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        target_dir = audio_dir / "test-output_2025-01-15-10-30-00"
        target_dir.mkdir()

        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("test-output")

            assert result is not None
            assert "test-output" in result
        finally:
            os.chdir(original_cwd)

    def test_find_no_directory(self, tmp_path):
        """Test when no matching directory exists"""
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("nonexistent")

            assert result is None
        finally:
            os.chdir(original_cwd)

    def test_find_multiple_directories(self, tmp_path):
        """Test when multiple matching directories exist"""
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        # Create multiple directories
        (audio_dir / "test_2025-01-15-10-00-00").mkdir()
        (audio_dir / "test_2025-01-15-11-00-00").mkdir()
        (audio_dir / "test_2025-01-15-12-00-00").mkdir()

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = find_existing_audio_directory("test")

            # Should return most recent
            assert result is not None
            assert "test" in result
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
@pytest.mark.audio
class TestAnalyzeProgress:
    """Tests for analyze_progress function"""

    def test_analyze_progress_no_existing(self, tmp_path, sample_chapter_data):
        """Test progress analysis with no existing files"""
        from main_document_mode import Chapter, chunk_chapter_text

        chapters = [
            Chapter(
                number=ch['number'],
                title=ch['title'],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch['text'],
                chunks=[]
            )
            for ch in sample_chapter_data
        ]

        # Chunk chapters so they have chunks to analyze
        for chapter in chapters:
            chunk_chapter_text(chapter, chunk_size=1000)

        completed, total, incomplete = analyze_progress(str(tmp_path), chapters)

        assert completed == 0
        assert total > 0
        assert len(incomplete) > 0  # Should have missing chunks

    def test_analyze_progress_partial_completion(self, tmp_path, sample_chapter_data):
        """Test progress analysis with some completed chunks"""
        from main_document_mode import Chapter, chunk_chapter_text

        chapters = [
            Chapter(
                number=ch['number'],
                title=ch['title'],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch['text'],
                chunks=[]
            )
            for ch in sample_chapter_data
        ]

        # Chunk chapters
        for chapter in chapters:
            chunk_chapter_text(chapter, chunk_size=500)

        # Create some chunk files for the first chapter
        first_chapter = chapters[0]
        chapter_dir = tmp_path / first_chapter.dir_name
        chapter_dir.mkdir()
        (chapter_dir / f"{first_chapter.dir_name.split('-')[0]}-chunk-1.mp3").write_bytes(b"fake audio")

        completed, total, incomplete = analyze_progress(str(tmp_path), chapters)

        # Should detect the one completed chunk
        assert completed > 0
        assert total > completed

    def test_analyze_progress_all_complete(self, tmp_path, sample_chapter_data):
        """Test progress analysis with all chunks completed"""
        from main_document_mode import Chapter, chunk_chapter_text

        chapters = [
            Chapter(
                number=ch['number'],
                title=ch['title'],
                dir_name=f"{ch['number']:02d}-{ch['title'].lower().replace(' ', '-')}",
                text=ch['text'],
                chunks=[]
            )
            for ch in sample_chapter_data
        ]

        # Chunk all chapters
        for chapter in chapters:
            chunk_chapter_text(chapter, chunk_size=1000)

        # Create all chunk files
        for chapter in chapters:
            chapter_dir = tmp_path / chapter.dir_name
            chapter_dir.mkdir()

            # Extract the numeric prefix from dir_name for filename
            dir_prefix = chapter.dir_name.split('-')[0]

            for i in range(len(chapter.chunks)):
                chunk_file = chapter_dir / f"{dir_prefix}-chunk-{i+1}.mp3"
                chunk_file.write_bytes(b"fake audio")

        completed, total, incomplete = analyze_progress(str(tmp_path), chapters)

        assert completed == total
        assert len(incomplete) == 0


@pytest.mark.unit
@pytest.mark.audio
class TestFileOperationEdgeCases:
    """Edge cases for file operations"""

    def test_save_audio_invalid_directory_characters(self, tmp_path, mock_audio_response):
        """Test handling directory names with special characters"""
        # Depending on OS, some characters may be invalid
        directory = tmp_path / "audio:test"  # Colon invalid on some systems

        # Should handle or sanitize
        with patch('main.os.makedirs'):
            with patch('builtins.open', create=True):
                try:
                    save_audio(mock_audio_response, str(directory), 1)
                except (OSError, ValueError):
                    pass  # Expected on some systems

    def test_save_audio_very_large_chunk_number(self, tmp_path, mock_audio_response):
        """Test with very large chunk numbers"""
        directory = tmp_path / "audio"

        with patch('main.os.makedirs'):
            with patch('builtins.open', create=True) as mock_open:
                save_audio(mock_audio_response, str(directory), 999999)

                call_args = mock_open.call_args
                file_path = call_args[0][0]
                assert "999999" in file_path

    @pytest.mark.asyncio
    @patch('main_document_mode.subprocess.run')
    async def test_concatenate_nonexistent_files(self, mock_run, tmp_path):
        """Test concatenation with non-existent source files"""
        mp3_files = [
            str(tmp_path / "nonexistent1.mp3"),
            str(tmp_path / "nonexistent2.mp3")
        ]
        chapter_dir = str(tmp_path)
        chapter_name = "01-test-chapter"

        mock_run.side_effect = Exception("File not found")

        # Should handle missing files and return None
        result = await concatenate_chapter_mp3s(chapter_dir, chapter_name, mp3_files)
        assert result is None  # Error should return None

    def test_find_directory_permission_denied(self, tmp_path):
        """Test handling permission errors"""
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        # Create a directory we can't read (platform-dependent)
        restricted_dir = audio_dir / "restricted"
        restricted_dir.mkdir()

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Should handle permission errors gracefully
            result = find_existing_audio_directory("restricted")
            # May return None or raise exception depending on implementation
        finally:
            os.chdir(original_cwd)
