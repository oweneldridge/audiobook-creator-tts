"""
Pluggable TTS backends for Audiobook Creator.

- speechma : the original speechma.com scraper (PersistentBrowser) — unchanged.
- kokoro   : self-hosted, OpenAI-compatible Kokoro-FastAPI. No CAPTCHAs, no rate
             limits, no browser. A drop-in stand-in for PersistentBrowser: it
             exposes the same async ``request_audio(text, voice_id)`` returning
             MP3 bytes, so the existing chunk -> mp3 -> concat -> M4B pipeline is
             untouched.

Configured via environment variables:
    TTS_BACKEND   = kokoro | speechma          (default: kokoro)
    KOKORO_URL    = http://becspk.tailaeef0f.ts.net:8880/v1   (the OpenAI-compatible base)
    KOKORO_VOICE  = af_bella                    (default narrator; bf_emma for non-fiction)
    KOKORO_FORMAT = mp3                         (keep mp3 so the .mp3 pipeline works as-is)

No new dependencies — uses the standard library (urllib).
"""

import asyncio
import json
import os
import urllib.request
from typing import Optional, Union

DEFAULT_KOKORO_URL = "http://becspk.tailaeef0f.ts.net:8880/v1"
DEFAULT_KOKORO_VOICE = "af_bella"  # animated/dramatic — best for fiction; bf_emma for non-fiction


class KokoroBackend:
    """Drop-in replacement for PersistentBrowser, backed by Kokoro-FastAPI."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        voice: Optional[str] = None,
        fmt: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("KOKORO_URL", DEFAULT_KOKORO_URL)).rstrip("/")
        self.voice = voice or os.environ.get("KOKORO_VOICE", DEFAULT_KOKORO_VOICE)
        self.fmt = fmt or os.environ.get("KOKORO_FORMAT", "mp3")
        # Compatibility stubs (the speechma flow references these on the browser object)
        self.requests_since_captcha = 0
        self.base_delay = 0.0
        self.captcha_request_limit = 10**9

    @property
    def _health_url(self) -> str:
        # /health lives at the server root, not under /v1
        root = self.base_url[:-3] if self.base_url.endswith("/v1") else self.base_url
        return root.rstrip("/") + "/health"

    async def initialize(self) -> None:
        """Health-check the Kokoro server (no browser, no CAPTCHA)."""

        def _check() -> int:
            req = urllib.request.Request(self._health_url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status

        ok = False
        try:
            ok = await asyncio.to_thread(_check) == 200
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Kokoro health check failed: {exc}")
        state = "ready" if ok else "UNREACHABLE"
        print(f"\U0001f50a TTS backend: Kokoro @ {self.base_url} (voice: {self.voice}, {self.fmt}) — {state}")
        if not ok:
            raise RuntimeError(
                f"Kokoro server not reachable at {self._health_url}. "
                "Start the container or set KOKORO_URL (or use TTS_BACKEND=speechma)."
            )

    async def request_audio(self, text: str, voice_id: str = "", retry_on_captcha: bool = True) -> Union[bytes, None]:
        """Synthesize ``text`` via Kokoro. Returns MP3 bytes, or None on failure.

        ``voice_id`` (a speechma id) is ignored; the configured Kokoro voice is used.
        """
        payload = json.dumps(
            {"model": "kokoro", "voice": self.voice, "input": text, "response_format": self.fmt}
        ).encode("utf-8")

        def _post() -> bytes:
            req = urllib.request.Request(
                f"{self.base_url}/audio/speech",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()

        for attempt in range(3):
            try:
                return await asyncio.to_thread(_post)
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"❌ Kokoro request failed after 3 attempts: {exc}")
                    return None
                await asyncio.sleep(1.5 * (attempt + 1))
        return None

    # --- No-op shims: Kokoro has no captcha / rate-limit / session lifecycle ---
    async def check_and_handle_captcha_limit(self) -> None: ...
    async def check_for_captcha(self) -> bool:
        return False

    async def check_session_health(self) -> bool:
        return True

    async def wait_if_needed(self) -> None: ...
    async def restart(self) -> None: ...
    async def cleanup(self) -> None: ...

    def update_health(self, success: bool = True) -> None: ...


def get_backend_name() -> str:
    return os.environ.get("TTS_BACKEND", "kokoro").strip().lower()


def is_kokoro() -> bool:
    return get_backend_name() == "kokoro"


def make_backend():
    """Return the configured TTS backend (duck-typed like PersistentBrowser)."""
    if is_kokoro():
        return KokoroBackend()
    from main_playwright_persistent import PersistentBrowser

    return PersistentBrowser()
