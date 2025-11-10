# Audiobook Creator TTS

Convert text and documents to audio using AI text-to-speech. Supports 583 voices across 76 languages.

Built on top of [Speechma-API](https://github.com/fairy-root/Speechma-API) with added document processing, parallel conversion, and M4B audiobook generation.

## Quick Start

Clone and run the automated installer:

```bash
git clone https://github.com/oweneldridge/audiobook-creator-tts.git
cd audiobook-creator-tts
./install.sh
```

The installer handles everything automatically - Python 3.11, virtual environment, dependencies, Playwright browser, and system packages (ffmpeg, AtomicParsley).
On a fresh system, you'll be prompted to confirm installation of Homebrew and Python if they're missing.

### Basic Usage

**Document mode** (recommended for books and PDFs):

```bash
python3.11 main_document_mode.py
```

**Text mode** (for shorter content):

```bash
python3.11 main_playwright_persistent.py
```

**Manual cookie mode** (for headless/automation):

```bash
python3.11 main.py
```

## Document Mode

The main way to use this tool. Converts PDFs, EPUBs, DOCX, TXT, HTML, and Markdown files to audio.

Run it and you'll get three input options:

1. File browser (if you have tkinter installed)
2. Type or paste text directly
3. Enter a file path manually

You can also provide the file path directly:

```bash
python3.11 main_document_mode.py /path/to/document.pdf
```

The script will:

- Extract text from your document
- Show you a preview and estimated chunk count
- Let you pick a voice from 583 options
- Convert each chunk to MP3
- Combine everything into a single M4B audiobook with chapter markers

Output goes to `audio/filename_timestamp/` with files named like `book-1.mp3`, `book-2.mp3`, etc. If you have ffmpeg installed, you'll also get a complete `book.m4b` file.

### Parallel Mode

For large documents (100+ chunks), parallel mode runs multiple browser sessions simultaneously to speed things up significantly.

When converting a large document, you'll be prompted to choose between:

- **Simple mode**: One browser session, reliable, slower (~21 min for 636 chunks)
- **Parallel mode**: Multiple workers, much faster (~3 min for 636 chunks), requires managing multiple CAPTCHA windows

The system calculates optimal worker count automatically (chunks ÷ 55, max 15 workers). You can pick from three CAPTCHA strategies:

- **Simultaneous**: All workers start together (fastest, all CAPTCHAs at once)
- **Staggered**: Workers start 10 seconds apart (balanced)
- **Sequential**: Batches of 2-3 workers (easiest to manage)

A safety test runs first (2 workers, 100 chunks) to verify no IP-level rate limiting before scaling up.

Configuration is in `config/parallel_settings.json` if you want to adjust worker limits or default strategy.

## Text Mode

Interactive mode for quick conversions. Paste or type text, get audio back. You can do multiple conversions in one session. Type "END" on a new line to finish input.

Output goes to `audio/timestamp/` with files named `audio_chunk_1.mp3`, etc.

## Supported Formats

- PDF (searchable text only - scanned PDFs need OCR first)
- EPUB (non-DRM)
- DOCX
- TXT (auto-detects encoding)
- HTML/HTM
- Markdown

## Voice Selection

583 voices organized by language, region, and gender. The script shows you an interactive menu where you can browse and search.
Voices include regional accents (US, UK, AU, etc.) and different speaking styles.

## Configuration

Text chunking defaults to 2000 characters with smart sentence boundary detection. You can adjust this in the code if needed:

- 500-1000: Better for poetry or dramatic content
- 1500-2000: Good for most books (default)
- 2000: Better for technical documents

## Resume Capability

If a conversion gets interrupted, run the script again with the same file. It'll detect existing audio chunks and offer to resume from where it left off or start fresh.

## M4B Audiobooks

With ffmpeg installed, the script automatically creates M4B audiobook files with:

- Chapter markers (based on document structure or chunk boundaries)
- Metadata (title, author, etc.)
- Cover art embedding (if available)
- Single-file output for easy library management

On macOS, it'll offer to open the finished audiobook in the Books app.

## Performance

Simple mode (single session):

- About 50-100 chunks per hour depending on network conditions
- API response time is 1-2 seconds per chunk, but rate limiting and CAPTCHA overhead slow things down
- A 500-page book takes 30-60 minutes

Parallel mode (multi-worker):

- 7x faster than simple mode for large documents
- Example: 636 chunks in ~3 minutes vs ~21 minutes
- Worker count auto-calculated based on chunk count
- Requires managing multiple browser windows for CAPTCHA

## Troubleshooting

**File browser not available:**

The file browser needs tkinter, which Homebrew Python 3.11+ doesn't include by default. You can either:

- Use option 2 (type/paste text) or option 3 (enter path manually)
- Pass the file path as a CLI argument: `python3.11 main_document_mode.py /path/to/file.pdf`
- Install tkinter: `brew install python-tk@3.11` (macOS) or `sudo apt-get install python3-tk` (Ubuntu/Debian)

**403 Forbidden errors:**

You hit a CAPTCHA. The script will prompt you to solve it in the browser window. Keep the browser visible while converting.

**No text extracted from PDF:**

Your PDF is probably scanned images. This tool only works with PDFs that have selectable text. You'd need OCR first.

**Browser won't open:**

Make sure Playwright's Chromium is installed: `playwright install chromium`

If you're on a headless server, use manual cookie mode instead.

## Technical Details

The conversion process:

1. Parse document and extract text
2. Split into chunks (max 2000 chars, respecting sentence boundaries)
3. Send each chunk to speechma.com's TTS API via Playwright-controlled browser
4. Save MP3 chunks with sequential naming
5. Concatenate chunks (ffmpeg) and create M4B with chapters

One CAPTCHA solve gives you about 55 successful API requests before you need to solve another one. Parallel mode distributes chunks across multiple workers, each with its own CAPTCHA counter.

Dependencies:

- playwright - Browser automation
- pypdf - PDF parsing
- ebooklib - EPUB parsing
- python-docx - Word documents
- chardet - Text encoding detection
- beautifulsoup4 - HTML/EPUB content extraction
- mistune - Markdown rendering
- ffmpeg (optional but recommended) - Audio concatenation and M4B creation
- AtomicParsley (optional) - Cover art embedding

## Manual Installation

If you prefer to set things up yourself instead of using the automated installer:

**Prerequisites:**

- Homebrew (macOS): <https://brew.sh>
- Python 3.11: `brew install python@3.11` (macOS) or `sudo apt-get install python3.11` (Ubuntu/Debian)

**Steps:**

```bash
# Clone repo
git clone https://github.com/oweneldridge/audiobook-creator-tts.git
cd audiobook-creator-tts

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Install optional system packages
brew install python-tk@3.11 ffmpeg atomicparsley  # macOS
sudo apt-get install python3-tk ffmpeg atomicparsley  # Ubuntu/Debian
```

## Additional Documentation

- [Document Mode Guide](README_DOCUMENT_MODE.md) - Full details on document conversion
- [Development Guide](DEVELOPMENT.md) - Architecture and development workflow
- [CAPTCHA Improvements](IMPROVEMENTS.md) - Details on predictive CAPTCHA handling

## License

MIT License - see LICENSE file.

This software interacts with speechma.com's API. Users are responsible for complying with speechma.com's terms of service. Intended for personal and educational use.

## Credits

Based on [Speechma-API](https://github.com/fairy-root/Speechma-API) by [FairyRoot](https://github.com/fairy-root).

Added features in this fork:

- Complete 583-voice library
- Playwright-based persistent sessions
- Multi-format document processing
- M4B audiobook creation
- Parallel processing mode
- Modern dependency management
