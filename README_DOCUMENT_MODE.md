# Audiobook Creator TTS - Document Mode

Convert EPUB and PDF documents to audio with automatic text extraction and smart chunking.

## Features

- Automatic text extraction from PDF and EPUB files
- Chapter-based organization with nested directories
- Smart metadata extraction (automatically extracts author from EPUB files)
- Intelligent title handling (removes author from filename when detected)
- Smart chunking that preserves sentence boundaries
- Named output files based on input filename (e.g., `othello-1.mp3`, `othello-2.mp3`)
- M4B audiobook creation with chapter markers and metadata (requires ffmpeg)
- Cover art embedding (requires AtomicParsley)
- Apple Books integration on macOS
- Progress tracking with live updates
- Resume capability for interrupted conversions
- One-time CAPTCHA solve, then convert unlimited documents
- Configurable chunk size (100-2000 characters)

## Quick Start

```bash
python3.11 main_document_mode.py
```

## Example Usage

### Converting an EPUB book

```bash
$ python3.11 main_document_mode.py

Audiobook Creator TTS - Document Mode
Convert EPUB and PDF files to audio

Voice Library: 583 voices

Initializing browser session...
Navigating to speechma.com...

[Solve CAPTCHA once]
Browser session ready!

NEW DOCUMENT CONVERSION

Enter document path (PDF or EPUB): ~/Downloads/Othello.epub

Reading EPUB: ~/Downloads/Othello.epub
Found 32 chapters/sections
   Processed 5/32 sections...
   Processed 10/32 sections...
   ...
Extracted 145,230 characters from EPUB

Text preview:
   OTHELLO, THE MOOR OF VENICE by William Shakespeare ACT I...

Total characters: 145,230
Estimated chunks: ~145

Proceed with conversion? (y/n): y

Show voice IDs? (y/n, default: n): n

Available voices:
1- Multilingual United States male Andrew Multilingual
...

Voice number (1-583): 12

Output files will be named: othello-1.mp3, othello-2.mp3, etc.

Chunk size in characters (default: 2000, max: 2000): 2000
Using chunk size: 2000 characters (optimal for performance)

Splitting text into chunks (max 2000 chars)...
Created 147 chunks
Average chunk size: 988 characters

Output directory: audio/othello_2025-01-14-10-30-45
Starting conversion...

[1/147] Processing chunk 1 (1%)...
   Preview: OTHELLO, THE MOOR OF VENICE by William Shakespeare ACT I SCENE I...
   Saved othello-1.mp3 (42.3 KB)

[2/147] Processing chunk 2 (1%)...
   Preview: Venice. A street. Enter RODERIGO and IAGO...
   Saved othello-2.mp3 (43.1 KB)

...

CONVERSION SUMMARY
Successful: 147/147 chunks
Output: audio/othello_2025-01-14-10-30-45
Files: othello-1.mp3 through othello-147.mp3

Creating M4B audiobook: othello
Converting to M4B with chapter markers...
Created M4B audiobook: othello.m4b (125.3 MB)

Audiobook ready: audio/othello_2025-01-14-10-30-45/othello.m4b

Open audiobook in Books app? (y/n): y
Opening in Books app...
Audiobook opened in Books app!

Convert another document? (y/n): n

Goodbye!
```

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Extracts text from all pages |
| EPUB | `.epub` | Extracts text from all chapters/sections |

## File Naming

Output files are automatically named based on the input filename:

| Input File | Output Files |
|------------|--------------|
| `Othello.epub` | `othello-1.mp3`, `othello-2.mp3`, ... |
| `My Book.pdf` | `my-book-1.mp3`, `my-book-2.mp3`, ... |
| `Pride_and_Prejudice.epub` | `pride-and-prejudice-1.mp3`, `pride-and-prejudice-2.mp3`, ... |

Output format: `{sanitized-filename}-{chunk-number}.mp3`

## Output Directory Structure

```text
audio/
  └── {filename}_{timestamp}/
      ├── othello-1.mp3
      ├── othello-2.mp3
      ├── othello-3.mp3
      ├── ...
      └── othello.m4b        (M4B audiobook with chapter markers)
```

Example:

```text
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

The system splits text to preserve natural reading flow:

1. Sentence boundaries - Splits at `. ! ?` when possible
2. Comma boundaries - Falls back to `,` if no sentence end
3. Word boundaries - Ensures words aren't cut in half
4. Configurable size - Adjust chunk size (100-2000 characters)

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

For M4B audiobook creation (optional but recommended):

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

Features:

- Single file with all audio combined
- Chapter markers for navigation
- Metadata (title and author)
- Cover art embedding (with AtomicParsley)
- Compatible with Apple Books, audiobook players, and most media players
- Automatic creation after successful conversion

Requirements:

- ffmpeg must be installed
- All MP3 chunks successfully generated
- AtomicParsley (optional, for cover art): `brew install atomicparsley`

If ffmpeg is not installed, the script skips M4B creation and shows a warning. You'll still have all individual MP3 files.

## Cover Art for Audiobooks

When creating M4B audiobooks, you can add custom cover art. The script prompts for cover art after confirming title and author but before starting TTS conversion.

Workflow:

1. Confirm conversion and select voice
2. Provide title and author metadata
3. Add cover art (asked here)
4. TTS conversion begins
5. M4B file created with cover art embedded

Options:

- Use default: If `cover.jpg` exists in the audiobook directory, script will offer to use it
- Custom path: Provide full path to your cover image
- Skip: Press 'n' to create audiobook without cover art

Supported formats: JPG/JPEG, PNG, GIF, BMP

Recommended: Square images (500x500 or larger), high quality (<2MB), clear thumbnail

Manual cover art embedding:

```bash
AtomicParsley audiobook.m4b --artwork cover.jpg --overWrite
```

## Apple Books Integration (macOS)

After creating your M4B audiobook, you can open it directly in Apple Books. The script prompts to open the audiobook in Books after M4B creation completes.

Platform support: macOS only (uses native `open` command)

Manual opening:

```bash
open audio/othello_2025-01-14-10-30-45/othello.m4b
```

Or drag and drop the M4B file directly into the Books app.

## Features in Detail

### Automatic Text Extraction

PDF Files:

- Extracts text from all pages
- Shows progress every 10 pages
- Handles multi-column layouts
- Preserves paragraph structure

EPUB Files:

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

- Automatic retries (3 attempts per chunk)
- CAPTCHA handling (prompts you to solve if needed)
- Failed chunk tracking
- Graceful recovery (continues even if some chunks fail)

## Tips

### For Long Documents

1. Start small - Test with a single chapter first
2. Monitor progress - Keep terminal visible
3. Stable connection - Ensure reliable internet
4. Don't close browser - Keep browser window open

### For Better Audio Quality

1. Choose appropriate voice - Test different voices
2. Optimize chunk size - Larger chunks = fewer files
3. Clean text first - Remove headers/footers if possible
4. Check extracted text - Review the preview before converting

### File Path Tips

- Drag and drop - Drag file into terminal to auto-fill path
- Quote paths - Use quotes for paths with spaces: `"/path/my file.pdf"`
- Relative paths - `./books/othello.epub` works
- Absolute paths - `/Users/name/Documents/book.pdf` also works

## Troubleshooting

### "No text extracted"

PDF Files:

- File might be scanned images (not searchable text)
- Try OCR software first to make it text-searchable
- Some PDFs have text extraction disabled

EPUB Files:

- File might be corrupted
- Try opening in an ebook reader first
- Re-download the file if needed

### "File not found"

- Check the file path is correct
- Use quotes around paths with spaces
- Ensure file extension is `.pdf` or `.epub`

### Large Files (>500 pages)

- Will take significant time (expect 1-2 hours)
- Process continues even if you minimize terminal
- Consider splitting large files into parts

### Browser Crashes

- Close other browser windows
- Restart the script
- You'll need to solve CAPTCHA again

## Performance

Processing speed:

- ~1-2 seconds per chunk (network dependent)
- ~50-100 chunks per hour
- Large books (500 pages) = 2-3 hours

File sizes:

- ~30-50 KB per chunk (MP3)
- 100 chunks ≈ 3-5 MB total
- Full novel ≈ 10-20 MB

## Comparison with Text Mode

| Feature | Document Mode | Text Mode |
|---------|--------------|-----------|
| Input | PDF/EPUB files | Copy/paste text |
| Output naming | `filename-N.mp3` | `audio_chunk_N.mp3` |
| M4B audiobook | Yes (with ffmpeg) | No |
| Text extraction | Automatic | Manual |
| Best for | Books, long documents | Short texts, articles |
| Chunk count | 50-500+ | 1-20 |

## Use Cases

- Audiobooks - Convert ebooks to audiobooks
- Study materials - Listen to textbooks and papers
- Articles - Convert saved PDFs to audio
- Documentation - Technical docs on the go
- Accessibility - Make documents accessible

## Limitations

- Scanned PDFs - Cannot extract text from images
- Complex layouts - Multi-column or graphic-heavy PDFs may not extract cleanly
- DRM-protected - Cannot process DRM-locked ebooks
- Image-based EPUBs - Fixed-layout EPUBs with images may not work

## Ready to Convert?

```bash
python3.11 main_document_mode.py
```
