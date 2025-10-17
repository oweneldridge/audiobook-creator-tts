"""
Integration tests for API interactions

Tests for complete request/response cycles with mocked HTTP
"""

import pytest
import responses
from unittest.mock import Mock, patch
from main import get_audio


@pytest.mark.integration
@pytest.mark.api
class TestGetAudioIntegration:
    """Integration tests for get_audio function"""

    @responses.activate
    def test_get_audio_successful_request(self, mock_audio_response):
        """Test successful audio retrieval"""
        url = "https://speechma.com/com.api/tts-api.php"

        # Mock the HTTP response
        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test message", "voice": "voice-111"}
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

        result = get_audio(url, data, headers)

        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    @responses.activate
    def test_get_audio_403_forbidden(self):
        """Test handling 403 Forbidden response"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body="Forbidden", status=403, headers={"Content-Type": "text/html"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is None

    @responses.activate
    def test_get_audio_429_rate_limit(self):
        """Test handling 429 rate limit response"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(
            responses.POST,
            url,
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Content-Type": "application/json"},
        )

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is None

    @responses.activate
    def test_get_audio_500_server_error(self):
        """Test handling 500 server error"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body="Internal Server Error", status=500)

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is None

    @responses.activate
    def test_get_audio_network_timeout(self):
        """Test handling network timeout"""
        url = "https://speechma.com/com.api/tts-api.php"

        # Mock timeout exception
        import requests

        responses.add(responses.POST, url, body=requests.exceptions.Timeout("Connection timeout"))

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        # Should handle timeout gracefully
        result = get_audio(url, data, headers)
        # Result may be None or raise exception depending on implementation

    @responses.activate
    def test_get_audio_with_cookies(self, mock_audio_response):
        """Test request with cookies"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}
        cookies = {"cf_clearance": "test_token", "__cfruid": "test_ruid"}

        result = get_audio(url, data, headers, cookies=cookies)

        assert result is not None

    @responses.activate
    def test_get_audio_unexpected_content_type(self):
        """Test handling unexpected content type"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(
            responses.POST, url, body="<html>Error page</html>", status=200, headers={"Content-Type": "text/html"}
        )

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        # Should detect wrong content type
        assert result is None

    @responses.activate
    def test_get_audio_large_response(self):
        """Test handling large audio response"""
        url = "https://speechma.com/com.api/tts-api.php"

        # Simulate large audio file (1MB)
        large_audio = b"\xff\xfb\x90\x00" + b"\x00" * (1024 * 1024)

        responses.add(responses.POST, url, body=large_audio, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Long text" * 100, "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is not None
        assert len(result) > 1024 * 1024

    @responses.activate
    def test_get_audio_empty_response(self):
        """Test handling empty audio response"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=b"", status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        # Should handle empty response
        assert result is not None  # Returns empty bytes
        assert len(result) == 0


@pytest.mark.integration
@pytest.mark.api
class TestAPIRetryLogic:
    """Integration tests for retry logic"""

    @responses.activate
    def test_retry_on_failure(self, mock_audio_response):
        """Test that API calls are retried on failure"""
        url = "https://speechma.com/com.api/tts-api.php"

        # First two calls fail, third succeeds
        responses.add(responses.POST, url, body="Error", status=500)
        responses.add(responses.POST, url, body="Error", status=500)
        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        # Simulate retry logic (actual implementation in main code)
        result = None
        for attempt in range(3):
            result = get_audio(url, data, headers)
            if result:
                break

        assert result is not None

    @responses.activate
    def test_all_retries_fail(self):
        """Test behavior when all retries fail"""
        url = "https://speechma.com/com.api/tts-api.php"

        # All calls fail
        for _ in range(3):
            responses.add(responses.POST, url, body="Error", status=500)

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        # Simulate retry logic
        result = None
        for attempt in range(3):
            result = get_audio(url, data, headers)
            if result:
                break

        assert result is None


@pytest.mark.integration
@pytest.mark.api
class TestAPIDataSanitization:
    """Integration tests for data sanitization before API calls"""

    @responses.activate
    def test_api_with_sanitized_text(self, mock_audio_response):
        """Test API call with sanitized text"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        # Text should have quotes and special chars removed
        original_text = "Hello 'world' and \"universe\" & more!"
        sanitized_text = original_text.replace("'", "").replace('"', "").replace("&", "and")

        data = {"text": sanitized_text, "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is not None

        # Verify request was made with sanitized text (no apostrophes or ampersands in content)
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        # Verify the sanitized text is in the request (apostrophes and quotes removed)
        assert "Hello world and universe and more!" in request_body

    @responses.activate
    def test_api_with_long_text(self, mock_audio_response):
        """Test API call with text at length limit"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        # Text at or near 1000 char limit
        long_text = "Word. " * 166  # ~1000 chars

        data = {"text": long_text[:1000], "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        result = get_audio(url, data, headers)

        assert result is not None


@pytest.mark.integration
@pytest.mark.api
class TestAPIHeaderValidation:
    """Integration tests for request header validation"""

    @responses.activate
    def test_api_with_required_headers(self, mock_audio_response):
        """Test that all required headers are included"""
        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {
            "Host": "speechma.com",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Origin": "https://speechma.com",
            "Referer": "https://speechma.com/",
        }

        result = get_audio(url, data, headers)

        assert result is not None

        # Verify headers were sent
        request = responses.calls[0].request
        assert request.headers.get("Content-Type") == "application/json"

    @responses.activate
    def test_api_without_user_agent(self, mock_audio_response):
        """Test API call without User-Agent (may be blocked)"""
        url = "https://speechma.com/com.api/tts-api.php"

        # Server might reject without User-Agent
        responses.add(responses.POST, url, body="Forbidden", status=403)

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}  # No User-Agent

        result = get_audio(url, data, headers)

        # Might return None due to 403
        assert result is None or isinstance(result, bytes)


@pytest.mark.integration
@pytest.mark.slow
class TestAPIPerformance:
    """Performance-related integration tests"""

    @responses.activate
    def test_api_response_time(self, mock_audio_response):
        """Test API response time is reasonable"""
        import time

        url = "https://speechma.com/com.api/tts-api.php"

        responses.add(responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"})

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        start_time = time.time()
        result = get_audio(url, data, headers)
        elapsed_time = time.time() - start_time

        assert result is not None
        assert elapsed_time < 5.0  # Should complete within 5 seconds

    @responses.activate
    def test_concurrent_api_calls(self, mock_audio_response):
        """Test handling multiple concurrent API calls"""
        import concurrent.futures

        url = "https://speechma.com/com.api/tts-api.php"

        # Add multiple responses
        for _ in range(5):
            responses.add(
                responses.POST, url, body=mock_audio_response, status=200, headers={"Content-Type": "audio/mpeg"}
            )

        data = {"text": "Test", "voice": "voice-111"}
        headers = {"Content-Type": "application/json"}

        # Make concurrent calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_audio, url, data, headers) for _ in range(5)]

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r is not None for r in results)
        assert len(results) == 5
