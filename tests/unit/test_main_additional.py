"""
Additional comprehensive tests for main.py to increase coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json


class TestGetAudio:
    """Tests for get_audio function"""

    def test_get_audio_success(self, monkeypatch):
        """Test successful audio retrieval"""
        import main

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "audio/mpeg"}
        mock_response.content = b"audio_data"
        mock_response.raise_for_status = Mock()

        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("main.req.post", mock_post)

        url = "http://test.com/api"
        data = {"text": "test", "voice": "voice-1"}
        headers = {"User-Agent": "test"}

        result = main.get_audio(url, data, headers)

        assert result == b"audio_data"
        assert mock_post.called

    def test_get_audio_wrong_content_type(self, monkeypatch):
        """Test handling of wrong content type"""
        import main

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status = Mock()

        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("main.req.post", mock_post)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        url = "http://test.com/api"
        data = {"text": "test", "voice": "voice-1"}
        headers = {}

        result = main.get_audio(url, data, headers)

        assert result is None
        assert any("Unexpected response format" in p for p in printed)

    def test_get_audio_request_exception_with_response(self, monkeypatch):
        """Test handling of request exception with response"""
        import main
        import requests as req

        mock_response = Mock()
        mock_response.text = "Error message"

        mock_exception = req.exceptions.RequestException("Failed")
        mock_exception.response = mock_response

        mock_post = Mock(side_effect=mock_exception)
        monkeypatch.setattr("main.req.post", mock_post)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        url = "http://test.com/api"
        data = {"text": "test", "voice": "voice-1"}
        headers = {}

        result = main.get_audio(url, data, headers)

        assert result is None
        assert any("Server response" in p for p in printed)
        assert any("Request failed" in p for p in printed)

    def test_get_audio_request_exception_without_response(self, monkeypatch):
        """Test handling of request exception without response"""
        import main
        import requests as req

        mock_exception = req.exceptions.RequestException("Connection failed")
        mock_exception.response = None

        mock_post = Mock(side_effect=mock_exception)
        monkeypatch.setattr("main.req.post", mock_post)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        url = "http://test.com/api"
        data = {"text": "test", "voice": "voice-1"}
        headers = {}

        result = main.get_audio(url, data, headers)

        assert result is None
        assert any("Request failed" in p for p in printed)

    def test_get_audio_unexpected_exception(self, monkeypatch):
        """Test handling of unexpected exception"""
        import main

        mock_post = Mock(side_effect=ValueError("Unexpected error"))
        monkeypatch.setattr("main.req.post", mock_post)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        url = "http://test.com/api"
        data = {"text": "test", "voice": "voice-1"}
        headers = {}

        result = main.get_audio(url, data, headers)

        assert result is None
        assert any("unexpected error occurred" in p for p in printed)


class TestSaveAudio:
    """Tests for save_audio function"""

    def test_save_audio_success(self, tmp_path, monkeypatch):
        """Test successful audio save"""
        import main

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        audio_data = b"test_audio_data"
        directory = str(tmp_path / "audio")
        chunk_num = 1

        main.save_audio(audio_data, directory, chunk_num)

        # Verify file was created
        assert (tmp_path / "audio" / "audio_chunk_1.mp3").exists()
        assert any("Audio saved" in p for p in printed)

    def test_save_audio_no_data(self, tmp_path, monkeypatch):
        """Test handling of no audio data"""
        import main

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        directory = str(tmp_path / "audio")
        chunk_num = 1

        main.save_audio(None, directory, chunk_num)

        assert any("No audio data to save" in p for p in printed)

    def test_save_audio_io_error(self, tmp_path, monkeypatch):
        """Test handling of IO error during save"""
        import main

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        # Mock open to raise IOError
        mock_file_open = mock_open()
        mock_file_open.side_effect = IOError("Disk full")
        monkeypatch.setattr("builtins.open", mock_file_open)

        audio_data = b"test_audio_data"
        directory = str(tmp_path / "audio")
        chunk_num = 1

        main.save_audio(audio_data, directory, chunk_num)

        assert any("Error saving audio" in p for p in printed)


class TestMultilineInput:
    """Tests for get_multiline_input function"""

    def test_get_multiline_input_single_line(self, monkeypatch):
        """Test single line input"""
        import main

        inputs = ["This is a test", "END"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda: next(input_iter))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.get_multiline_input()

        assert result == "This is a test"

    def test_get_multiline_input_multiple_lines(self, monkeypatch):
        """Test multiple line input"""
        import main

        inputs = ["Line 1", "Line 2", "Line 3", "END"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda: next(input_iter))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.get_multiline_input()

        assert result == "Line 1 Line 2 Line 3"


class TestGracefulExit:
    """Tests for prompt_graceful_exit function"""

    def test_prompt_graceful_exit_yes(self, monkeypatch):
        """Test exiting with yes"""
        import main
        import sys

        monkeypatch.setattr("main.input_colored", lambda prompt, color: "y")

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        with pytest.raises(SystemExit) as exc_info:
            main.prompt_graceful_exit()

        assert exc_info.value.code == 0
        assert any("Exiting gracefully" in p for p in printed)

    def test_prompt_graceful_exit_no(self, monkeypatch):
        """Test continuing with no"""
        import main

        monkeypatch.setattr("main.input_colored", lambda prompt, color: "n")

        # Should return without error
        main.prompt_graceful_exit()

    def test_prompt_graceful_exit_invalid_then_yes(self, monkeypatch):
        """Test invalid input then yes"""
        import main
        import sys

        inputs = ["invalid", "y"]
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        with pytest.raises(SystemExit):
            main.prompt_graceful_exit()

        assert any("Invalid choice" in p for p in printed)


class TestCoverArtFunctions:
    """Tests for cover art related functions"""

    def test_embed_cover_art_success(self, tmp_path, monkeypatch):
        """Test successful cover art embedding"""
        import main
        import subprocess

        # Create test files
        m4b_file = tmp_path / "test.m4b"
        m4b_file.write_bytes(b"test")
        cover_file = tmp_path / "cover.jpg"
        cover_file.write_bytes(b"image")

        # Mock which command
        which_result = Mock()
        which_result.returncode = 0

        # Mock AtomicParsley command
        atomic_result = Mock()
        atomic_result.returncode = 0

        def mock_run(cmd, **kwargs):
            if cmd[0] == "which":
                return which_result
            else:
                return atomic_result

        monkeypatch.setattr("subprocess.run", mock_run)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.embed_cover_art(str(m4b_file), str(cover_file))

        assert result is True
        assert any("Cover art embedded successfully" in p for p in printed)

    def test_embed_cover_art_atomicparsley_not_installed(self, monkeypatch):
        """Test when AtomicParsley is not installed"""
        import main
        import subprocess

        which_result = Mock()
        which_result.returncode = 1

        monkeypatch.setattr("subprocess.run", lambda cmd, **kwargs: which_result)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.embed_cover_art("/fake/file.m4b", "/fake/cover.jpg")

        assert result is False
        assert any("AtomicParsley is not installed" in p for p in printed)

    def test_embed_cover_art_m4b_not_found(self, monkeypatch):
        """Test when M4B file not found"""
        import main
        import subprocess

        which_result = Mock()
        which_result.returncode = 0

        monkeypatch.setattr("subprocess.run", lambda cmd, **kwargs: which_result)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.embed_cover_art("/fake/file.m4b", "/fake/cover.jpg")

        assert result is False
        assert any("M4B file not found" in p for p in printed)

    def test_embed_cover_art_cover_not_found(self, tmp_path, monkeypatch):
        """Test when cover file not found"""
        import main
        import subprocess

        m4b_file = tmp_path / "test.m4b"
        m4b_file.write_bytes(b"test")

        which_result = Mock()
        which_result.returncode = 0

        monkeypatch.setattr("subprocess.run", lambda cmd, **kwargs: which_result)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.embed_cover_art(str(m4b_file), "/fake/cover.jpg")

        assert result is False
        assert any("Cover image not found" in p for p in printed)

    def test_embed_cover_art_atomic_error(self, tmp_path, monkeypatch):
        """Test when AtomicParsley returns error"""
        import main
        import subprocess

        m4b_file = tmp_path / "test.m4b"
        m4b_file.write_bytes(b"test")
        cover_file = tmp_path / "cover.jpg"
        cover_file.write_bytes(b"image")

        which_result = Mock()
        which_result.returncode = 0

        atomic_result = Mock()
        atomic_result.returncode = 1
        atomic_result.stderr = "Error message"

        def mock_run(cmd, **kwargs):
            if cmd[0] == "which":
                return which_result
            else:
                return atomic_result

        monkeypatch.setattr("subprocess.run", mock_run)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.embed_cover_art(str(m4b_file), str(cover_file))

        assert result is False
        assert any("Error embedding cover art" in p for p in printed)

    def test_prompt_for_cover_art_decline(self, monkeypatch):
        """Test declining cover art"""
        import main

        monkeypatch.setattr("main.input_colored", lambda prompt, color: "n")

        result = main.prompt_for_cover_art("/fake/dir")

        assert result is None

    def test_prompt_for_cover_art_use_default(self, tmp_path, monkeypatch):
        """Test using default cover.jpg"""
        import main

        cover_file = tmp_path / "cover.jpg"
        cover_file.write_bytes(b"image")

        inputs = ["y", "y"]
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        result = main.prompt_for_cover_art(str(tmp_path))

        assert result == str(cover_file)

    def test_prompt_for_cover_art_custom_path(self, tmp_path, monkeypatch):
        """Test providing custom cover path"""
        import main

        cover_file = tmp_path / "custom_cover.jpg"
        cover_file.write_bytes(b"image")

        inputs = ["y", str(cover_file)]
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        result = main.prompt_for_cover_art(str(tmp_path))

        assert result == str(cover_file)

    def test_prompt_for_cover_art_quoted_path(self, tmp_path, monkeypatch):
        """Test handling quoted paths"""
        import main

        cover_file = tmp_path / "cover.jpg"
        cover_file.write_bytes(b"image")

        # Need to provide "n" to skip the default cover.jpg prompt, then the quoted path
        inputs = ["y", "n", f'"{cover_file}"']
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        result = main.prompt_for_cover_art(str(tmp_path))

        assert result == str(cover_file)

    def test_prompt_for_cover_art_invalid_extension(self, tmp_path, monkeypatch):
        """Test invalid file extension"""
        import main

        invalid_file = tmp_path / "file.txt"
        invalid_file.write_text("not an image")

        # After invalid extension error, function loops back and asks for path again
        # We provide a non-existent path which triggers "Try again?" prompt, then "n"
        inputs = ["y", str(invalid_file), "/fake/path.jpg", "n"]
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.prompt_for_cover_art(str(tmp_path))

        assert result is None
        assert any("must be an image" in p for p in printed)

    def test_prompt_for_cover_art_file_not_found_retry_no(self, tmp_path, monkeypatch):
        """Test file not found with no retry"""
        import main

        inputs = ["y", "/fake/path.jpg", "n"]
        input_iter = iter(inputs)
        monkeypatch.setattr("main.input_colored", lambda prompt, color: next(input_iter))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        result = main.prompt_for_cover_art(str(tmp_path))

        assert result is None
        assert any("File not found" in p for p in printed)


class TestMainAdditional:
    """Test main function execution paths"""

    def test_main_no_voices(self, monkeypatch):
        """Test main when voices can't be loaded"""
        import main

        monkeypatch.setattr("main.load_voices", lambda: None)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        main.main()

        assert any("No voices available" in p for p in printed)

    def test_main_voice_selection_cancelled(self, monkeypatch):
        """Test main when voice selection is cancelled"""
        import main

        voices = {"English": {"US": {"female": {"Ava": "voice-111"}}}}
        monkeypatch.setattr("main.load_voices", lambda: voices)
        monkeypatch.setattr("main.select_voice_interactive", lambda v: (None, None))

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        main.main()

        assert any("Voice selection cancelled" in p for p in printed)

    def test_main_no_text_provided(self, monkeypatch):
        """Test main when no text is provided"""
        import main

        voices = {"English": {"US": {"female": {"Ava": "voice-111"}}}}
        monkeypatch.setattr("main.load_voices", lambda: voices)
        monkeypatch.setattr("main.select_voice_interactive", lambda v: ("voice-111", "Ava"))
        monkeypatch.setattr("main.get_multiline_input", lambda: "")

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        main.main()

        assert any("No text provided" in p for p in printed)

    def test_main_text_too_short(self, monkeypatch):
        """Test main when text is too short"""
        import main

        voices = {"English": {"US": {"female": {"Ava": "voice-111"}}}}
        monkeypatch.setattr("main.load_voices", lambda: voices)
        monkeypatch.setattr("main.select_voice_interactive", lambda v: ("voice-111", "Ava"))
        monkeypatch.setattr("main.get_multiline_input", lambda: "short")

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        main.main()

        assert any("must be more than 9 characters" in p for p in printed)

    def test_main_split_text_fails(self, monkeypatch):
        """Test main when text splitting fails"""
        import main

        voices = {"English": {"US": {"female": {"Ava": "voice-111"}}}}
        monkeypatch.setattr("main.load_voices", lambda: voices)
        monkeypatch.setattr("main.select_voice_interactive", lambda v: ("voice-111", "Ava"))
        monkeypatch.setattr("main.get_multiline_input", lambda: "Valid text here")
        monkeypatch.setattr("main.split_text", lambda text, chunk_size: [])

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        main.main()

        assert any("Could not split text into chunks" in p for p in printed)

    def test_main_successful_processing(self, tmp_path, monkeypatch):
        """Test main with successful processing"""
        import main

        voices = {"English": {"US": {"female": {"Ava": "voice-111"}}}}
        monkeypatch.setattr("main.load_voices", lambda: voices)
        monkeypatch.setattr("main.select_voice_interactive", lambda v: ("voice-111", "Ava"))
        monkeypatch.setattr("main.get_multiline_input", lambda: "This is a valid test message.")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "audio/mpeg"}
        mock_response.content = b"audio_data"
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr("main.req.post", lambda *args, **kwargs: mock_response)
        monkeypatch.setattr("main.prompt_graceful_exit", lambda: None)

        # Use temp path for audio output
        monkeypatch.setattr("os.path.join", lambda *args: str(tmp_path / "audio" / "chunk.mp3"))
        monkeypatch.setattr("os.path.exists", lambda path: False)
        monkeypatch.setattr("os.makedirs", lambda path: None)

        printed = []
        monkeypatch.setattr("main.print_colored", lambda text, color: printed.append(text))

        files_written = []

        def mock_file_write(path, mode):
            files_written.append(path)
            return mock_open()(path, mode)

        monkeypatch.setattr("builtins.open", mock_file_write)

        main.main()

        assert any("Processing chunk" in p for p in printed)
