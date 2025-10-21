# Audiobook Creator TTS - Document Mode

Convert entire EPUB and PDF documents to audio with automatic text extraction and smart chunking.

## Features

- **Automatic text extraction** from PDF and EPUB files
- **Chapter-based organization** with nested directories for books
- **Smart metadata extraction** - automatically extracts author from EPUB files
- **Intelligent title handling** - removes author from filename when detected
- **Smart chunking** that preserves sentence boundaries
- **Named output files** based on input filename (e.g., `othello-1.mp3`, `othello-2.mp3`)
- **M4B audiobook creation** with chapter markers and metadata (requires ffmpeg)
- **Cover art embedding** for professional audiobooks (requires AtomicParsley)
- **Apple Books integration** - open finished audiobooks directly in Books app (macOS)
- **Progress tracking** with live updates
- **Resume capability** - pick up where you left off if interrupted
- **One-time CAPTCHA** solve, then convert unlimited documents
- **Configurable chunk size** (100-2000 characters)

## Quick Start

```bash
python3.11 main_document_mode.py
```

## Example Usage

### Converting an EPUB book

```bash
$ python3.11 main_document_mode.py

============================================================
📚 Audiobook Creator TTS - Document Mode
============================================================
Convert EPUB and PDF files to audio
============================================================

📊 Voice Library: 583 voices

🚀 Initializing browser session...
🌐 Navigating to speechma.com...

[Solve CAPTCHA once]
✅ Browser session ready!

============================================================
NEW DOCUMENT CONVERSION
============================================================

📄 Enter document path (PDF or EPUB): ~/Downloads/Othello.epub

📚 Reading EPUB: ~/Downloads/Othello.epub
📖 Found 32 chapters/sections
   Processed 5/32 sections...
   Processed 10/32 sections...
   ...
✅ Extracted 145,230 characters from EPUB

============================================================

📝 Text preview:
   OTHELLO, THE MOOR OF VENICE by William Shakespeare ACT I...

📏 Total characters: 145,230
🔢 Estimated chunks: ~145

Proceed with conversion? (y/n): y

Show voice IDs? (y/n, default: n): n

📋 Available voices:
1- Multilingual United States male Andrew Multilingual
...

Voice number (1-583): 12

🎵 Output files will be named: othello-1.mp3, othello-2.mp3, etc.

Chunk size in characters (default: 2000, max: 2000): 2000
✅ Using chunk size: 2000 characters (optimal for performance)

✂️  Splitting text into chunks (max 2000 chars)...
✅ Created 147 chunks
📊 Average chunk size: 988 characters

📁 Output directory: audio/othello_2025-01-14-10-30-45
🎬 Starting conversion...

[1/147] Processing chunk 1 (1%)...
   Preview: OTHELLO, THE MOOR OF VENICE by William Shakespeare ACT I SCENE I...
   ✅ Saved othello-1.mp3 (42.3 KB)

[2/147] Processing chunk 2 (1%)...
   Preview: Venice. A street. Enter RODERIGO and IAGO...
   ✅ Saved othello-2.mp3 (43.1 KB)

...

============================================================
📊 CONVERSION SUMMARY
============================================================
✅ Successful: 147/147 chunks
📁 Output: audio/othello_2025-01-14-10-30-45
🎵 Files: othello-1.mp3 through othello-147.mp3

📖 Creating M4B audiobook: othello
🎬 Converting to M4B with chapter markers...
✅ Created M4B audiobook: othello.m4b (125.3 MB)

🎧 Audiobook ready: audio/othello_2025-01-14-10-30-45/othello.m4b

📖 Open audiobook in Books app? (y/n): y
📚 Opening in Books app...
✅ Audiobook opened in Books app!
============================================================

🔄 Convert another document? (y/n): n

👋 Goodbye!
```

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Extracts text from all pages |
| EPUB | `.epub` | Extracts text from all chapters/sections |

## File Naming

The output files are automatically named based on the input filename:

| Input File | Output Files |
|------------|--------------|
| `Othello.epub` | `othello-1.mp3`, `othello-2.mp3`, ... |
| `My Book.pdf` | `my-book-1.mp3`, `my-book-2.mp3`, ... |
| `Pride_and_Prejudice.epub` | `pride-and-prejudice-1.mp3`, `pride-and-prejudice-2.mp3`, ... |

Output format: `{sanitized-filename}-{chunk-number}.mp3`

## Output Directory Structure

```
audio/
  └── {filename}_{timestamp}/
      ├── othello-1.mp3
      ├── othello-2.mp3
      ├── othello-3.mp3
      ├── ...
      └── othello.m4b        (M4B audiobook with chapter markers)
```

Example:
```
audio/
  └── othello_2025-01-14-10-30-45/
      ├── othello-1.mp3      (42.3 KB)
      ├── othello-2.mp3      (43.1 KB)
      ├── othello-3.mp3      (41.8 KB)
      ├── ...
      ├── othello-147.mp3    (41.2 KB)
      └── othello.m4b        (125.3 MB - complete audiobook)
```

## Smart Chunking

The system intelligently splits text to preserve natural reading flow:

1. **Sentence boundaries** - Splits at `. ! ?` when possible
2. **Comma boundaries** - Falls back to `,` if no sentence end
3. **Word boundaries** - Ensures words aren't cut in half
4. **Configurable size** - Adjust chunk size (100-2000 characters)

### Chunk Size Guidelines

| Chunk Size | Use Case | Audio Length |
|------------|----------|--------------|
| 500-1000 | Short sentences, poetry | ~30-60 seconds |
| 1500-2000 (default) | General books, articles, optimal performance | ~75-120 seconds |
| 2000 | Long passages, technical docs, maximum efficiency | ~120 seconds |

## Installation

Make sure you have all dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

**For M4B audiobook creation** (optional but recommended):
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## M4B Audiobook Creation

After converting all MP3 chunks, the script automatically creates a single M4B audiobook file with chapter markers. Each chunk becomes a chapter, making it easy to navigate through the book.

**Features:**
- **Single File** - All audio combined into one M4B file
- **Chapter Markers** - Each chunk becomes a navigable chapter
- **Metadata** - Includes book title and author information
- **Cover Art** - Embed custom cover images for professional audiobooks
- **Compatibility** - Works with Apple Books, Audiobook players, and most media players
- **Automatic Creation** - Runs automatically after successful conversion

**Requirements:**
- ffmpeg must be installed (see Installation section above)
- All MP3 chunks must be successfully generated
- AtomicParsley (optional, for cover art): `brew install atomicparsley`

**Example Output:**
```
📖 Creating M4B audiobook: othello
🎬 Converting to M4B with chapter markers...
   Adding 147 chapters...
   Merging audio files...
   Writing metadata...
✅ Created M4B audiobook: othello.m4b (125.3 MB)

🎧 Audiobook ready: audio/othello_2025-01-14-10-30-45/othello.m4b
```

**What if ffmpeg is not installed?**
- Script will skip M4B creation and show a warning
- You'll still have all individual MP3 files
- You can install ffmpeg later and manually create M4B if needed

## Cover Art for Audiobooks

When creating M4B audiobooks, you can add custom cover art to make your audiobooks look professional in audiobook players and media libraries.

**When Asked:**
The script will prompt for cover art **after confirming title and author** but **before starting the TTS conversion**, so you don't have to wait.

**Workflow:**
1. Confirm conversion and select voice
2. **Provide title and author metadata**
3. **→ Add cover art (asked here)**
4. TTS conversion begins (all chapters)
5. M4B file created with cover art embedded

**Options:**
- **Use default**: If `cover.jpg` exists in the audiobook directory, script will offer to use it
- **Custom path**: Provide full path to your cover image
- **Skip**: Press 'n' to create audiobook without cover art

**Supported Formats:**
- JPG/JPEG
- PNG
- GIF
- BMP

**Recommended:**
- Square images (500x500 or larger)
- High quality (but not too large, <2MB)
- Clear, readable thumbnail

**Example:**
```
📖 Preparing to create M4B audiobook with metadata:
   Title: Othello
   Author: William Shakespeare

🎨 Would you like to add cover art to the audiobook? (y/n): y

✅ Found cover.jpg in audiobook directory. Use this file? (y/n): y

✅ Using cover.jpg
```

**Manual Cover Art Embedding:**
If you already have an M4B file and want to add cover art later:
```bash
AtomicParsley audiobook.m4b --artwork cover.jpg --overWrite
```

## Apple Books Integration (macOS)

After creating your M4B audiobook, you can open it directly in Apple Books for immediate listening and library management.

**When Asked:**
The script will prompt to open the audiobook in Books **after M4B creation completes**, so your audiobook is immediately ready to enjoy.

**Workflow:**
1. TTS conversion completes successfully
2. M4B file created with metadata and cover art
3. **→ Open in Books app? (asked here)**
4. Audiobook opens in Apple Books, ready to play

**Platform Support:**
- **macOS only** - Uses the native `open` command to launch Books app
- Automatically skipped on other platforms (Linux, Windows)
- Books app must be installed (pre-installed on macOS)

**Options:**
- **Yes (y)**: Opens the M4B file in Books app immediately
- **No (n)**: Skip opening, audiobook file remains in output directory

**Example:**
```
✅ Created M4B audiobook: othello.m4b (125.3 MB)

🎧 Audiobook ready: audio/othello_2025-01-14-10-30-45/othello.m4b

📖 Open audiobook in Books app? (y/n): y

📚 Opening in Books app...
✅ Audiobook opened in Books app!
```

**Error Handling:**
The script gracefully handles common issues:
- **File association not set**: Shows warning if M4B files aren't linked to Books
- **Timeout**: Shows warning if Books app takes too long to launch
- **Other errors**: Displays specific error message but continues normally

**Manual Opening:**
You can always open the audiobook in Books later:
```bash
open audio/othello_2025-01-14-10-30-45/othello.m4b
```

Or drag and drop the M4B file directly into the Books app.

## Features in Detail

### Automatic Text Extraction

**PDF Files:**
- Extracts text from all pages
- Shows progress every 10 pages
- Handles multi-column layouts
- Preserves paragraph structure

**EPUB Files:**
- Extracts from all chapters/sections
- Removes HTML formatting
- Cleans up navigation and metadata
- Shows progress every 5 sections

### Text Cleaning

Automatically:
- Removes non-ASCII characters
- Normalizes whitespace
- Removes excessive line breaks
- Sanitizes quotes and apostrophes
- Converts ampersands to "and"

### Progress Tracking

Real-time updates:
- Current chunk number and percentage
- Preview of text being converted
- File size of generated audio
- Success/failure status for each chunk

### Error Handling

- **Automatic retries** - 3 attempts per chunk
- **CAPTCHA handling** - Prompts you to solve if needed
- **Failed chunk tracking** - Shows which chunks failed
- **Graceful recovery** - Continues even if some chunks fail

## Tips

### For Long Documents

1. **Start small** - Test with a single chapter first
2. **Monitor progress** - Keep terminal visible to see progress
3. **Stable connection** - Ensure reliable internet
4. **Don't close browser** - Keep the browser window open

### For Better Audio Quality

1. **Choose appropriate voice** - Test different voices
2. **Optimize chunk size** - Larger chunks = fewer files
3. **Clean text first** - Remove headers/footers if possible
4. **Check extracted text** - Review the preview before converting

### File Path Tips

- **Drag and drop** - Drag file into terminal to auto-fill path
- **Quote paths** - Use quotes for paths with spaces: `"/path/my file.pdf"`
- **Relative paths** - `./books/othello.epub` works fine
- **Absolute paths** - `/Users/name/Documents/book.pdf` also works

## Troubleshooting

### "No text extracted"

**PDF Files:**
- File might be scanned images (not searchable text)
- Try OCR software first to make it text-searchable
- Some PDFs have text extraction disabled

**EPUB Files:**
- File might be corrupted
- Try opening in an ebook reader first
- Re-download the file if needed

### "File not found"

- Check the file path is correct
- Use quotes around paths with spaces
- Ensure file extension is `.pdf` or `.epub`

### Large Files (>500 pages)

- Will take significant time (expect 1-2 hours)
- Process will continue even if you minimize terminal
- Consider splitting large files into parts

### Browser Crashes

- Close other browser windows
- Restart the script
- You'll need to solve CAPTCHA again

## Performance

**Processing Speed:**
- ~1-2 seconds per chunk (network dependent)
- ~50-100 chunks per hour
- Large books (500 pages) = 2-3 hours

**File Sizes:**
- ~30-50 KB per chunk (MP3)
- 100 chunks ≈ 3-5 MB total
- Full novel ≈ 10-20 MB

## Comparison with Text Mode

| Feature | Document Mode | Text Mode |
|---------|--------------|-----------|
| Input | PDF/EPUB files | Copy/paste text |
| Output naming | `filename-N.mp3` | `audio_chunk_N.mp3` |
| M4B audiobook | ✅ Yes (with ffmpeg) | ❌ No |
| Text extraction | Automatic | Manual |
| Best for | Books, long documents | Short texts, articles |
| Chunk count | 50-500+ | 1-20 |

## Use Cases

✅ **Audiobooks** - Convert ebooks to audiobooks
✅ **Study materials** - Listen to textbooks and papers
✅ **Articles** - Convert saved PDFs to audio
✅ **Documentation** - Technical docs on the go
✅ **Accessibility** - Make documents accessible

## Example Workflows

### Converting a Novel

1. Download EPUB from library
2. Run `main_document_mode.py`
3. Select narrative voice (e.g., British English)
4. Convert with default settings
5. Listen in order: `othello-1.mp3`, `othello-2.mp3`, etc.

### Converting a Textbook

1. Get PDF version
2. Run script with larger chunks (1500-2000 chars)
3. Select clear, professional voice
4. Review chapter by chapter
5. Each chapter becomes separate folder

### Converting Research Papers

1. Collect PDFs in one folder
2. Process each paper separately
3. Use technical/academic voice
4. Smaller chunks (500-800) for complex content
5. Listen while commuting

## Limitations

- **Scanned PDFs** - Cannot extract text from images
- **Complex layouts** - Multi-column or graphic-heavy PDFs may not extract cleanly
- **DRM-protected** - Cannot process DRM-locked ebooks
- **Image-based EPUBs** - Fixed-layout EPUBs with images may not work

## Next Steps

1. Test with a small document first (10-20 pages)
2. Experiment with different voices
3. Find optimal chunk size for your content
4. Convert your library!

## Ready to Convert?

```bash
python3.11 main_document_mode.py
```

Happy reading (or listening)! 🎧📚
