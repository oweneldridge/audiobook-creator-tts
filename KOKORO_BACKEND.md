# Kokoro TTS Backend

A pluggable TTS backend that replaces the fragile **speechma.com** browser scrape
with a self-hosted, OpenAI-compatible **Kokoro-FastAPI** server. No CAPTCHAs, no
rate limits, no Playwright, no parallel-window juggling — just unlimited local TTS.

## What changed

- **New `tts_backend.py`** — `KokoroBackend` is a drop-in stand-in for
  `PersistentBrowser`: same async `request_audio(text, voice_id) -> bytes`, so the
  existing `chunk → .mp3 → concat → M4B` pipeline is untouched.
- **`main_document_mode.py`** — picks the backend via `make_backend()`; in Kokoro
  mode it uses the configured voice (skips the 583-voice speechma picker) and skips
  the parallel-browser mode (pointless without CAPTCHAs). M4B bitrate **64k → 128k**.
- **`main.py`** — `validate_text` now **preserves Unicode** (accents, smart quotes,
  em-dashes) instead of stripping to ASCII, which had caused mispronunciations.

The old speechma path is fully intact — select it with `TTS_BACKEND=speechma`.

## Configuration (env vars)

| Var | Default | Meaning |
|---|---|---|
| `TTS_BACKEND` | `kokoro` | `kokoro` or `speechma` |
| `KOKORO_URL` | `http://becspk.tailaeef0f.ts.net:8880/v1` | OpenAI-compatible base URL |
| `KOKORO_VOICE` | `af_bella` | narrator voice (browse all at `…:8880/web`) |
| `KOKORO_FORMAT` | `mp3` | keep `mp3` so the `.mp3` pipeline works as-is |

The backend is the self-hosted Kokoro container on Spectre (`docker compose` service
`kokoro`, port 8880). Reachable on the LAN (`192.168.50.180:8880`) or over Tailscale
(`becspk.tailaeef0f.ts.net:8880`).

## Usage

```bash
# Default — uses Kokoro (af_bella, best for fiction) on Spectre:
python3.11 main_document_mode.py /path/to/book.epub

# Non-fiction / epic fantasy — UK female:
KOKORO_VOICE=bf_emma python3.11 main_document_mode.py /path/to/book.epub

# Fall back to the old speechma.com path:
TTS_BACKEND=speechma python3.11 main_document_mode.py /path/to/book.epub
```

## Quality / cost notes

Kokoro is free, offline, CPU-only (~2× real-time), Apache-2.0. ~75–80% of ElevenLabs
for neutral narration. For premium fiction, point `KOKORO_URL`/`TTS_BACKEND` at an
API (OpenAI, ElevenLabs, Azure) — the same `request_audio` signature works once a
matching backend is added to `tts_backend.py`.
