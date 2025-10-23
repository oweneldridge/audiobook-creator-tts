#!/usr/bin/env python3.11
"""
Worker Browser - Isolated browser instance for parallel processing
Each worker maintains independent session, CAPTCHA counter, and browser profile
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, List, Tuple
from playwright.async_api import Browser, BrowserContext, Page

# Import from main
sys.path.insert(0, os.path.dirname(__file__))
from main_playwright_persistent import PersistentBrowser
from main import print_colored


def print_timestamped(message: str, color: str = "cyan"):
    """Print message with timestamp prefix"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm
    print_colored(f"[{timestamp}] {message}", color)


class WorkerBrowser(PersistentBrowser):
    """
    Isolated browser worker for parallel processing

    Each worker gets:
    - Unique browser profile (separate cookies/session)
    - Independent CAPTCHA counter (55-request limit per worker)
    - Assigned chunk list (distributed from coordinator)
    - Worker-specific window title and notifications
    """

    def __init__(self, worker_id: int, profile_dir: Optional[str] = None):
        """
        Initialize worker browser

        Args:
            worker_id: Unique identifier for this worker (1, 2, 3, ...)
            profile_dir: Directory for browser profile (defaults to /tmp/worker-{id})
        """
        super().__init__()

        self.worker_id = worker_id

        # Use unique profile directory per worker (separate cookies/sessions)
        if profile_dir is None:
            profile_dir = f"/tmp/audiobook-worker-{worker_id}"
        self.profile_dir = profile_dir

        # Worker-specific chunk assignments
        self.assigned_chunks: List[Tuple[int, str]] = []  # [(chunk_idx, chunk_text), ...]
        self.completed_chunks: List[int] = []  # Successfully processed chunk indices
        self.failed_chunks: List[int] = []  # Failed chunk indices

        # Worker-specific statistics
        self.worker_request_count = 0
        self.worker_success_count = 0

    async def initialize(self, skip_initial_captcha_prompt: bool = True):
        """
        Start browser with worker-specific configuration

        Args:
            skip_initial_captcha_prompt: If True, skip the initial CAPTCHA prompt (default: True for efficiency)
        """
        print_timestamped(f"🚀 [Worker #{self.worker_id}] Initializing browser session...", "cyan")

        from playwright.async_api import async_playwright

        # Ensure profile directory exists
        os.makedirs(self.profile_dir, exist_ok=True)

        self.playwright = await async_playwright().start()

        # Launch browser with persistent context (separate profile per worker)
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.profile_dir,
            headless=False,  # Visible for CAPTCHA solving
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            locale="en-US",
            permissions=["geolocation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Get first page from context
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        # Add stealth JavaScript
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

        # Navigate to site with error handling
        print_timestamped(f"🌐 [Worker #{self.worker_id}] Navigating to speechma.com...", "cyan")
        try:
            await self.page.goto("https://speechma.com", wait_until="networkidle", timeout=60000)
            print_timestamped(f"✅ [Worker #{self.worker_id}] Page loaded successfully", "green")
        except Exception as e:
            print_timestamped(f"⚠️  [Worker #{self.worker_id}] Navigation warning: {e}", "yellow")
            print_timestamped(f"   Retrying navigation...", "yellow")
            await self.page.goto("https://speechma.com", wait_until="domcontentloaded", timeout=60000)

        await asyncio.sleep(3)

        # Set worker-specific window title
        await self.page.evaluate(f'document.title = "Worker #{self.worker_id} - Audiobook TTS"')

        # Initial CAPTCHA check (skip for safety test to avoid deadlock)
        if not skip_initial_captcha_prompt:
            print_colored(f"\n{'='*60}", "yellow")
            print_colored(f"⚠️  [Worker #{self.worker_id}] CAPTCHA CHECK", "yellow")
            print_colored(f"{'='*60}", "yellow")
            print_colored(f"Browser window title: 'Worker #{self.worker_id}'", "cyan")
            print_colored(f"If you see a CAPTCHA in Worker #{self.worker_id} window:", "yellow")
            print_colored(f"  1. Solve the CAPTCHA", "yellow")
            print_colored(f"  2. Wait for page to load", "yellow")
            print_colored(f"  3. Press Enter here to continue", "yellow")
            print_colored(f"{'='*60}", "yellow")
            input()
        else:
            print_colored(
                f"⏩ [Worker #{self.worker_id}] Skipping initial CAPTCHA prompt (will prompt when needed)", "cyan"
            )

        self.captcha_solved = True
        self.requests_since_captcha = 0
        print_timestamped(f"✅ [Worker #{self.worker_id}] Browser session ready!", "green")

    async def display_captcha_notification(self):
        """Enhanced CAPTCHA notification with worker identification"""
        import subprocess
        import tempfile

        try:
            # Take screenshot
            screenshot_path = tempfile.mktemp(suffix=f"-worker-{self.worker_id}.png")
            await self.page.screenshot(path=screenshot_path)

            print_colored(f"\n{'='*70}", "yellow")
            print_colored(f"╔══════════════════════════════════════════════════════════════════╗", "yellow")
            print_colored(f"║  🔔 WORKER #{self.worker_id} - CAPTCHA REQUIRED                       ║", "yellow")
            print_colored(f"╚══════════════════════════════════════════════════════════════════╝", "yellow")

            print_colored(f"\n🪟 Find browser window: 'Worker #{self.worker_id} - Audiobook TTS'", "cyan")

            # Display screenshot in iTerm2
            try:
                result = subprocess.run(["imgcat", screenshot_path], capture_output=True, timeout=5, check=False)
                if result.returncode != 0:
                    print_colored(f"\n📸 Screenshot: {screenshot_path}", "cyan")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                print_colored(f"\n📸 Screenshot: {screenshot_path}", "cyan")

            # Worker-specific stats
            print_colored(f"\n📊 Worker #{self.worker_id} Stats:", "cyan")
            print_colored(f"   Total Requests: {self.request_count}", "cyan")
            print_colored(f"   Requests Since CAPTCHA: {self.requests_since_captcha}", "cyan")
            print_colored(f"   Completed Chunks: {len(self.completed_chunks)}", "cyan")
            print_colored(f"   Assigned Chunks: {len(self.assigned_chunks)}", "cyan")

            # Send macOS notification with worker ID
            try:
                notification_title = f"Worker #{self.worker_id} - CAPTCHA Required"
                notification_message = f"Solve CAPTCHA in Worker #{self.worker_id} browser window"
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
                pass

            print_colored(f"\n→ Solve CAPTCHA in 'Worker #{self.worker_id}' browser window", "green")
            print_colored(f"→ Press Enter when complete", "green")
            print_colored(f"{'='*70}", "yellow")

        except Exception as e:
            print_colored(f"⚠️  [Worker #{self.worker_id}] Screenshot error: {e}", "yellow")

    def assign_chunks(self, chunks: List[Tuple[int, str]]):
        """
        Assign chunks to this worker

        Args:
            chunks: List of (chunk_index, chunk_text) tuples
        """
        self.assigned_chunks = chunks
        print_colored(f"📋 [Worker #{self.worker_id}] Assigned {len(chunks)} chunks", "cyan")

    async def process_assigned_chunks(
        self,
        voice_id: str,
        output_dir: str,
        chapter_dir_name: str,
        chapter_number: int,
    ) -> dict:
        """
        Process all chunks assigned to this worker

        Args:
            voice_id: Voice ID for TTS
            output_dir: Base output directory
            chapter_dir_name: Chapter directory name (e.g., "01-prologue")
            chapter_number: Chapter number for progress display

        Returns:
            Dictionary with results:
            {
                "worker_id": int,
                "completed": [chunk_indices],
                "failed": [chunk_indices],
                "success_count": int,
                "failure_count": int
            }
        """
        print_timestamped(f"🎬 [Worker #{self.worker_id}] Starting chunk processing...", "green")

        for chunk_idx, chunk_text in self.assigned_chunks:
            # Progress indicator
            progress_num = self.assigned_chunks.index((chunk_idx, chunk_text)) + 1
            progress_total = len(self.assigned_chunks)

            print_timestamped(
                f"[Worker #{self.worker_id}] [{progress_num}/{progress_total}] Processing chunk {chunk_idx}...",
                "yellow",
            )
            print_colored(f"   Preview: {chunk_text[:60]}...", "cyan")

            # Request audio with retries
            max_retries = 3
            audio_data = None

            for attempt in range(max_retries):
                audio_data = await self.request_audio(chunk_text, voice_id)

                if audio_data == "RATE_LIMIT":
                    # Handle rate limit (shouldn't happen with proactive CAPTCHA)
                    print_colored(f"⚠️  [Worker #{self.worker_id}] Rate limit hit (unexpected)", "yellow")
                    await self.restart()
                    continue

                if audio_data and isinstance(audio_data, bytes):
                    # Success - save file
                    chapter_dir = os.path.join(output_dir, chapter_dir_name)
                    os.makedirs(chapter_dir, exist_ok=True)

                    # Determine filename based on directory structure
                    dir_prefix = chapter_dir_name.split("-")[0]
                    if chapter_dir_name.startswith("00-"):
                        parts = chapter_dir_name.split("-")
                        dir_prefix = f"{parts[0]}-{parts[1]}"

                    file_name = f"{dir_prefix}-chunk-{chunk_idx}.mp3"
                    file_path = os.path.join(chapter_dir, file_name)

                    with open(file_path, "wb") as f:
                        f.write(audio_data)

                    size_kb = len(audio_data) / 1024
                    print_timestamped(f"   ✅ [Worker #{self.worker_id}] Saved {file_name} ({size_kb:.1f} KB)", "green")

                    self.completed_chunks.append(chunk_idx)
                    self.worker_success_count += 1
                    break
                else:
                    # Retry on failure
                    if attempt < max_retries - 1:
                        print_colored(
                            f"   ⚠️  [Worker #{self.worker_id}] Retry {attempt + 1}/{max_retries}...", "yellow"
                        )
                        await asyncio.sleep(2)

            # Mark as failed if all retries exhausted
            if not audio_data:
                print_colored(f"   ❌ [Worker #{self.worker_id}] Failed chunk {chunk_idx}", "red")
                self.failed_chunks.append(chunk_idx)

        # Return results
        return {
            "worker_id": self.worker_id,
            "completed": self.completed_chunks,
            "failed": self.failed_chunks,
            "success_count": len(self.completed_chunks),
            "failure_count": len(self.failed_chunks),
        }

    async def cleanup(self):
        """Close browser and cleanup worker resources"""
        print_timestamped(f"🔒 [Worker #{self.worker_id}] Closing browser...", "cyan")

        # Close context instead of browser (since we used launch_persistent_context)
        if hasattr(self, "context") and self.context:
            await self.context.close()

        if self.playwright:
            await self.playwright.stop()

        print_timestamped(f"✅ [Worker #{self.worker_id}] Cleanup complete", "green")
