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
# Interactive mode
python3.11 main_document_mode.py

# CLI mode (provide file path as argument)
python3.11 main_document_mode.py /path/to/document.pdf
```

✅ **Three input methods:**
  - 📂 File browser (native OS file picker)
  - ✍️  Plaintext input (type or paste directly)
  - ⌨️  Manual file path entry

✅ Automatic text extraction from multiple formats
✅ Supports: PDF, EPUB, DOCX, TXT, HTML, Markdown, Plaintext
✅ Smart chunking that preserves sentences
✅ Named output: `othello-1.mp3`, `othello-2.mp3`, etc.
✅ M4B audiobook creation with chapter markers (requires ffmpeg)
✅ Progress tracking with live updates
✅ One CAPTCHA solve for unlimited conversions

**Best for:** Books, research papers, Word documents, web articles, Markdown docs, custom text

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

### Example 1: Convert a Document with File Browser

```bash
$ python3.11 main_document_mode.py

📝 Input Method:
   1. Select file (opens file browser)
   2. Type or paste text
   3. Enter file path manually

Choice (1, 2, or 3): 1

[Native file picker opens - select your document]

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
```

### Example 2: Convert Plaintext

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
(Minimum 10 characters required)

Today's meeting covered the quarterly results.
We discussed revenue growth and market expansion.
Action items were assigned to each team member.
END

✅ Received 152 characters

[Processing continues...]
```

### Example 3: CLI Mode (Automation)

```bash
$ python3.11 main_document_mode.py ~/Documents/report.pdf

📄 File provided via CLI: ~/Documents/report.pdf

[Conversion proceeds directly with interactive prompts for voice and chunk size]
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

| Use Case | Mode | Input Method | Example |
|----------|------|--------------|---------|
| Convert ebook to audiobook | Document | File Browser/CLI | `Othello.epub` → `othello-1.mp3` ... |
| Study textbooks | Document | File Browser/CLI | `Biology_Ch5.pdf` → `biology-ch5-1.mp3` ... |
| Listen to research papers | Document | File Browser/Path | `paper.pdf` → `paper-1.mp3` ... |
| Convert Word documents | Document | File Browser/CLI | `report.docx` → `report-1.mp3` ... |
| Convert web articles | Document | File Browser/Path | `article.html` → `article-1.mp3` ... |
| Convert Markdown docs | Document | File Browser/Path | `README.md` → `readme-1.mp3` ... |
| Convert meeting notes | Document | Plaintext Input | Type text → `meeting-notes-1.mp3` ... |
| Quick announcements | Document | Plaintext Input | Paste text → `announcement-1.mp3` ... |
| Script automation | Document | CLI Argument | `script.sh` passes file path |
| Batch processing | Document | CLI Argument | Loop through files programmatically |

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
