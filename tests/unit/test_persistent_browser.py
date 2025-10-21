"""
Unit tests for PersistentBrowser class

Tests for simplified rate limiting with proactive CAPTCHA handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import asyncio


@pytest.mark.unit
class TestPersistentBrowserBasics:
    """Tests for basic request tracking functionality"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        # Mock the async __init__ to avoid actual browser launch
        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()

            # Initialize simplified attributes
            browser.base_delay = 2.0
            browser.request_count = 0
            browser.success_count = 0
            browser.requests_since_captcha = 0
            browser.captcha_request_limit = 55
            browser.last_request_time = 0

            return browser

    def test_update_health_success(self, browser_instance):
        """Test updating counters with successful request"""
        browser_instance.update_health(success=True)

        assert browser_instance.request_count == 1
        assert browser_instance.success_count == 1
        assert browser_instance.requests_since_captcha == 1

    def test_update_health_failure(self, browser_instance):
        """Test updating counters with failed request"""
        browser_instance.update_health(success=False)

        assert browser_instance.request_count == 1
        assert browser_instance.success_count == 0
        # requests_since_captcha only increments on success
        assert browser_instance.requests_since_captcha == 0

    def test_update_health_multiple_successes(self, browser_instance):
        """Test counter tracking over multiple successful requests"""
        for _ in range(10):
            browser_instance.update_health(success=True)

        assert browser_instance.request_count == 10
        assert browser_instance.success_count == 10
        assert browser_instance.requests_since_captcha == 10


@pytest.mark.unit
class TestPersistentBrowserProactiveCaptcha:
    """Tests for proactive CAPTCHA handling at 60-request limit"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.requests_since_captcha = 0
            browser.captcha_request_limit = 55
            browser.page = AsyncMock()
            browser.request_count = 0
            browser.success_count = 0
            return browser

    @pytest.mark.asyncio
    async def test_check_and_handle_captcha_limit_below_threshold(self, browser_instance):
        """Test that CAPTCHA check does nothing when below threshold"""
        browser_instance.requests_since_captcha = 50  # Below 55 limit

        # Should not prompt for CAPTCHA
        with patch("builtins.input") as mock_input:
            await browser_instance.check_and_handle_captcha_limit()
            mock_input.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_and_handle_captcha_limit_at_threshold(self, browser_instance):
        """Test that CAPTCHA check prompts when at threshold"""
        browser_instance.requests_since_captcha = 55  # At limit

        with (
            patch("builtins.input") as mock_input,
            patch.object(browser_instance, "display_captcha_notification", new_callable=AsyncMock),
            patch("builtins.print"),
        ):
            await browser_instance.check_and_handle_captcha_limit()

            # Should have prompted for CAPTCHA
            mock_input.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_and_handle_captcha_limit_resets_counter(self, browser_instance):
        """Test that counter resets after CAPTCHA solved"""
        browser_instance.requests_since_captcha = 55

        with (
            patch("builtins.input"),
            patch.object(browser_instance, "display_captcha_notification", new_callable=AsyncMock),
            patch("builtins.print"),
        ):
            await browser_instance.check_and_handle_captcha_limit()

            # Counter should be reset
            assert browser_instance.requests_since_captcha == 0

    @pytest.mark.asyncio
    async def test_check_and_handle_captcha_limit_above_threshold(self, browser_instance):
        """Test CAPTCHA handling when above threshold (edge case)"""
        browser_instance.requests_since_captcha = 60  # Above limit

        with (
            patch("builtins.input") as mock_input,
            patch.object(browser_instance, "display_captcha_notification", new_callable=AsyncMock),
            patch("builtins.print"),
        ):
            await browser_instance.check_and_handle_captcha_limit()

            # Should have prompted
            mock_input.assert_called_once()
            assert browser_instance.requests_since_captcha == 0


@pytest.mark.unit
class TestPersistentBrowserSessionHealthCheck:
    """Tests for check_session_health method"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.request_count = 0
            browser.success_count = 0
            return browser

    @pytest.mark.asyncio
    async def test_check_session_health_always_returns_true(self, browser_instance):
        """Test that simplified health check always returns True"""
        # Simplified version always returns True (compatibility stub)
        result = await browser_instance.check_session_health()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_session_health_with_failures(self, browser_instance):
        """Test health check still returns True even with failures"""
        # Add some failures
        for _ in range(20):
            browser_instance.update_health(success=False)

        result = await browser_instance.check_session_health()
        assert result is True  # Simplified version always returns True


@pytest.mark.unit
class TestPersistentBrowserRestart:
    """Tests for browser restart and metric reset"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance with populated metrics"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()

            # Set up some metrics
            browser.request_count = 50
            browser.success_count = 40
            browser.requests_since_captcha = 35
            browser.base_delay = 2.0

            # Mock browser and page
            browser.browser = AsyncMock()
            browser.page = AsyncMock()
            browser.playwright = AsyncMock()

            return browser

    @pytest.mark.asyncio
    async def test_restart_resets_metrics(self, browser_instance):
        """Test that restart() resets all counters"""
        # Mock initialize and cleanup to avoid actual browser operations
        with (
            patch.object(browser_instance, "initialize", new_callable=AsyncMock),
            patch.object(browser_instance, "cleanup", new_callable=AsyncMock),
            patch("builtins.print"),
        ):  # Suppress print output

            await browser_instance.restart()

        # Check that all metrics are reset
        assert browser_instance.request_count == 0
        assert browser_instance.success_count == 0
        assert browser_instance.requests_since_captcha == 0


@pytest.mark.unit
class TestPersistentBrowserWaitIfNeeded:
    """Tests for wait_if_needed with simple delay"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser
        import time

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.base_delay = 2.0
            browser.request_count = 0
            browser.success_count = 0
            # Set last request to recent past so sleep will be needed
            browser.last_request_time = time.time() - 1.0  # 1 second ago
            return browser

    @pytest.mark.asyncio
    async def test_wait_if_needed_sleeps_when_too_soon(self, browser_instance):
        """Test that wait_if_needed sleeps when time since last request is too short"""
        import time

        with (
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("time.time", return_value=browser_instance.last_request_time + 1.0),
        ):
            # Mock time.time to return a value 1 second after last request
            # This ensures time_since_last (1.0) < base_delay (2.0), so sleep is called
            await browser_instance.wait_if_needed()

        # Should sleep for remaining time: 2.0 - 1.0 = 1.0 second
        mock_sleep.assert_called_once()
        call_args = mock_sleep.call_args[0]
        assert abs(call_args[0] - 1.0) < 0.01  # Allow small floating point error

    @pytest.mark.asyncio
    async def test_wait_if_needed_no_sleep_when_enough_time_passed(self, browser_instance):
        """Test that wait_if_needed doesn't sleep when enough time has passed"""
        import time

        with (
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("time.time", return_value=browser_instance.last_request_time + 3.0),
        ):
            # Mock time.time to return a value 3 seconds after last request
            # This is >= base_delay (2.0), so no sleep needed
            await browser_instance.wait_if_needed()

        # Should not sleep
        mock_sleep.assert_not_called()


@pytest.mark.unit
class TestPersistentBrowserCaptchaNotification:
    """Tests for CAPTCHA notification display"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance with page"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.page = AsyncMock()
            browser.request_count = 50
            browser.success_count = 45
            browser.requests_since_captcha = 45
            return browser

    @pytest.mark.asyncio
    async def test_display_captcha_notification_takes_screenshot(self, browser_instance):
        """Test that CAPTCHA notification takes screenshot"""
        with patch("tempfile.mktemp", return_value="/tmp/test.png"), patch("subprocess.run"), patch("builtins.print"):

            await browser_instance.display_captcha_notification()

            # Verify screenshot was attempted
            browser_instance.page.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_captcha_notification_shows_stats(self, browser_instance):
        """Test that CAPTCHA notification displays session stats"""
        with (
            patch("tempfile.mktemp", return_value="/tmp/test.png"),
            patch("subprocess.run"),
            patch("builtins.print") as mock_print,
        ):

            await browser_instance.display_captcha_notification()

            # Should have printed stats
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_display_captcha_notification_sends_macos_notification(self, browser_instance):
        """Test that macOS notification is sent"""
        with (
            patch("tempfile.mktemp", return_value="/tmp/test.png"),
            patch("subprocess.run") as mock_run,
            patch("builtins.print"),
        ):

            await browser_instance.display_captcha_notification()

            # Should attempt to run osascript for macOS notification
            # Just verify it doesn't crash (platform-dependent)
            # Check if subprocess.run was called at all
            assert mock_run.called


@pytest.mark.unit
class TestPersistentBrowserIntegration:
    """Integration tests for request flow with proactive CAPTCHA"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.base_delay = 2.0
            browser.request_count = 0
            browser.success_count = 0
            browser.requests_since_captcha = 0
            browser.captcha_request_limit = 55
            browser.last_request_time = 0
            return browser

    def test_request_counter_increments_properly(self, browser_instance):
        """Test that counters increment properly through multiple requests"""
        # Simulate 60 successful requests
        for _ in range(60):
            browser_instance.update_health(success=True)

        assert browser_instance.request_count == 60
        assert browser_instance.success_count == 60
        assert browser_instance.requests_since_captcha == 60

    def test_captcha_limit_detection(self, browser_instance):
        """Test that CAPTCHA limit is properly detected"""
        # Simulate requests up to limit
        for _ in range(54):
            browser_instance.update_health(success=True)

        assert browser_instance.requests_since_captcha == 54
        assert browser_instance.requests_since_captcha < browser_instance.captcha_request_limit

        # One more pushes to limit
        browser_instance.update_health(success=True)
        assert browser_instance.requests_since_captcha >= browser_instance.captcha_request_limit

    @pytest.mark.asyncio
    async def test_full_request_cycle_with_captcha(self, browser_instance):
        """Test full cycle: requests → CAPTCHA prompt → reset → continue"""
        # Simulate 54 requests (below limit)
        for _ in range(54):
            browser_instance.update_health(success=True)

        # One more triggers CAPTCHA check (55 total)
        browser_instance.update_health(success=True)
        assert browser_instance.requests_since_captcha == 55

        # Simulate CAPTCHA solve
        with (
            patch("builtins.input"),
            patch.object(browser_instance, "display_captcha_notification", new_callable=AsyncMock),
            patch("builtins.print"),
        ):
            await browser_instance.check_and_handle_captcha_limit()

        # Counter should be reset
        assert browser_instance.requests_since_captcha == 0

        # Can continue making requests
        for _ in range(10):
            browser_instance.update_health(success=True)

        assert browser_instance.requests_since_captcha == 10
        assert browser_instance.success_count == 65  # 55 + 10
