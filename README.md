# Speechma Text-to-Speech CLI

A powerful command-line tool to convert text to speech using the Speechma API with 583 voices across 76 languages.

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for Playwright-based features)
playwright install chromium
```

## 🎯 Choose Your Mode

### 📚 Document Mode (RECOMMENDED for Books/Documents)
**Convert documents and ebooks to audio**

```bash
python3.11 main_document_mode.py
```

✅ Automatic text extraction from multiple formats
✅ Supports: PDF, EPUB, DOCX, TXT, HTML, Markdown
✅ Smart chunking that preserves sentences
✅ Named output: `othello-1.mp3`, `othello-2.mp3`, etc.
✅ M4B audiobook creation with chapter markers (requires ffmpeg)
✅ Progress tracking with live updates
✅ One CAPTCHA solve for unlimited conversions

**Best for:** Books, research papers, Word documents, web articles, Markdown docs

[📖 Document Mode Guide](README_DOCUMENT_MODE.md)

---

### 💬 Text Mode (for Short Texts)
**Type or paste text directly**

```bash
python3.11 main_playwright_persistent.py
```

✅ Interactive text input
✅ Multiline support (type END to finish)
✅ Multiple conversions in one session
✅ Persistent browser session

**Best for:** Short texts, articles, custom content

---

### 🍪 Manual Cookie Mode (Advanced)
**Manual cookie management (for headless environments)**

```bash
python3.11 main.py
```

✅ No browser automation required
✅ Lightweight execution
✅ Works in headless environments
❌ Requires manual cookie extraction

**Best for:** Automation, servers, advanced users

---

## 📊 Voice Library

- **583 voices** across **76 languages**
- Male, female, and multilingual options
- Professional quality audio output
- Support for major languages: English, Spanish, French, German, Chinese, Arabic, and many more

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium

# For M4B audiobook creation (optional but recommended)
# macOS: brew install ffmpeg
# Ubuntu/Debian: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
```

3. **Choose your mode and run:**

**For documents (PDF, EPUB, DOCX, TXT, HTML, Markdown):**
```bash
python3.11 main_document_mode.py
```

**For text input:**
```bash
python3.11 main_playwright_persistent.py
```

## 📁 Output Structure

All audio files are saved to timestamped directories:

### Document Mode
```
audio/
  └── othello_2025-01-14-10-30-45/
      ├── othello-1.mp3
      ├── othello-2.mp3
      ├── othello-3.mp3
      ├── ...
      └── othello.m4b        (Complete audiobook with chapter markers)
```

### Text Mode
```
audio/
  └── 2025-01-14 10-30-45/
      ├── audio_chunk_1.mp3
      ├── audio_chunk_2.mp3
      └── ...
```

## 🎬 How It Works

### Document Mode Workflow

1. **Extract Text** - Automatically parse PDF, EPUB, DOCX, TXT, HTML, or Markdown
2. **Smart Chunking** - Split text at sentence boundaries (1000 chars default)
3. **Browser Session** - Solve CAPTCHA once at startup
4. **Convert** - Process each chunk through Speechma API
5. **Named Output** - Save as `filename-1.mp3`, `filename-2.mp3`, etc.
6. **Create M4B** - Combine all MP3s into single audiobook with chapter markers (requires ffmpeg)

### Text Mode Workflow

1. **Browser Session** - Solve CAPTCHA once at startup
2. **Enter Text** - Type or paste text (type END to finish)
3. **Auto-Chunk** - Split into 1000 character chunks
4. **Convert** - Process through Speechma API
5. **Save** - Output to timestamped directory

## 🔧 Configuration Options

### Chunk Size
Adjust how text is split (default: 1000 characters):

- **500-800**: Short sentences, poetry
- **1000**: General books and articles (default)
- **1500-2000**: Long passages, technical documents

### Voice Selection
583 voices to choose from:

- **Multilingual**: Multiple languages per voice
- **Regional**: UK, US, Australian English, etc.
- **Gender**: Male and female options
- **Specialty**: Expressive and standard variants

## 📝 Examples

### Convert an EPUB Book

```bash
$ python3.11 main_document_mode.py

📄 Enter document path: ~/Downloads/Othello.epub

📚 Reading EPUB...
✅ Extracted 145,230 characters from EPUB

Voice number (1-583): 12

✂️  Splitting text into chunks...
✅ Created 147 chunks

[1/147] Processing chunk 1 (1%)...
   ✅ Saved othello-1.mp3 (42.3 KB)
...

============================================================
✅ Successful: 147/147 chunks
📁 Output: audio/othello_2025-01-14-10-30-45

📖 Creating M4B audiobook: othello
🎬 Converting to M4B with chapter markers...
✅ Created M4B audiobook: othello.m4b (125.3 MB)

🎧 Audiobook ready: audio/othello_2025-01-14-10-30-45/othello.m4b
============================================================
```

### Convert Short Text

```bash
$ python3.11 main_playwright_persistent.py

📋 Available voices:
...

Voice number (1-583): 25

📝 Enter your text:
(Type END on a new line when finished)
The quick brown fox jumps over the lazy dog.
This is a test of the text-to-speech system.
END

📊 Processing 1 chunk(s)...
✅ Saved to audio/2025-01-14-11-00-00/audio_chunk_1.mp3
```

## 🎯 Use Cases

| Use Case | Mode | Example |
|----------|------|---------|
| Convert ebook to audiobook | Document | `Othello.epub` → `othello-1.mp3` ... |
| Study textbooks | Document | `Biology_Ch5.pdf` → `biology-ch5-1.mp3` ... |
| Listen to research papers | Document | `paper.pdf` → `paper-1.mp3` ... |
| Convert Word documents | Document | `report.docx` → `report-1.mp3` ... |
| Convert web articles | Document | `article.html` → `article-1.mp3` ... |
| Convert Markdown docs | Document | `README.md` → `readme-1.mp3` ... |
| Convert short article | Text | Paste text → `audio_chunk_1.mp3` |
| Custom announcements | Text | Type text → `audio_chunk_1.mp3` |

## ⚠️ Important Notes

### CAPTCHA Handling
- Solve CAPTCHA **once** at startup
- Browser stays open for unlimited conversions
- If CAPTCHA reappears, script will pause and prompt you

### File Format Support

**Document Mode:**
- ✅ **PDF** - Searchable text PDFs
- ✅ **EPUB** - Ebooks (not DRM-protected)
- ✅ **DOCX** - Microsoft Word documents
- ✅ **TXT** - Plain text files (auto-detects encoding)
- ✅ **HTML/HTM** - Web pages and articles
- ✅ **Markdown (.md)** - Markdown documents
- ❌ Scanned PDFs (need OCR first)
- ❌ Images or graphic-only PDFs

### Performance

**Processing Speed:**
- ~1-2 seconds per chunk
- ~50-100 chunks per hour
- Large books (500 pages): 30-60 minutes

**Audio Quality:**
- Format: MP3
- Bitrate: Standard streaming quality
- Size: ~30-50 KB per chunk

## 🔍 Troubleshooting

### "No text extracted from PDF"
- PDF might be scanned images (needs OCR)
- Verify PDF has selectable text
- Try a different PDF reader

### "403 Forbidden" errors
- CAPTCHA needs solving
- Script will prompt you automatically
- Make sure browser window is visible

### "File not found"
- Check file path is correct
- Use quotes for paths with spaces
- Try absolute path: `/full/path/to/file.pdf`

### Browser won't open
- Make sure Chromium is installed: `playwright install chromium`
- Check you have a display/desktop session
- Not supported in pure headless environments (use manual cookie mode)

## 📚 Documentation

- [Document Mode Guide](README_DOCUMENT_MODE.md) - Full guide for PDF/EPUB conversion

## 🛠️ Technical Details

### Architecture

```
┌─────────────────────────────────────────────┐
│  Python Script                              │
│  (Document/Text Mode)                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Playwright Browser (Chromium)              │
│  • Automatic cookie management              │
│  • CAPTCHA solving interface                │
│  • Persistent session                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Text Processing                            │
│  • PDF extraction (pypdf)                   │
│  • EPUB extraction (ebooklib)               │
│  • DOCX extraction (python-docx)            │
│  • TXT extraction (chardet)                 │
│  • HTML extraction (BeautifulSoup)          │
│  • Markdown extraction (mistune)            │
│  • Smart chunking algorithm                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Speechma API                               │
│  • 583 voices across 76 languages           │
│  • Returns MP3 audio files                  │
└─────────────────────────────────────────────┘
```

### Dependencies

**Core:**
- **requests** - HTTP requests
- **playwright** - Browser automation

**Document Processing:**
- **pypdf** - PDF text extraction
- **ebooklib** - EPUB text extraction
- **python-docx** - DOCX text extraction
- **chardet** - TXT encoding detection
- **beautifulsoup4** - HTML parsing
- **mistune** - Markdown parsing

### Python Version

Requires Python 3.11+

## 📄 License

This project is for personal and educational use. Respect Speechma's terms of service.

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue!

## ⭐ Features

- ✅ Complete 583 voice library (76 languages)
- ✅ Multiple document formats (PDF, EPUB, DOCX, TXT, HTML, Markdown)
- ✅ M4B audiobook creation with chapter markers
- ✅ Persistent browser sessions
- ✅ Smart text chunking
- ✅ Progress tracking
- ✅ Named output files
- ✅ Automatic encoding detection for text files

### Future Enhancements

- [ ] Batch processing multiple files
- [ ] Resume interrupted conversions
- [ ] Audio file merging options
- [ ] ODT and RTF file support

## 💡 Tips

1. **Test with small documents first** - Get familiar with the process
2. **Choose appropriate voices** - British English for Shakespeare, etc.
3. **Adjust chunk size** - Smaller for poetry, larger for prose
4. **Keep browser visible** - Don't minimize during conversion
5. **Stable internet** - Ensure reliable connection for long conversions

## 🎉 Ready to Start?

**For documents:**
```bash
python3.11 main_document_mode.py
```

**For text:**
```bash
python3.11 main_playwright_persistent.py
```

Happy converting! 🎧📚✨

---

## 🙏 Credits

This project is based on [Speechma-API](https://github.com/fairy-root/Speechma-API) by [FairyRoot](https://github.com/fairy-root).

**Enhancements in this fork:**
- Complete 583 voice library extracted from speechma.com
- Playwright-based persistent browser mode
- Document conversion features with multi-format support
  - PDF, EPUB, DOCX, TXT, HTML, Markdown
- M4B audiobook creation with chapter markers
- Automatic encoding detection for text files
- requirements.txt for easy installation
- Comprehensive documentation
