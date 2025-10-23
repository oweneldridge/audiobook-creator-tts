"""
Unit tests for worker_browser.py
Tests for WorkerBrowser class and parallel worker functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock


class TestWorkerBrowserInit:
    """Tests for WorkerBrowser initialization"""

    def test_init_basic(self):
        """Test basic initialization"""
        from worker_browser import WorkerBrowser

        worker = WorkerBrowser(worker_id=5)

        assert worker.worker_id == 5
        assert worker.profile_dir == "/tmp/audiobook-worker-5"
        assert worker.assigned_chunks == []
        assert worker.completed_chunks == []
        assert worker.failed_chunks == []
        assert worker.worker_request_count == 0
        assert worker.worker_success_count == 0

    def test_init_custom_profile_dir(self):
        """Test initialization with custom profile directory"""
        from worker_browser import WorkerBrowser

        worker = WorkerBrowser(worker_id=3, profile_dir="/custom/path")

        assert worker.worker_id == 3
        assert worker.profile_dir == "/custom/path"


class TestChunkAssignment:
    """Tests for chunk assignment"""

    def test_assign_chunks(self, monkeypatch):
        """Test assigning chunks to worker"""
        from worker_browser import WorkerBrowser

        # Mock print_colored
        printed = []
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: printed.append(text))

        worker = WorkerBrowser(worker_id=1)
        chunks = [(1, "chunk1"), (2, "chunk2"), (3, "chunk3")]

        worker.assign_chunks(chunks)

        assert worker.assigned_chunks == chunks
        assert any("Assigned 3 chunks" in p for p in printed)

    def test_assign_empty_chunks(self, monkeypatch):
        """Test assigning empty chunk list"""
        from worker_browser import WorkerBrowser

        printed = []
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: printed.append(text))

        worker = WorkerBrowser(worker_id=2)
        worker.assign_chunks([])

        assert worker.assigned_chunks == []
        assert any("Assigned 0 chunks" in p for p in printed)


@pytest.mark.asyncio
class TestWorkerInitialization:
    """Tests for async worker initialization"""

    async def test_initialize_creates_profile_dir(self, tmp_path):
        """Test that initialization creates profile directory"""
        from worker_browser import WorkerBrowser

        profile_dir = str(tmp_path / "worker-test")

        # Mock playwright and browser components
        mock_playwright = MagicMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.evaluate = AsyncMock()
        mock_page.add_init_script = AsyncMock()
        mock_context.pages = []
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.chromium.launch_persistent_context = AsyncMock(return_value=mock_context)

        async_playwright_mock = AsyncMock()
        async_playwright_mock.start = AsyncMock(return_value=mock_playwright)

        worker = WorkerBrowser(worker_id=1, profile_dir=profile_dir)

        # Patch async_playwright where it's imported (inside the initialize method)
        with patch("playwright.async_api.async_playwright", return_value=async_playwright_mock):
            with patch("worker_browser.print_timestamped"):
                with patch("worker_browser.print_colored"):
                    await worker.initialize(skip_initial_captcha_prompt=True)

        assert worker.playwright is not None
        assert worker.context is not None
        assert worker.page is not None

    async def test_initialize_skips_captcha_prompt(self):
        """Test initialization with skip_initial_captcha_prompt=True"""
        from worker_browser import WorkerBrowser

        # Mock all the async components
        mock_playwright = MagicMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.evaluate = AsyncMock()
        mock_page.add_init_script = AsyncMock()
        mock_context.pages = [mock_page]
        mock_playwright.chromium.launch_persistent_context = AsyncMock(return_value=mock_context)

        async_playwright_mock = AsyncMock()
        async_playwright_mock.start = AsyncMock(return_value=mock_playwright)

        printed = []

        worker = WorkerBrowser(worker_id=1)

        # Patch async_playwright where it's imported (inside the initialize method)
        with patch("playwright.async_api.async_playwright", return_value=async_playwright_mock):
            with patch("worker_browser.print_timestamped"):
                with patch("worker_browser.print_colored", side_effect=lambda text, color: printed.append(text)):
                    await worker.initialize(skip_initial_captcha_prompt=True)

        assert any("Skipping initial CAPTCHA prompt" in p for p in printed)
        assert worker.captcha_solved is True
        assert worker.requests_since_captcha == 0


@pytest.mark.asyncio
class TestChunkProcessing:
    """Tests for chunk processing"""

    async def test_process_assigned_chunks_success(self, monkeypatch, tmp_path):
        """Test successful chunk processing"""
        from worker_browser import WorkerBrowser

        # Mock print functions
        monkeypatch.setattr("worker_browser.print_timestamped", lambda msg, color: None)
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: None)

        # Mock request_audio to return success
        async def mock_request_audio(text, voice_id):
            return b"audio_data"

        worker = WorkerBrowser(worker_id=1)
        worker.request_audio = mock_request_audio
        worker.assign_chunks([(1, "test chunk 1"), (2, "test chunk 2")])

        output_dir = str(tmp_path)
        result = await worker.process_assigned_chunks(
            voice_id="voice-1", output_dir=output_dir, chapter_dir_name="01-chapter", chapter_number=1
        )

        assert result["worker_id"] == 1
        assert result["completed"] == [1, 2]
        assert result["failed"] == []
        assert result["success_count"] == 2
        assert result["failure_count"] == 0

    async def test_process_assigned_chunks_with_failures(self, monkeypatch, tmp_path):
        """Test chunk processing with some failures"""
        from worker_browser import WorkerBrowser

        monkeypatch.setattr("worker_browser.print_timestamped", lambda msg, color: None)
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: None)

        # Mock request_audio to fail on chunk 2
        call_count = [0]

        async def mock_request_audio(text, voice_id):
            call_count[0] += 1
            if "chunk 2" in text:
                return None  # Failure
            return b"audio_data"

        worker = WorkerBrowser(worker_id=1)
        worker.request_audio = mock_request_audio
        worker.assign_chunks([(1, "test chunk 1"), (2, "test chunk 2"), (3, "test chunk 3")])

        result = await worker.process_assigned_chunks(
            voice_id="voice-1", output_dir=str(tmp_path), chapter_dir_name="01-chapter", chapter_number=1
        )

        assert result["worker_id"] == 1
        assert len(result["completed"]) == 2
        assert len(result["failed"]) == 1
        assert 2 in result["failed"]

    async def test_process_assigned_chunks_rate_limit(self, monkeypatch, tmp_path):
        """Test handling of rate limit response"""
        from worker_browser import WorkerBrowser

        monkeypatch.setattr("worker_browser.print_timestamped", lambda msg, color: None)
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: None)

        # Mock request_audio to return RATE_LIMIT
        async def mock_request_audio(text, voice_id):
            return "RATE_LIMIT"

        # Mock restart method
        restart_called = [False]

        async def mock_restart():
            restart_called[0] = True

        worker = WorkerBrowser(worker_id=1)
        worker.request_audio = mock_request_audio
        worker.restart = mock_restart
        worker.assign_chunks([(1, "test chunk 1")])

        result = await worker.process_assigned_chunks(
            voice_id="voice-1", output_dir=str(tmp_path), chapter_dir_name="01-chapter", chapter_number=1
        )

        assert restart_called[0] is True


@pytest.mark.asyncio
class TestCleanup:
    """Tests for worker cleanup"""

    async def test_cleanup_success(self, monkeypatch):
        """Test successful cleanup"""
        from worker_browser import WorkerBrowser

        monkeypatch.setattr("worker_browser.print_timestamped", lambda msg, color: None)

        worker = WorkerBrowser(worker_id=1)

        # Mock context and playwright
        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        worker.context = mock_context

        mock_playwright = AsyncMock()
        mock_playwright.stop = AsyncMock()
        worker.playwright = mock_playwright

        await worker.cleanup()

        mock_context.close.assert_called_once()
        mock_playwright.stop.assert_called_once()

    async def test_cleanup_no_context(self, monkeypatch):
        """Test cleanup when context doesn't exist"""
        from worker_browser import WorkerBrowser

        monkeypatch.setattr("worker_browser.print_timestamped", lambda msg, color: None)

        worker = WorkerBrowser(worker_id=1)
        worker.playwright = None

        # Should not raise error
        await worker.cleanup()


class TestCaptchaNotification:
    """Tests for CAPTCHA notification"""

    @pytest.mark.asyncio
    async def test_display_captcha_notification(self, monkeypatch, tmp_path):
        """Test CAPTCHA notification display"""
        from worker_browser import WorkerBrowser

        printed = []
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: printed.append(text))

        # Mock page screenshot
        mock_page = AsyncMock()
        screenshot_path = str(tmp_path / "screenshot.png")
        mock_page.screenshot = AsyncMock(return_value=None)

        # Mock subprocess for screenshot and notification
        monkeypatch.setattr("subprocess.run", Mock(return_value=Mock(returncode=0)))

        # Mock tempfile
        monkeypatch.setattr("tempfile.mktemp", lambda suffix: screenshot_path)

        worker = WorkerBrowser(worker_id=3)
        worker.page = mock_page
        worker.request_count = 55
        worker.requests_since_captcha = 55
        worker.completed_chunks = [1, 2, 3]
        worker.assigned_chunks = [(1, "a"), (2, "b"), (3, "c"), (4, "d"), (5, "e")]

        await worker.display_captcha_notification()

        # Verify notification was displayed
        assert any("WORKER #3 - CAPTCHA REQUIRED" in p for p in printed)
        assert any("Worker #3 Stats:" in p for p in printed)


class TestPrintTimestamped:
    """Tests for timestamp print function"""

    def test_print_timestamped(self, monkeypatch):
        """Test timestamped printing"""
        from worker_browser import print_timestamped

        printed = []
        monkeypatch.setattr("worker_browser.print_colored", lambda text, color: printed.append(text))

        print_timestamped("Test message", "cyan")

        assert len(printed) == 1
        assert "Test message" in printed[0]
        assert "[" in printed[0]  # Has timestamp
        assert "]" in printed[0]
