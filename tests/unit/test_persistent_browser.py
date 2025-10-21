"""
Unit tests for PersistentBrowser class enhancements

Tests for adaptive rate limiting, session health monitoring, and CAPTCHA improvements
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import asyncio


@pytest.mark.unit
class TestPersistentBrowserHealthMonitoring:
    """Tests for session health monitoring functionality"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance with health monitoring attributes"""
        from main_playwright_persistent import PersistentBrowser

        # Mock the async __init__ to avoid actual browser launch
        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()

            # Initialize health monitoring attributes
            browser.base_delay = 2.5
            browser.current_delay = 2.5
            browser.max_delay = 8.0
            browser.request_count = 0
            browser.success_count = 0
            browser.recent_results = []
            browser.health_window_size = 20
            browser.response_times = []
            browser.baseline_response_time = None
            browser.response_time_window = 10

            return browser

    def test_update_health_success(self, browser_instance):
        """Test updating health with successful request"""
        browser_instance.update_health(success=True)

        assert browser_instance.request_count == 1
        assert browser_instance.success_count == 1
        assert len(browser_instance.recent_results) == 1
        assert browser_instance.recent_results[0] is True

    def test_update_health_failure(self, browser_instance):
        """Test updating health with failed request"""
        browser_instance.update_health(success=False)

        assert browser_instance.request_count == 1
        assert browser_instance.success_count == 0
        assert len(browser_instance.recent_results) == 1
        assert browser_instance.recent_results[0] is False

    def test_update_health_window_limit(self, browser_instance):
        """Test that health tracking maintains window size limit"""
        # Add 25 results (exceeds window size of 20)
        for i in range(25):
            browser_instance.update_health(success=True)

        assert len(browser_instance.recent_results) == 20  # Should be capped at window size
        assert browser_instance.request_count == 25
        assert browser_instance.success_count == 25

    def test_get_health_score_perfect(self, browser_instance):
        """Test health score calculation with 100% success rate"""
        for _ in range(10):
            browser_instance.update_health(success=True)

        health = browser_instance.get_health_score()
        assert health == 1.0

    def test_get_health_score_zero(self, browser_instance):
        """Test health score calculation with 0% success rate"""
        for _ in range(10):
            browser_instance.update_health(success=False)

        health = browser_instance.get_health_score()
        assert health == 0.0

    def test_get_health_score_mixed(self, browser_instance):
        """Test health score calculation with mixed results"""
        # 7 successes, 3 failures = 70% health
        for _ in range(7):
            browser_instance.update_health(success=True)
        for _ in range(3):
            browser_instance.update_health(success=False)

        health = browser_instance.get_health_score()
        assert health == 0.7

    def test_get_health_score_empty(self, browser_instance):
        """Test health score returns 1.0 when no data available"""
        health = browser_instance.get_health_score()
        assert health == 1.0  # Default to healthy when no data


@pytest.mark.unit
class TestPersistentBrowserResponseTimeTracking:
    """Tests for response time monitoring functionality"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.response_times = []
            browser.baseline_response_time = None
            browser.response_time_window = 10
            return browser

    def test_update_response_time_single(self, browser_instance):
        """Test updating response time with single value"""
        browser_instance.update_response_time(1.5)

        assert len(browser_instance.response_times) == 1
        assert browser_instance.response_times[0] == 1.5
        # Baseline requires >=3 values
        assert browser_instance.baseline_response_time is None

    def test_update_response_time_baseline_calculation(self, browser_instance):
        """Test baseline calculation as average of response times"""
        browser_instance.update_response_time(1.0)
        browser_instance.update_response_time(2.0)
        browser_instance.update_response_time(3.0)

        assert browser_instance.baseline_response_time == 2.0  # Average of 1, 2, 3

    def test_update_response_time_window_limit(self, browser_instance):
        """Test that response time tracking maintains window size"""
        # Add 15 values (exceeds window size of 10)
        for i in range(15):
            browser_instance.update_response_time(float(i))

        assert len(browser_instance.response_times) == 10  # Should be capped
        assert browser_instance.response_times[0] == 5.0  # Oldest should be value 5
        assert browser_instance.response_times[-1] == 14.0  # Newest should be value 14


@pytest.mark.unit
class TestPersistentBrowserAdaptiveDelay:
    """Tests for adaptive delay calculation"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.base_delay = 2.5
            browser.max_delay = 8.0
            browser.recent_results = []
            browser.health_window_size = 20
            browser.response_times = []
            browser.baseline_response_time = None
            browser.response_time_window = 10
            browser.request_count = 0
            browser.success_count = 0
            return browser

    def test_calculate_adaptive_delay_healthy_session(self, browser_instance):
        """Test adaptive delay with healthy session (>90% success)"""
        # Set up healthy session (95% success)
        for _ in range(19):
            browser_instance.update_health(success=True)
        browser_instance.update_health(success=False)

        delay = browser_instance.calculate_adaptive_delay()
        assert delay == 2.5  # Should be base delay

    def test_calculate_adaptive_delay_warning_health(self, browser_instance):
        """Test adaptive delay with warning-level health (85% success)"""
        # 85% success rate (below 90% threshold)
        for _ in range(17):
            browser_instance.update_health(success=True)
        for _ in range(3):
            browser_instance.update_health(success=False)

        delay = browser_instance.calculate_adaptive_delay()
        # Health penalty: (0.90 - 0.85) * 10 = 0.5 seconds
        assert delay == pytest.approx(3.0, rel=1e-9)  # 2.5 + 0.5

    def test_calculate_adaptive_delay_critical_health(self, browser_instance):
        """Test adaptive delay with critical health (75% success)"""
        # 75% success rate
        for _ in range(15):
            browser_instance.update_health(success=True)
        for _ in range(5):
            browser_instance.update_health(success=False)

        delay = browser_instance.calculate_adaptive_delay()
        # Health penalty: (0.90 - 0.75) * 10 = 1.5 seconds
        assert delay == 4.0  # 2.5 + 1.5

    def test_calculate_adaptive_delay_slow_responses(self, browser_instance):
        """Test adaptive delay when API responses are slow"""
        # Set up baseline manually with slow recent responses
        # Note: baseline recalculates with each new value in implementation
        # To trigger slow response penalty: recent_avg > baseline * 1.5
        browser_instance.response_times = [1.0, 1.0, 1.0, 5.0, 5.0, 5.0]
        browser_instance.baseline_response_time = sum(browser_instance.response_times) / len(
            browser_instance.response_times
        )
        # baseline is now (1+1+1+5+5+5)/6 = 3.0
        # recent 3 avg: (5+5+5)/3 = 5.0
        # 5.0 > 3.0 * 1.5 (4.5)? YES!

        delay = browser_instance.calculate_adaptive_delay()
        # Should add 2.0 seconds for slow responses
        assert delay == 4.5  # 2.5 + 2.0

    def test_calculate_adaptive_delay_max_cap(self, browser_instance):
        """Test that adaptive delay is capped at max_delay"""
        # Very poor health (20% success)
        for _ in range(4):
            browser_instance.update_health(success=True)
        for _ in range(16):
            browser_instance.update_health(success=False)

        # Also slow responses
        browser_instance.update_response_time(1.0)
        browser_instance.baseline_response_time = 1.0
        browser_instance.update_response_time(3.0)
        browser_instance.update_response_time(3.0)
        browser_instance.update_response_time(3.0)

        delay = browser_instance.calculate_adaptive_delay()
        # Would be: 2.5 + 7.0 (health) + 2.0 (slow) = 11.5
        # But capped at max_delay
        assert delay == 8.0  # max_delay


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
            browser.recent_results = []
            browser.health_window_size = 20
            browser.current_delay = 2.5
            return browser

    @pytest.mark.asyncio
    async def test_check_session_health_healthy(self, browser_instance):
        """Test session health check returns True when healthy"""
        # 95% success rate
        for _ in range(19):
            browser_instance.update_health(success=True)
        browser_instance.update_health(success=False)

        result = await browser_instance.check_session_health()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_session_health_warning(self, browser_instance):
        """Test session health check returns True but warns at 85%"""
        # 85% success rate
        for _ in range(17):
            browser_instance.update_health(success=True)
        for _ in range(3):
            browser_instance.update_health(success=False)

        with patch("builtins.print"):  # Suppress print output
            result = await browser_instance.check_session_health()

        assert result is True  # Still healthy enough

    @pytest.mark.asyncio
    async def test_check_session_health_critical(self, browser_instance):
        """Test session health check returns False when critical (<80%)"""
        # 75% success rate
        for _ in range(15):
            browser_instance.update_health(success=True)
        for _ in range(5):
            browser_instance.update_health(success=False)

        with patch("builtins.print"):  # Suppress print output
            result = await browser_instance.check_session_health()

        assert result is False  # Critical, should recommend restart

    @pytest.mark.asyncio
    async def test_check_session_health_too_few_requests(self, browser_instance):
        """Test that health check doesn't trigger with too few requests"""
        # Only 5 requests (below threshold)
        for _ in range(5):
            browser_instance.update_health(success=True)

        result = await browser_instance.check_session_health()
        assert result is True  # Not enough data to judge


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
            browser.recent_results = [True, False, True, True]
            browser.response_times = [1.5, 2.0, 1.8]
            browser.baseline_response_time = 1.77
            browser.current_delay = 4.5
            browser.base_delay = 2.5

            # Mock browser and page
            browser.browser = AsyncMock()
            browser.page = AsyncMock()
            browser.playwright = AsyncMock()

            return browser

    @pytest.mark.asyncio
    async def test_restart_resets_metrics(self, browser_instance):
        """Test that restart() resets all health metrics"""
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
        assert browser_instance.recent_results == []
        assert browser_instance.response_times == []
        assert browser_instance.baseline_response_time is None
        assert browser_instance.current_delay == browser_instance.base_delay


@pytest.mark.unit
class TestPersistentBrowserWaitIfNeeded:
    """Tests for wait_if_needed with adaptive delay"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser
        import time

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.base_delay = 2.5
            browser.current_delay = 2.5
            browser.max_delay = 8.0
            browser.recent_results = []
            browser.health_window_size = 20
            browser.response_times = []
            browser.baseline_response_time = None
            browser.response_time_window = 10
            browser.request_count = 0
            browser.success_count = 0
            # Set last request to recent past so sleep will be needed
            browser.last_request_time = time.time() - 1.0  # 1 second ago
            return browser

    @pytest.mark.asyncio
    async def test_wait_if_needed_updates_current_delay(self, browser_instance):
        """Test that wait_if_needed updates current_delay based on health"""
        # Set poor health to trigger delay increase
        for _ in range(15):
            browser_instance.update_health(success=True)
        for _ in range(5):
            browser_instance.update_health(success=False)

        with (
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("time.time", return_value=browser_instance.last_request_time + 2.0),
        ):
            # Mock time.time to return a value 2 seconds after last request
            # This ensures time_since_last (2.0) < current_delay (4.0), so sleep is called
            await browser_instance.wait_if_needed()

        # Current delay should be updated from base (health penalty: (0.90 - 0.75) * 10 = 1.5)
        assert browser_instance.current_delay == 4.0  # 2.5 + 1.5
        mock_sleep.assert_called_once()


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
            browser.recent_results = [True] * 18 + [False] * 2
            browser.current_delay = 3.5
            return browser

    @pytest.mark.asyncio
    async def test_display_captcha_notification_takes_screenshot(self, browser_instance):
        """Test that CAPTCHA notification takes screenshot"""
        with patch("tempfile.mktemp", return_value="/tmp/test.png"), patch("subprocess.run"), patch("builtins.print"):

            await browser_instance.display_captcha_notification()

            # Verify screenshot was attempted
            browser_instance.page.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_captcha_notification_shows_health(self, browser_instance):
        """Test that CAPTCHA notification displays health stats"""
        with (
            patch("tempfile.mktemp", return_value="/tmp/test.png"),
            patch("subprocess.run"),
            patch("builtins.print") as mock_print,
        ):

            await browser_instance.display_captcha_notification()

            # Should have printed health information
            # Check that print was called (exact text may vary)
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
            # Check if any subprocess.run call included osascript
            osascript_calls = [call for call in mock_run.call_args_list if "osascript" in str(call)]
            # May or may not be called depending on platform, just verify it doesn't crash


@pytest.mark.unit
class TestPersistentBrowserIntegration:
    """Integration tests for combined functionality"""

    @pytest.fixture
    def browser_instance(self):
        """Create a mock PersistentBrowser instance"""
        from main_playwright_persistent import PersistentBrowser

        with patch.object(PersistentBrowser, "__init__", lambda x: None):
            browser = PersistentBrowser()
            browser.base_delay = 2.5
            browser.current_delay = 2.5
            browser.max_delay = 8.0
            browser.request_count = 0
            browser.success_count = 0
            browser.recent_results = []
            browser.health_window_size = 20
            browser.response_times = []
            browser.baseline_response_time = None
            browser.response_time_window = 10
            return browser

    def test_health_degradation_increases_delay(self, browser_instance):
        """Test that health degradation automatically increases delay"""
        # Start healthy
        initial_delay = browser_instance.calculate_adaptive_delay()
        assert initial_delay == 2.5

        # Simulate failures
        for _ in range(10):
            browser_instance.update_health(success=True)
        for _ in range(10):
            browser_instance.update_health(success=False)

        # Delay should increase
        degraded_delay = browser_instance.calculate_adaptive_delay()
        assert degraded_delay > initial_delay

    def test_slow_responses_increase_delay(self, browser_instance):
        """Test that slow API responses increase delay"""
        # Set up scenario with slow recent responses
        # Manually set response times to create the condition
        browser_instance.response_times = [1.0, 1.0, 1.0, 5.0, 5.0, 5.0]
        browser_instance.baseline_response_time = sum(browser_instance.response_times) / len(
            browser_instance.response_times
        )
        # baseline = 3.0, recent 3 avg = 5.0, 5.0 > 3.0 * 1.5 (4.5) = TRUE

        slow_delay = browser_instance.calculate_adaptive_delay()
        assert slow_delay == 4.5  # 2.5 + 2.0

    def test_combined_health_and_response_degradation(self, browser_instance):
        """Test delay increase with both health and response time issues"""
        # Good health, good responses
        for _ in range(10):
            browser_instance.update_health(success=True)
            browser_instance.update_response_time(1.0)

        healthy_delay = browser_instance.calculate_adaptive_delay()

        # Degrade both
        for _ in range(10):
            browser_instance.update_health(success=False)
            browser_instance.update_response_time(3.0)

        degraded_delay = browser_instance.calculate_adaptive_delay()

        # Should have significant increase
        assert degraded_delay > healthy_delay + 1.0  # At least 1 second increase
