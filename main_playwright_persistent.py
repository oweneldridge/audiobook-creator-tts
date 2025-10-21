#!/usr/bin/env python3.11
"""
Audiobook Creator TTS with Persistent Playwright Browser
Keeps browser session alive across multiple text-to-speech conversions
User only needs to solve CAPTCHA once at startup
"""
import asyncio
import json
import os
import sys
from datetime import datetime
import time
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

# Import functions from main.py to avoid duplication
sys.path.insert(0, os.path.dirname(__file__))
from main import (
    print_colored,
    input_colored,
    load_voices,
    display_voices,
    get_voice_id,
    split_text,
    validate_text,
    count_voice_stats,
    select_voice_interactive,
)


class PersistentBrowser:
    """Manages a persistent browser session for API requests with adaptive rate limiting"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.captcha_solved = False
        self.last_request_time = 0

        # Adaptive Rate Limiting
        self.base_delay = 2.5  # Base seconds between requests (increased from 2.0)
        self.current_delay = 2.5  # Current adaptive delay
        self.max_delay = 8.0  # Maximum delay under stress

        # Session Health Monitoring
        self.request_count = 0
        self.success_count = 0
        self.recent_results = []  # Track last 20 results for health score
        self.health_window_size = 20

        # Response Time Monitoring
        self.response_times = []
        self.baseline_response_time = None
        self.response_time_window = 10  # Track last 10 response times

    async def initialize(self):
        """Start browser and navigate to site"""
        print_colored("\n🚀 Initializing browser session...", "cyan")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Visible for CAPTCHA solving
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )

        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            locale="en-US",
            permissions=["geolocation"],
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        self.page = await context.new_page()

        # Add stealth JavaScript to mask automation
        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            window.chrome = {
                runtime: {}
            };
        """
        )

        # Navigate to the site
        print_colored("🌐 Navigating to speechma.com...", "cyan")
        await self.page.goto("https://speechma.com", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # Check for CAPTCHA
        print_colored("\n" + "=" * 60, "yellow")
        print_colored("⚠️  CAPTCHA CHECK", "yellow")
        print_colored("=" * 60, "yellow")
        print_colored("If you see a CAPTCHA in the browser window:", "yellow")
        print_colored("  1. Solve the CAPTCHA", "yellow")
        print_colored("  2. Wait for the page to fully load", "yellow")
        print_colored("  3. Press Enter here to continue", "yellow")
        print_colored("=" * 60, "yellow")
        input()

        self.captcha_solved = True
        print_colored("✅ Browser session ready!", "green")

    async def check_for_captcha(self) -> bool:
        """Check if CAPTCHA is present on the page"""
        try:
            # Check for common Cloudflare Turnstile CAPTCHA indicators
            captcha_selectors = [
                'iframe[src*="challenges.cloudflare.com"]',
                "#challenge-form",
                ".cf-challenge-running",
                '[id^="cf-challenge"]',
            ]

            for selector in captcha_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    return True

            return False
        except Exception:
            return False

    def update_health(self, success: bool):
        """Update session health tracking"""
        self.recent_results.append(success)
        if len(self.recent_results) > self.health_window_size:
            self.recent_results.pop(0)

        self.request_count += 1
        if success:
            self.success_count += 1

    def get_health_score(self) -> float:
        """Calculate session health score (0.0 to 1.0)"""
        if not self.recent_results:
            return 1.0
        return sum(self.recent_results) / len(self.recent_results)

    def update_response_time(self, response_time: float):
        """Track response times for baseline calculation"""
        self.response_times.append(response_time)
        if len(self.response_times) > self.response_time_window:
            self.response_times.pop(0)

        # Update baseline (average of tracked times)
        if len(self.response_times) >= 3:
            self.baseline_response_time = sum(self.response_times) / len(self.response_times)

    def calculate_adaptive_delay(self) -> float:
        """Calculate adaptive delay based on health and response times"""
        delay = self.base_delay

        # Health-based adjustment
        health = self.get_health_score()
        if health < 0.90:
            # Poor health: increase delay progressively
            health_penalty = (0.90 - health) * 10  # 0-9 second penalty
            delay += health_penalty

        # Response time-based adjustment
        if self.baseline_response_time and self.response_times:
            recent_avg = sum(self.response_times[-3:]) / min(3, len(self.response_times))
            if recent_avg > self.baseline_response_time * 1.5:
                # Slow responses detected: add delay
                delay += 2.0

        # Cap at maximum delay
        return min(delay, self.max_delay)

    async def display_captcha_notification(self):
        """Display CAPTCHA screenshot in terminal and send system notification"""
        import subprocess
        import tempfile

        try:
            # Take screenshot of current page
            screenshot_path = tempfile.mktemp(suffix=".png")
            await self.page.screenshot(path=screenshot_path)

            print_colored("\n" + "=" * 70, "yellow")
            print_colored("╔══════════════════════════════════════════════════════════════════╗", "yellow")
            print_colored("║  ⚠️  CAPTCHA REQUIRED - Solve in browser window                 ║", "yellow")
            print_colored("╚══════════════════════════════════════════════════════════════════╝", "yellow")

            # Display screenshot in iTerm2
            try:
                # Try iTerm2 imgcat protocol
                result = subprocess.run(["imgcat", screenshot_path], capture_output=True, timeout=5, check=False)
                if result.returncode != 0:
                    # Fallback: show file path
                    print_colored(f"\n📸 Screenshot saved: {screenshot_path}", "cyan")
                    print_colored("   Open screenshot to see CAPTCHA", "yellow")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # imgcat not available, just show path
                print_colored(f"\n📸 Screenshot saved: {screenshot_path}", "cyan")
                print_colored("   Open screenshot for reference", "yellow")

            # Session health stats
            health = self.get_health_score()
            print_colored(f"\n📊 Session Health: {health*100:.1f}%", "cyan")
            print_colored(f"   Total Requests: {self.request_count}", "cyan")
            print_colored(f"   Current Delay: {self.current_delay:.1f}s", "cyan")

            # Send macOS notification
            try:
                notification_title = "Audiobook Creator TTS"
                notification_message = "CAPTCHA solving required"
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{notification_message}" with title "{notification_title}" sound name "Hero"',
                    ],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
            except Exception:
                pass  # Notification failed, not critical

            print_colored("\n→ Solve the CAPTCHA in the browser window above", "green")
            print_colored("→ Press Enter when complete", "green")
            print_colored("=" * 70, "yellow")

        except Exception as e:
            print_colored(f"⚠️  Screenshot error: {e}", "yellow")

    async def wait_if_needed(self):
        """Add adaptive delay between requests to avoid triggering rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        # Calculate adaptive delay
        self.current_delay = self.calculate_adaptive_delay()

        if time_since_last < self.current_delay:
            wait_time = self.current_delay - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def request_audio(self, text: str, voice_id: str, retry_on_captcha: bool = True) -> Optional[bytes]:
        """
        Make API request using browser context with health monitoring
        Returns audio bytes or None on failure, or "RATE_LIMIT" string
        """
        try:
            # Add adaptive delay to avoid triggering rate limits/CAPTCHA
            await self.wait_if_needed()

            # Check for CAPTCHA before making request
            if await self.check_for_captcha():
                await self.display_captcha_notification()
                if retry_on_captcha:
                    input()
                    return await self.request_audio(text, voice_id, retry_on_captcha=False)
                return None

            # Track request start time for response time monitoring
            request_start = time.time()
            url = "https://speechma.com/com.api/tts-api.php"
            data = {"text": text.replace("'", "").replace('"', "").replace("&", "and"), "voice": voice_id}

            # Execute fetch request in browser context (includes all cookies)
            result = await self.page.evaluate(
                """
                async ({ url, data }) => {
                    try {
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });

                        if (!response.ok) {
                            return {
                                success: false,
                                status: response.status,
                                text: await response.text()
                            };
                        }

                        const contentType = response.headers.get('Content-Type');

                        if (contentType === 'audio/mpeg') {
                            const arrayBuffer = await response.arrayBuffer();
                            return {
                                success: true,
                                audio: Array.from(new Uint8Array(arrayBuffer)),
                                contentType: contentType
                            };
                        } else {
                            return {
                                success: false,
                                status: response.status,
                                contentType: contentType,
                                text: await response.text()
                            };
                        }
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message
                        };
                    }
                }
            """,
                {"url": url, "data": data},
            )

            # Track response time
            response_time = time.time() - request_start
            self.update_response_time(response_time)

            if result.get("success"):
                # Success: update health and return audio
                self.update_health(success=True)
                return bytes(result["audio"])

            # Handle errors - update health as failure
            self.update_health(success=False)
            status = result.get("status", "unknown")

            # Handle 429 Rate Limit
            if status == 429:
                print_colored("⚠️  Rate limit reached (429)", "yellow")
                if "text" in result:
                    print_colored(f"Response: {result['text'][:200]}", "yellow")

                # Return special marker to indicate rate limit
                return "RATE_LIMIT"

            # Handle 403 CAPTCHA
            elif status == 403:
                print_colored("❌ 403 Forbidden - CAPTCHA required!", "red")

                if retry_on_captcha:
                    await self.display_captcha_notification()
                    input()
                    # Retry once after user solves CAPTCHA
                    return await self.request_audio(text, voice_id, retry_on_captcha=False)

            # Handle other errors
            else:
                print_colored(f"❌ Request failed: Status {status}", "red")
                if "text" in result:
                    print_colored(f"Response: {result['text'][:200]}", "red")

            return None

        except Exception as e:
            # Exception: update health as failure
            self.update_health(success=False)
            print_colored(f"❌ Error: {e}", "red")
            return None

    async def check_session_health(self) -> bool:
        """
        Check session health and suggest restart if needed
        Returns True if session is healthy, False if restart recommended
        """
        health = self.get_health_score()

        # Warning at 90% health
        if health < 0.90 and self.request_count >= 10:
            print_colored(f"\n⚠️  Session Health Warning: {health*100:.1f}%", "yellow")
            print_colored(f"   Success Rate: {self.success_count}/{self.request_count}", "yellow")
            print_colored(f"   Current Delay: {self.current_delay:.1f}s", "yellow")

        # Critical at 80% health
        if health < 0.80 and self.request_count >= 15:
            print_colored(f"\n🚨 Session Health Critical: {health*100:.1f}%", "red")
            print_colored(f"   Success Rate: {self.success_count}/{self.request_count}", "red")
            print_colored("\n   Restarting session is recommended to improve performance", "yellow")
            return False

        return True

    async def restart(self):
        """
        Restart browser session (useful when rate-limited)
        Closes current session and starts fresh with new cookies
        """
        print_colored("\n🔄 Restarting browser session...", "yellow")
        print_colored("   Closing current session...", "cyan")
        await self.cleanup()
        print_colored("   Starting new session...", "cyan")
        await self.initialize()
        print_colored("✅ Session restart complete!", "green")

        # Reset health metrics
        self.request_count = 0
        self.success_count = 0
        self.recent_results = []
        self.response_times = []
        self.baseline_response_time = None
        self.current_delay = self.base_delay

    async def cleanup(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def process_text_to_speech(browser: PersistentBrowser, voice_id: str, text: str):
    """Process text-to-speech conversion"""

    # Split into chunks
    chunks = split_text(text, chunk_size=1000)
    if not chunks:
        print_colored("Error: Could not split text.", "red")
        return

    # Create output directory
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    directory = os.path.join("audio", timestamp)
    os.makedirs(directory, exist_ok=True)

    print_colored(f"\n📊 Processing {len(chunks)} chunk(s)...", "cyan")

    # Process each chunk
    success_count = 0
    for i, chunk in enumerate(chunks, start=1):
        print_colored(f"\n[{i}/{len(chunks)}] Processing chunk...", "yellow")

        max_retries = 3
        audio_data = None

        for attempt in range(max_retries):
            audio_data = await browser.request_audio(chunk, voice_id)

            if audio_data:
                # Save audio file
                file_path = os.path.join(directory, f"audio_chunk_{i}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                print_colored(f"✅ Saved to {file_path} ({len(audio_data)} bytes)", "green")
                success_count += 1
                break
            else:
                if attempt < max_retries - 1:
                    print_colored(f"⚠️  Retry {attempt + 1}/{max_retries}...", "yellow")
                    await asyncio.sleep(2)

        if not audio_data:
            print_colored(f"❌ Failed to process chunk {i}", "red")

    # Summary
    print_colored(f"\n{'='*60}", "cyan")
    print_colored(f"✅ Completed: {success_count}/{len(chunks)} chunks", "green")
    print_colored(f"📁 Output directory: {directory}", "cyan")
    print_colored(f"{'='*60}", "cyan")


async def main():
    """Main application loop"""

    # Display header
    print_colored("\n" + "=" * 60, "cyan")
    print_colored("🎤 Audiobook Creator TTS - Persistent Browser Mode", "magenta")
    print_colored("=" * 60, "cyan")

    # Load voices
    voices = load_voices()
    if not voices:
        print_colored("Error: No voices available.", "red")
        return

    # Display stats
    stats = count_voice_stats(voices)
    print_colored(f"\n📊 Voice Library:", "yellow")
    print(f"   • {stats['total']} voices")
    print(f"   • {len(stats['languages'])} languages")
    print(f"   • {len(stats['countries'])} countries")
    print_colored("=" * 60, "cyan")

    # Initialize browser (one-time setup)
    browser = PersistentBrowser()

    try:
        await browser.initialize()

        # Main loop
        while True:
            print_colored("\n" + "=" * 60, "blue")
            print_colored("NEW CONVERSION", "blue")
            print_colored("=" * 60, "blue")

            # Use interactive voice selection
            voice_id, voice_name = select_voice_interactive(voices)
            if not voice_id:
                print_colored("Voice selection cancelled. Exiting.", "yellow")
                return

            # Get text
            print_colored("\n📝 Enter your text:", "cyan")
            print_colored("(Type END on a new line when finished)", "yellow")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)

            text = " ".join(lines).replace("  ", " ")

            if not text or len(text) <= 9:
                print_colored("Error: Text too short (min 10 characters).", "red")
                continue

            text = validate_text(text)

            # Process
            await process_text_to_speech(browser, voice_id, text)

            # Continue?
            while True:
                choice = input_colored("\n🔄 Convert another text? (y/n): ", "blue").lower()
                if choice == "y":
                    break
                elif choice == "n":
                    print_colored("\n👋 Goodbye!", "magenta")
                    return
                else:
                    print_colored("Please enter 'y' or 'n'.", "red")

    finally:
        print_colored("\n🔒 Closing browser...", "cyan")
        await browser.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Exiting...", "yellow")
