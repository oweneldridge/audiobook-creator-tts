<div align="center">

<img src="icon.png" alt="Audiobook Creator TTS" width="200"/>

# Audiobook Creator TTS

### 🎙️ Transform text into high-quality audiobooks with 583 AI voices

*Convert documents, ebooks, and text into professional audio across 76 languages*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Voices](https://img.shields.io/badge/voices-583-green.svg)](voices.json)
[![Languages](https://img.shields.io/badge/languages-76-orange.svg)](voices.json)
[![Format](https://img.shields.io/badge/output-MP3%20%7C%20M4B-red.svg)](#)

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🎯 **Smart Document Processing**
- 📄 **Multi-Format Support**: PDF, EPUB, DOCX, TXT, HTML, Markdown
- 🧠 **Intelligent Chunking**: Preserves sentence boundaries
- 📚 **M4B Audiobooks**: Chapter markers & metadata
- 🎵 **Named Output**: `book-1.mp3`, `book-2.mp3`, etc.
- 🔄 **Progress Tracking**: Real-time conversion updates

</td>
<td width="50%" valign="top">

### 🌍 **Extensive Voice Library**
- 🗣️ **583 Premium Voices** across 76 languages
- 👥 Male, female, and multilingual options
- 🎭 Regional accents (UK, US, AU, etc.)
- 🎨 Expressive and standard variants
- 🔊 Professional streaming quality

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation

**⚡ Quick Install (Recommended)**

One command installs everything:

```bash
# Clone repository
git clone https://github.com/oweneldridge/audiobook-creator-tts.git
cd audiobook-creator-tts

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux

# Run automated installer (installs ALL dependencies)
./install.sh
```

The installer automatically handles:
- ✅ Python packages (requests, playwright, pypdf, etc.)
- ✅ Playwright browser (Chromium)
- ✅ System packages (tkinter, ffmpeg, AtomicParsley)
- ✅ Installation verification

<details>
<summary><b>📝 Manual Installation (Alternative)</b></summary>

```bash
# 1. Clone repository
git clone https://github.com/oweneldridge/audiobook-creator-tts.git
cd audiobook-creator-tts

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. (Optional) Install system packages for enhanced features
# File Browser (tkinter) - enables Option 1 "Select file" dialog
brew install python-tk@3.11  # macOS (Homebrew)
# sudo apt-get install python3-tk  # Ubuntu/Debian

# M4B Audiobook Creation (ffmpeg) - recommended
brew install ffmpeg  # macOS
# sudo apt-get install ffmpeg  # Ubuntu/Debian

# Cover Art Embedding (AtomicParsley) - optional
brew install atomicparsley  # macOS
```

</details>

### Usage

<table>
<tr>
<th>Mode</th>
<th>Command</th>
<th>Best For</th>
</tr>
<tr>
<td>📚 <b>Document Mode</b><br/><i>(Recommended)</i></td>
<td><code>python3.11 main_document_mode.py</code></td>
<td>Books, PDFs, documents, ebooks</td>
</tr>
<tr>
<td>💬 <b>Text Mode</b></td>
<td><code>python3.11 main_playwright_persistent.py</code></td>
<td>Short texts, articles, custom content</td>
</tr>
<tr>
<td>🍪 <b>Manual Cookie</b></td>
<td><code>python3.11 main.py</code></td>
<td>Headless servers, automation</td>
</tr>
</table>

> **💡 Tip:** Always activate your virtual environment before running: `source venv/bin/activate`

---

## 📖 Modes Explained

### 📚 Document Mode <sup>**RECOMMENDED**</sup>

Convert entire documents and ebooks into professional audiobooks with chapter markers.

```bash
python3.11 main_document_mode.py

# Or provide file path directly:
python3.11 main_document_mode.py /path/to/document.pdf
```

**Three Flexible Input Methods:**

| Method | Description | Use Case |
|--------|-------------|----------|
| 🖱️ **File Browser** | Native OS file picker | Quick document selection |
| ✍️ **Plaintext Input** | Type or paste directly | Meeting notes, custom text |
| ⌨️ **Manual Path** | Enter file path | Automation, scripting |

**Supported Formats:**
- ✅ **PDF** - Searchable text PDFs
- ✅ **EPUB** - Ebooks (non-DRM)
- ✅ **DOCX** - Microsoft Word documents
- ✅ **TXT** - Plain text (auto-encoding detection)
- ✅ **HTML/HTM** - Web pages and articles
- ✅ **Markdown** - Documentation files

**Output:**
```
audio/
  └── othello_2025-01-14-10-30-45/
      ├── othello-1.mp3
      ├── othello-2.mp3
      ├── othello-3.mp3
      └── othello.m4b  ← Complete audiobook with chapters!
```

**Key Features:**
- ✅ One-time CAPTCHA solving for unlimited conversions
- ✅ Smart text chunking (~2000 chars, sentence-aware)
- ✅ M4B creation with chapter markers and metadata
- ✅ Progress tracking with live updates
- ✅ Resume capability for interrupted conversions
- ✅ Named output files based on document name

[📖 **Full Document Mode Guide →**](README_DOCUMENT_MODE.md)

---

### 💬 Text Mode

Perfect for quick text-to-speech conversions and short content.

```bash
python3.11 main_playwright_persistent.py
```

**Features:**
- ✨ Interactive text input (multiline support)
- ♾️ Multiple conversions in one session
- 🌐 Persistent browser session
- 🔄 Type "END" to finish input

**Output:**
```
audio/
  └── 2025-01-14 10-30-45/
      ├── audio_chunk_1.mp3
      ├── audio_chunk_2.mp3
      └── ...
```

---

### 🍪 Manual Cookie Mode

Advanced mode for headless environments and automation.

```bash
python3.11 main.py
```

**Features:**
- 🪶 Lightweight execution (no browser)
- 🖥️ Works in headless environments
- ⚙️ Ideal for automation
- ⚠️ Requires manual cookie extraction

---

## 🎯 Use Cases

<table>
<tr>
<th>📚 Learning & Education</th>
<th>📖 Reading & Entertainment</th>
</tr>
<tr>
<td>
• Study textbooks while commuting<br/>
• Listen to research papers<br/>
• Convert lecture notes to audio<br/>
• Learn languages with native speakers<br/>
</td>
<td>
• Convert ebooks to audiobooks<br/>
• Listen to articles and blogs<br/>
• Enjoy public domain classics<br/>
• Accessibility for visual impairments<br/>
</td>
</tr>
</table>

<table>
<tr>
<th>💼 Professional</th>
<th>🔧 Technical</th>
</tr>
<tr>
<td>
• Convert reports and documents<br/>
• Meeting notes playback<br/>
• Content creation for podcasts<br/>
• Email and document review<br/>
</td>
<td>
• Batch document processing<br/>
• API integration workflows<br/>
• Automated content generation<br/>
• Multi-language localization<br/>
</td>
</tr>
</table>

---

## 📝 Examples

### Example 1: Convert an Ebook with File Browser

```bash
$ python3.11 main_document_mode.py

📝 Input Method:
   1. Select file (opens file browser)
   2. Type or paste text
   3. Enter file path manually

Choice (1, 2, or 3): 1

[Native file picker opens - select your EPUB file]

📚 Reading EPUB...
✅ Extracted 145,230 characters from EPUB

📝 Text preview:
   To be or not to be, that is the question...

📏 Total characters: 145,230
🔢 Estimated chunks: ~146

Proceed with conversion? (y/n): y

[Voice selection...]
✅ Using voice: Emma (US Female)

🎵 Output files will be named: othello-1.mp3, othello-2.mp3, etc.

[Processing...]
✅ Successful: 147/147 chunks
📖 Creating M4B audiobook: othello.m4b
🎉 Complete! Your audiobook is ready.
```

---

### Example 2: Convert Custom Text

```bash
$ python3.11 main_document_mode.py

📝 Input Method:
   1. Select file (opens file browser)
   2. Type or paste text
   3. Enter file path manually

Choice (1, 2, or 3): 2

📝 Custom Output Name
What would you like to name this conversion? Meeting Notes

✅ Output files will be: meeting-notes-1.mp3, meeting-notes-2.mp3, etc.

📝 Enter your text:
(Type END on a new line when finished)

Today's meeting covered quarterly results.
We discussed revenue growth and market expansion.
Action items were assigned to each team.
END

✅ Received 152 characters
🔄 Processing...
```

---

### Example 3: CLI Mode (Automation)

```bash
$ python3.11 main_document_mode.py ~/Documents/report.pdf

📄 File provided via CLI: ~/Documents/report.pdf

[Conversion proceeds with interactive voice selection]
```

---

## 🔧 Configuration

### Chunk Size

Adjust text splitting for different content types (default: 2000 characters):

| Size | Best For |
|------|----------|
| **500-1000** | Poetry, short sentences, dramatic pauses |
| **1500-2000** | General books and articles _(default, recommended)_ |
| **2000** | Technical documents, long passages, optimal performance |

### Voice Selection

**583 voices organized by:**
- 🌍 **Language**: English, Spanish, French, German, Chinese, Arabic, and 70+ more
- 🗺️ **Region**: UK, US, Australia, Canada, India, etc.
- 👤 **Gender**: Male and female options
- 🎭 **Style**: Standard and expressive variants

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **API Response Time** | ~1-2 seconds per chunk |
| **Actual Throughput** | ~50-100 chunks per hour* |
| **Large Book (500 pages)** | 30-60 minutes |
| **Audio Format** | MP3 (streaming quality) |
| **File Size** | ~30-50 KB per chunk |

*Throughput includes network latency, rate limiting, and CAPTCHA overhead

---

## 🔍 Troubleshooting

<details>
<summary><b>🚫 "File browser not available (tkinter not installed)"</b></summary>

**Quick Solutions (No tkinter needed):**
- ✅ **Option 2**: Type or paste text directly
- ✅ **Option 3**: Enter file path manually
- ✅ **CLI Mode**: `python3.11 main_document_mode.py /path/to/file.pdf`

**Why this happens:**
- tkinter isn't included by default in Homebrew Python 3.11+
- File browser is optional - other input methods work perfectly

**To enable file browser (optional):**

**macOS (Homebrew Python):**
```bash
brew install python-tk@3.11
```

**macOS (pyenv):**
```bash
brew install tcl-tk

env \
  PATH="$(brew --prefix tcl-tk)/bin:$PATH" \
  LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
  CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
  PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
  CFLAGS="-I$(brew --prefix tcl-tk)/include" \
  PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
  pyenv install --force 3.11
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Verify installation:**
```bash
python3.11 -c "import tkinter; print('✅ tkinter available')"
```
</details>

<details>
<summary><b>🔴 "403 Forbidden" errors</b></summary>

- CAPTCHA needs solving
- Script will prompt automatically
- Keep browser window visible
</details>

<details>
<summary><b>📄 "No text extracted from PDF"</b></summary>

- PDF might be scanned images (needs OCR)
- Verify PDF has selectable text
- Try a different PDF
</details>

<details>
<summary><b>🌐 Browser won't open</b></summary>

- Install Chromium: `playwright install chromium`
- Ensure you have a desktop session
- Use manual cookie mode for headless environments
</details>

---

## 🛠️ Technical Architecture

### High-Level Flow

```mermaid
graph LR
    A[📄 Input<br/>PDF/EPUB/Text] --> B[📖 Document Parser<br/>pypdf, ebooklib, etc.]
    B --> C[✂️ Smart Chunking<br/>Sentence boundaries]
    C --> D[🌐 TTS API<br/>Playwright + speechma.com]
    D --> E[🎵 MP3 Chunks]
    E --> F[📦 Post-Processing<br/>ffmpeg, AtomicParsley]
    F --> G[🎧 M4B Audiobook<br/>Chapters + Metadata]
```

**Key Features:**
- **One-time CAPTCHA** solving for unlimited conversions
- **Resume capability** for interrupted sessions
- **Smart chunking** preserves natural reading flow
- **Chapter markers** in M4B with metadata and cover art

<details>
<summary><b>📐 Detailed Architecture (click to expand)</b></summary>

### Complete System Architecture

```mermaid
graph TB
    A[👤 User Input] --> B{Input Type?}

    B -->|File Path| C[📂 Document Parser]
    B -->|Plain Text| D[✅ Text Validation]

    C --> C1[📄 PDF Parser<br/>pypdf]
    C --> C2[📚 EPUB Parser<br/>ebooklib + BeautifulSoup]
    C --> C3[📝 DOCX Parser<br/>python-docx]
    C --> C4[📃 TXT Parser<br/>chardet encoding]
    C --> C5[🌐 HTML Parser<br/>BeautifulSoup]
    C --> C6[📋 Markdown Parser<br/>mistune]

    C1 --> E[📖 Chapter Extraction<br/>TOC + Headings + Structure]
    C2 --> E
    C3 --> F[📝 Text Extraction]
    C4 --> F
    C5 --> F
    C6 --> F
    D --> F

    E --> G[📊 Chapter Metadata<br/>Title, Number, Directory]
    F --> G

    G --> H[✂️ Smart Text Chunking<br/>Sentence/Comma/Word Boundaries<br/>Max 2000 chars]

    H --> I[🔍 Resume Check<br/>Analyze existing progress<br/>Identify missing chunks]

    I --> J[🎭 Voice Selection<br/>583 voices, 76 languages<br/>Interactive menu]

    J --> K[🌐 Playwright Browser Session<br/>Persistent authentication<br/>CAPTCHA handling]

    K --> L[🔊 TTS API Requests<br/>speechma.com/com.api/tts-api.php<br/>Rate limit management]

    L --> M[💾 MP3 Chunk Storage<br/>Nested directory structure<br/>Named: bookname-N.mp3]

    M --> N{Multiple<br/>Chunks?}
    N -->|Yes| O[🎵 Chapter Concatenation<br/>ffmpeg concat protocol<br/>Delete originals]
    N -->|Single| P

    O --> P[📖 M4B Creation Decision]

    P --> Q[🎬 M4B Audiobook Builder<br/>ffmpeg AAC encoding<br/>Chapter markers + metadata]

    Q --> R{Cover<br/>Art?}
    R -->|Yes| S[🎨 Cover Embedding<br/>AtomicParsley]
    R -->|No| T[✅ Final M4B File]

    S --> T

    T --> U{macOS<br/>Platform?}
    U -->|Yes| V[📚 Open in Books App<br/>macOS 'open' command]
    U -->|No| W[✅ Conversion Complete]
    V --> W

    style A fill:#e1f5ff
    style W fill:#c8e6c9
    style K fill:#fff9c4
    style L fill:#ffecb3
    style Q fill:#f8bbd0
```

### Component Details

**Document Parsing Layer:**
- Automatic format detection by file extension
- Chapter extraction strategies: TOC → Headings → File structure
- Author metadata extraction from EPUB Dublin Core
- Smart title handling (removes author from filename)

**Text Processing:**
- ASCII sanitization for API compatibility
- Smart chunking at sentence/comma/word boundaries
- Configurable chunk size (100-2000 characters)
- Preview generation for user confirmation

**Voice Management:**
- 583 voices organized by language, country, gender
- Interactive selection with search capability
- Voice statistics and filtering
- Session persistence

**TTS Conversion:**
- Playwright maintains authenticated browser session
- JavaScript `fetch()` in browser context for cookies
- Automatic CAPTCHA detection and user prompting
- Rate limit handling with session restart
- 3 retry attempts per chunk with exponential backoff

**Progress & Resume:**
- Analyzes existing audio directories by name pattern
- Calculates completion percentage
- Identifies missing chunks by chapter and index
- Offers resume or fresh start options
- Tracks concatenated vs. individual chunk files

**Post-Processing Pipeline:**
- **Chapter Concatenation**: ffmpeg concat protocol, stream copy (no re-encoding)
- **M4B Creation**: AAC encoding at 64kbps mono, FFMETADATA1 format
- **Chapter Markers**: Calculated from audio durations with millisecond precision
- **Cover Art**: AtomicParsley embedding with format validation
- **Apple Books**: macOS integration with error handling

**Output Structure:**
```
audio/
  └── bookname_2025-01-14-10-30-45/
      ├── 01-chapter-one/
      │   └── 01-chunk-1.mp3 (or 01-chapter-one.mp3 if concatenated)
      ├── 02-chapter-two/
      │   └── 02-chapter-two.mp3
      └── bookname.m4b (final audiobook with chapters)
```

</details>

### Core Dependencies

**Runtime:**
- **playwright** - Browser automation and session management
- **asyncio** - Asynchronous request handling

**Document Processing:**
- **pypdf** - PDF text extraction
- **ebooklib** - EPUB parsing and metadata
- **python-docx** - Microsoft Word documents
- **chardet** - Text encoding detection
- **beautifulsoup4** - HTML/EPUB content parsing
- **mistune** - Markdown rendering

**Audio Processing:**
- **ffmpeg** - MP3 concatenation and M4B creation (optional but recommended)
- **AtomicParsley** - Cover art embedding (optional)

---

## 💡 Pro Tips

| Tip | Description |
|-----|-------------|
| 🧪 **Start Small** | Test with small documents first |
| 🎭 **Match Voices** | British English for Shakespeare, etc. |
| 📏 **Adjust Chunks** | Smaller for poetry, larger for prose |
| 👀 **Keep Visible** | Don't minimize browser during conversion |
| 🌐 **Stable Internet** | Ensure reliable connection for long books |
| 📦 **Use M4B** | Single file with chapters > multiple MP3s |

---

## 📚 Documentation

- [📖 Document Mode Full Guide](README_DOCUMENT_MODE.md) - Comprehensive PDF/EPUB conversion guide
- [🛠️ Development Guide](DEVELOPMENT.md) - Technical architecture and development workflow
- [⚡ CAPTCHA & Rate Limiting Improvements](IMPROVEMENTS.md) - Adaptive rate limiting, session health monitoring, and performance optimizations

---

## 🚀 What's Next?

### Current Features
- ✅ 583 voices across 76 languages
- ✅ Multi-format document support
- ✅ M4B audiobook creation
- ✅ Persistent browser sessions
- ✅ Smart text chunking
- ✅ Progress tracking
- ✅ Resume interrupted conversions

### Roadmap
- [ ] Batch processing multiple files
- [ ] Audio merging and splitting tools
- [ ] ODT and RTF support
- [ ] Custom voice speed and pitch control
- [ ] GUI application

---

## 🙏 Acknowledgments

This project is built upon [Speechma-API](https://github.com/fairy-root/Speechma-API) by [FairyRoot](https://github.com/fairy-root).

**Enhancements in this fork:**
- ✨ Complete 583-voice library from speechma.com
- 🎭 Playwright-based persistent browser automation
- 📚 Multi-format document processing (PDF, EPUB, DOCX, TXT, HTML, Markdown)
- 🎵 M4B audiobook creation with chapter markers and metadata
- 📋 Comprehensive documentation and examples
- 🔧 Modern dependency management with requirements.txt

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

**Important**: This software interacts with speechma.com's API. Users must respect speechma.com's terms of service. This project is recommended for personal and educational use.

---

## 🤝 Contributing

Found a bug or have a feature request? Please [open an issue](../../issues)!

---

<div align="center">

### 🎧 Ready to Create Your First Audiobook?

**For documents:**
```bash
python3.11 main_document_mode.py
```

**For text:**
```bash
python3.11 main_playwright_persistent.py
```

---

**Made with ❤️ for audiobook enthusiasts**

*Star ⭐ this repo if you find it helpful!*

</div>
