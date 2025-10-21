#!/usr/bin/env python3.11
"""
Audiobook Creator TTS - Document Mode (EPUB/PDF)
Converts entire EPUB or PDF files to audio with automatic text extraction
Supports chapter-based organization with nested directory structure
"""
import asyncio
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

# File dialog support
try:
    import tkinter as tk
    from tkinter import filedialog

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# PDF parsing
from pypdf import PdfReader

# EPUB parsing
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# XML parsing for EPUB TOC
from xml.etree import ElementTree as ET

# Additional document format support
try:
    from docx import Document as DocxDocument  # DOCX support

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import chardet  # Encoding detection for TXT

    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

try:
    import mistune  # Markdown parsing

    MISTUNE_AVAILABLE = True
except ImportError:
    MISTUNE_AVAILABLE = False

# Import from main.py
sys.path.insert(0, os.path.dirname(__file__))
from main import (
    print_colored,
    input_colored,
    load_voices,
    display_voices,
    get_voice_id,
    validate_text,
    count_voice_stats,
    select_voice_interactive,
)

# Import Playwright browser
from main_playwright_persistent import PersistentBrowser


def select_file_with_dialog() -> Optional[str]:
    """
    Open native file dialog for selecting a document

    Returns:
        Selected file path, or None if cancelled or unavailable
    """
    if not TKINTER_AVAILABLE:
        print_colored("❌ File browser not available (tkinter not installed)", "red")
        print_colored("Please install tkinter or enter file path manually", "yellow")
        return None

    try:
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        # Define file type filters
        filetypes = [
            ("All Supported Documents", "*.pdf *.epub *.docx *.txt *.html *.htm *.md *.markdown"),
            ("PDF Documents", "*.pdf"),
            ("EPUB E-books", "*.epub"),
            ("Word Documents", "*.docx"),
            ("Text Files", "*.txt"),
            ("HTML Files", "*.html *.htm"),
            ("Markdown Files", "*.md *.markdown"),
            ("All Files", "*.*"),
        ]

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Document to Convert", filetypes=filetypes, initialdir=os.path.expanduser("~")
        )

        # Cleanup
        root.destroy()

        # Return path or None if cancelled
        return file_path if file_path else None

    except Exception as e:
        print_colored(f"❌ File browser error: {e}", "red")
        return None


def get_plaintext_input() -> Tuple[Optional[str], Optional[str]]:
    """
    Get plaintext input from user with custom naming

    Returns:
        Tuple of (text, output_name) or (None, None) if cancelled
    """
    # Ask for custom name first
    print_colored("\n📝 Custom Output Name", "cyan")
    print_colored("(This will be used for output files: name-1.mp3, name-2.mp3, etc.)", "yellow")

    while True:
        output_name = input_colored("\nWhat would you like to name this conversion? ", "blue").strip()

        if not output_name:
            print_colored("Name cannot be empty", "red")
            continue

        # Sanitize name for safe filename
        # Convert to lowercase, alphanumeric with hyphens only
        sanitized_name = re.sub(r"[^a-z0-9]+", "-", output_name.lower()).strip("-")

        if not sanitized_name:
            print_colored("Invalid name - please use letters and numbers", "red")
            continue

        # Show user the sanitized version
        if sanitized_name != output_name.lower():
            print_colored(f"   Sanitized to: {sanitized_name}", "yellow")

        print_colored(f"✅ Output files will be: {sanitized_name}-1.mp3, {sanitized_name}-2.mp3, etc.", "green")
        break

    # Get multiline text input
    print_colored("\n📝 Enter your text:", "cyan")
    print_colored("(Type END on a new line when finished)", "yellow")
    print_colored("(Minimum 10 characters required)", "yellow")

    lines = []
    while True:
        try:
            line = input()
            if line == "END":
                break
            lines.append(line)
        except EOFError:
            break

    # Join lines with space and clean up
    text = " ".join(lines).replace("  ", " ").strip()

    # Validate minimum length
    if len(text) < 10:
        print_colored("❌ Text too short (minimum 10 characters)", "red")
        return None, None

    print_colored(f"\n✅ Received {len(text)} characters", "green")

    return text, sanitized_name


def check_playwright_browser() -> bool:
    """Check if Playwright Chromium browser is installed"""
    try:
        # Check for Chromium browser in Playwright cache
        playwright_cache = Path.home() / ".cache" / "ms-playwright"
        if not playwright_cache.exists():
            return False

        # Look for chromium directory
        chromium_dirs = list(playwright_cache.glob("chromium-*"))
        return len(chromium_dirs) > 0
    except Exception:
        return False


def install_playwright_browser():
    """Install Playwright Chromium browser with user feedback"""
    print_colored("\n" + "=" * 60, "yellow")
    print_colored("🔽 FIRST-TIME SETUP", "yellow")
    print_colored("=" * 60, "yellow")
    print_colored("Playwright browser not found. Installing Chromium...", "yellow")
    print_colored("This is a one-time download (~200MB, takes 2-3 minutes)", "cyan")
    print_colored("=" * 60, "yellow")

    try:
        # Run playwright install chromium
        result = subprocess.run(
            ["playwright", "install", "chromium"], capture_output=True, text=True, timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            print_colored("✅ Chromium browser installed successfully!", "green")
            return True
        else:
            print_colored(f"❌ Installation failed: {result.stderr}", "red")
            return False
    except subprocess.TimeoutExpired:
        print_colored("❌ Installation timeout (network might be slow)", "red")
        return False
    except Exception as e:
        print_colored(f"❌ Installation error: {e}", "red")
        return False


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is installed and available in PATH"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def show_ffmpeg_install_instructions():
    """Display instructions for installing ffmpeg"""
    print_colored("\n" + "=" * 60, "yellow")
    print_colored("⚠️  ffmpeg NOT FOUND", "yellow")
    print_colored("=" * 60, "yellow")
    print_colored("ffmpeg is required for concatenating MP3 chunks into single files.", "yellow")
    print_colored("\nWithout ffmpeg:", "yellow")
    print_colored("  • Individual chunks will be kept separately", "cyan")
    print_colored("  • Each chapter will have multiple MP3 files", "cyan")
    print_colored("\nTo enable auto-concatenation, install ffmpeg:", "yellow")
    print_colored("  macOS:   brew install ffmpeg", "green")
    print_colored("  Linux:   sudo apt install ffmpeg", "green")
    print_colored("  Windows: https://ffmpeg.org/download.html", "green")
    print_colored("=" * 60, "yellow")


def kebab_to_title_case(kebab_str: str) -> str:
    """
    Convert kebab-case string to Title Case
    Example: "the-republic" -> "The Republic"

    Args:
        kebab_str: Kebab-case string (e.g., "the-odyssey")

    Returns:
        Title-cased string (e.g., "The Odyssey")
    """
    # Split on hyphens and capitalize each word
    words = kebab_str.split("-")

    # List of words that should be lowercase in titles (unless first word)
    lowercase_words = {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "for",
        "nor",
        "on",
        "at",
        "to",
        "from",
        "by",
        "of",
        "in",
        "its",
    }

    # Capitalize first word always
    title_words = [words[0].capitalize()]

    # Handle remaining words
    for word in words[1:]:
        if word.lower() in lowercase_words:
            title_words.append(word.lower())
        else:
            title_words.append(word.capitalize())

    return " ".join(title_words)


def embed_cover_art(m4b_file_path: str, cover_image_path: str) -> bool:
    """
    Embed cover art into an m4b audiobook file using AtomicParsley.

    Args:
        m4b_file_path: Path to the m4b audiobook file
        cover_image_path: Path to the cover image file (jpg, png, etc.)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if AtomicParsley is installed
        result = subprocess.run(["which", "AtomicParsley"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print_colored("⚠️  AtomicParsley is not installed.", "yellow")
            print_colored("   Install it with: brew install atomicparsley", "yellow")
            print_colored("   Skipping cover art embedding.", "yellow")
            return False

        # Check if files exist
        if not os.path.exists(m4b_file_path):
            print_colored(f"❌ M4B file not found: {m4b_file_path}", "red")
            return False

        if not os.path.exists(cover_image_path):
            print_colored(f"❌ Cover image not found: {cover_image_path}", "red")
            return False

        # Run AtomicParsley to embed cover art
        print_colored(f"\n🎨 Embedding cover art into {os.path.basename(m4b_file_path)}...", "cyan")

        cmd = ["AtomicParsley", m4b_file_path, "--artwork", cover_image_path, "--overWrite"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print_colored("✅ Cover art embedded successfully!", "green")
            return True
        else:
            print_colored(f"❌ Error embedding cover art: {result.stderr}", "red")
            return False

    except subprocess.TimeoutExpired:
        print_colored("❌ Cover art embedding timeout", "red")
        return False
    except Exception as e:
        print_colored(f"❌ Error during cover art embedding: {e}", "red")
        return False


def prompt_for_cover_art(audiobook_dir: str) -> Optional[str]:
    """
    Prompt user if they want to add cover art and get the file path.

    Args:
        audiobook_dir: Directory where the audiobook is located

    Returns:
        Path to cover image file, or None if user declines
    """
    while True:
        response = (
            input_colored("\n🎨 Would you like to add cover art to the audiobook? (y/n): ", "blue").lower().strip()
        )

        if response == "n":
            return None
        elif response == "y":
            # Check for any common cover image format in the audiobook directory
            cover_filenames = ["cover.jpg", "cover.jpeg", "cover.png", "cover.gif", "cover.bmp"]
            found_cover = None

            for filename in cover_filenames:
                cover_path = os.path.join(audiobook_dir, filename)
                if os.path.exists(cover_path):
                    found_cover = cover_path
                    break

            if found_cover:
                use_default = (
                    input_colored(
                        f"\n✅ Found {os.path.basename(found_cover)} in audiobook directory. Use this file? (y/n): ",
                        "blue",
                    )
                    .lower()
                    .strip()
                )
                if use_default == "y":
                    return found_cover

            # Prompt for custom path
            while True:
                cover_path = input_colored("\n📁 Enter the full path to the cover image file: ", "cyan").strip()

                # Handle quoted paths
                if cover_path.startswith('"') and cover_path.endswith('"'):
                    cover_path = cover_path[1:-1]
                elif cover_path.startswith("'") and cover_path.endswith("'"):
                    cover_path = cover_path[1:-1]

                # Expand user home directory
                cover_path = os.path.expanduser(cover_path)

                if os.path.exists(cover_path):
                    # Validate it's an image file
                    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
                    if any(cover_path.lower().endswith(ext) for ext in valid_extensions):
                        return cover_path
                    else:
                        print_colored("❌ File must be an image (jpg, png, gif, bmp)", "red")
                else:
                    print_colored(f"❌ File not found: {cover_path}", "red")
                    retry = input_colored("Try again? (y/n): ", "blue").lower().strip()
                    if retry != "y":
                        return None
        else:
            print_colored("Invalid choice. Please enter 'y' or 'n'.", "red")


async def concatenate_chapter_mp3s(chapter_dir: str, chapter_name: str, chunk_files: List[str]) -> Optional[str]:
    """
    Concatenate multiple MP3 files into one using ffmpeg
    Deletes original chunks on success

    Args:
        chapter_dir: Directory containing chunk files
        chapter_name: Name for output file (e.g., "01-prologue")
        chunk_files: List of chunk file paths to concatenate

    Returns:
        Path to concatenated file, or None on failure
    """
    if not chunk_files:
        return None

    # Create concat list file for ffmpeg
    concat_list_path = os.path.join(chapter_dir, "concat_list.txt")
    output_path = os.path.join(chapter_dir, f"{chapter_name}.mp3")

    try:
        # Write file list for ffmpeg concat
        with open(concat_list_path, "w") as f:
            for chunk_file in chunk_files:
                # Use relative path from concat_list.txt location
                rel_path = os.path.basename(chunk_file)
                f.write(f"file '{rel_path}'\n")

        # Run ffmpeg concatenation
        cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list_path,
            "-c",
            "copy",  # Stream copy - no re-encoding
            output_path,
            "-y",  # Overwrite if exists
            "-loglevel",
            "error",  # Only show errors
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        # Clean up concat list
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)

        # Check if concatenation succeeded
        if result.returncode == 0 and os.path.exists(output_path):
            # Verify output file has reasonable size
            output_size = os.path.getsize(output_path)
            total_input_size = sum(os.path.getsize(f) for f in chunk_files if os.path.exists(f))

            # Output should be roughly same size as inputs (allow 5% variance)
            if output_size > total_input_size * 0.95:
                # Success! Delete original chunks
                for chunk_file in chunk_files:
                    if os.path.exists(chunk_file):
                        os.remove(chunk_file)

                return output_path
            else:
                print_colored(f"⚠️  Concatenated file size mismatch, keeping chunks", "yellow")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None
        else:
            if result.stderr:
                print_colored(f"⚠️  ffmpeg error: {result.stderr[:200]}", "yellow")
            return None

    except subprocess.TimeoutExpired:
        print_colored(f"⚠️  Concatenation timeout, keeping chunks", "yellow")
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)
        return None

    except Exception as e:
        print_colored(f"⚠️  Concatenation error: {e}", "yellow")
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)
        return None


def prompt_for_author(default_author: Optional[str] = None) -> str:
    """
    Prompt user to enter author name with optional default

    Args:
        default_author: Optional default author name (from EPUB metadata or filename)

    Returns:
        Author name (user-entered or default or "Unknown Author")
    """
    if default_author:
        print_colored(f"\n📝 Author Metadata", "cyan")
        print_colored(f"   Detected: {default_author}", "yellow")

        response = input_colored("\nUse this author? (y/n/enter custom): ", "blue").strip().lower()

        if response == "y":
            return default_author
        elif response == "n":
            return "Unknown Author"
        else:
            # User wants to enter custom name
            custom_author = input_colored("Enter author name: ", "cyan").strip()
            if custom_author:
                return custom_author
            return "Unknown Author"
    else:
        print_colored(f"\n📝 Author Metadata", "cyan")
        print_colored("   No author metadata found", "yellow")

        response = input_colored("\nEnter author name (or press Enter to skip): ", "blue").strip()

        if response:
            return response
        return "Unknown Author"


async def create_m4b_audiobook(
    base_directory: str,
    chapters: List["Chapter"],
    book_title: str,
    author: str = "Unknown Author",
    cover_image_path: Optional[str] = None,
) -> Optional[str]:
    """
    Create a single M4B audiobook file with chapter navigation

    Args:
        base_directory: Directory containing chapter MP3 files
        chapters: List of Chapter objects with metadata
        book_title: Title of the book (will be converted from kebab-case to Title Case)
        author: Author name for metadata
        cover_image_path: Optional path to cover image file

    Returns:
        Path to M4B file, or None on failure
    """
    # Convert kebab-case title to Title Case for metadata
    display_title = kebab_to_title_case(book_title)

    print_colored(f"\n📖 Creating M4B audiobook: {display_title}", "cyan")
    print_colored(f"   Author: {author}", "cyan")

    # Collect all chapter MP3 files
    chapter_files = []
    chapter_metadata = []

    for chapter in chapters:
        chapter_dir = os.path.join(base_directory, chapter.dir_name)

        # Look for concatenated MP3 or first chunk
        mp3_file = os.path.join(chapter_dir, f"{chapter.dir_name}.mp3")

        if not os.path.exists(mp3_file):
            # No concatenated file, look for chunk files
            chunk_pattern = os.path.join(chapter_dir, "*-chunk-*.mp3")
            import glob

            chunk_files = sorted(glob.glob(chunk_pattern))
            if not chunk_files:
                print_colored(f"⚠️  No audio files found for {chapter.title}, skipping", "yellow")
                continue
            # Use first chunk as placeholder (should have been concatenated)
            mp3_file = chunk_files[0]

        chapter_files.append(mp3_file)
        chapter_metadata.append({"title": chapter.title, "file": mp3_file})

    if not chapter_files:
        print_colored("❌ No chapter audio files found", "red")
        return None

    print_colored(f"✅ Found {len(chapter_files)} chapter audio files", "green")

    # Create temporary concat list for ffmpeg
    concat_list_path = os.path.join(base_directory, "chapters_concat.txt")
    output_m4b = os.path.join(base_directory, f"{book_title}.m4b")

    try:
        # Write concat list
        with open(concat_list_path, "w") as f:
            for chapter_file in chapter_files:
                rel_path = os.path.relpath(chapter_file, base_directory)
                f.write(f"file '{rel_path}'\n")

        # Build chapter metadata for ffmpeg
        # Calculate cumulative durations for chapter markers
        print_colored("⏱️  Calculating chapter durations...", "cyan")

        chapter_markers = []
        cumulative_ms = 0

        for idx, meta in enumerate(chapter_metadata):
            # Get duration of this chapter's audio file
            duration_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                meta["file"],
            ]

            try:
                result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    duration_sec = float(result.stdout.strip())
                    duration_ms = int(duration_sec * 1000)

                    chapter_markers.append(
                        {"title": meta["title"], "start_ms": cumulative_ms, "end_ms": cumulative_ms + duration_ms}
                    )

                    cumulative_ms += duration_ms
                else:
                    print_colored(f"⚠️  Could not get duration for {meta['title']}", "yellow")

            except Exception as e:
                print_colored(f"⚠️  Error getting duration for {meta['title']}: {e}", "yellow")

        # Create chapter metadata file (FFMETADATA format)
        metadata_file = os.path.join(base_directory, "chapters_metadata.txt")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(";FFMETADATA1\n")
            f.write(f"title={display_title}\n")
            f.write(f"artist={author}\n")
            f.write(f"album={display_title}\n")
            f.write("genre=Audiobook\n\n")

            for chapter in chapter_markers:
                f.write("[CHAPTER]\n")
                f.write("TIMEBASE=1/1000\n")
                f.write(f"START={chapter['start_ms']}\n")
                f.write(f"END={chapter['end_ms']}\n")
                f.write(f"title={chapter['title']}\n\n")

        print_colored("🎬 Converting to M4B with chapter markers...", "cyan")

        # Run ffmpeg to create M4B with chapters
        # First concat MP3s, then convert to M4B with metadata
        temp_concat_mp3 = os.path.join(base_directory, "temp_concat.mp3")

        # Step 1: Concatenate all MP3s
        concat_cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list_path,
            "-c",
            "copy",
            temp_concat_mp3,
            "-y",
            "-loglevel",
            "error",
        ]

        result = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print_colored(f"❌ MP3 concatenation failed: {result.stderr}", "red")
            return None

        # Step 2: Convert to M4B with AAC codec and add chapter metadata
        convert_cmd = [
            "ffmpeg",
            "-i",
            temp_concat_mp3,
            "-i",
            metadata_file,
            "-map_metadata",
            "1",
            "-map_chapters",
            "1",
            "-c:a",
            "aac",
            "-b:a",
            "64k",  # 64kbps for voice is sufficient
            "-ar",
            "44100",
            "-ac",
            "1",  # Mono
            output_m4b,
            "-y",
            "-loglevel",
            "error",
        ]

        result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=600)

        # Clean up temporary files
        for temp_file in [concat_list_path, metadata_file, temp_concat_mp3]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        if result.returncode == 0 and os.path.exists(output_m4b):
            size_mb = os.path.getsize(output_m4b) / 1024 / 1024
            print_colored(f"✅ Created M4B audiobook: {os.path.basename(output_m4b)} ({size_mb:.1f} MB)", "green")
            print_colored(f"   📚 {len(chapter_markers)} chapters with navigation", "yellow")

            # Embed cover art if provided
            if cover_image_path:
                embed_cover_art(output_m4b, cover_image_path)

            # Offer to open in Books app (macOS only)
            if sys.platform == "darwin":
                while True:
                    open_response = input_colored("\n📖 Open audiobook in Books app? (y/n): ", "blue").lower().strip()
                    if open_response == "y":
                        try:
                            print_colored("📚 Opening in Books app...", "cyan")
                            subprocess.run(["open", output_m4b], check=True, timeout=10)
                            print_colored("✅ Audiobook opened in Books app!", "green")
                        except subprocess.CalledProcessError:
                            print_colored("⚠️  Could not open in Books app (file association may not be set)", "yellow")
                        except subprocess.TimeoutExpired:
                            print_colored("⚠️  Timeout while trying to open Books app", "yellow")
                        except Exception as e:
                            print_colored(f"⚠️  Error opening Books app: {e}", "yellow")
                        break
                    elif open_response == "n":
                        break
                    else:
                        print_colored("Please enter 'y' or 'n'", "red")

            return output_m4b
        else:
            print_colored(f"❌ M4B conversion failed: {result.stderr[:200]}", "red")
            return None

    except subprocess.TimeoutExpired:
        print_colored("❌ M4B conversion timeout", "red")
        return None
    except Exception as e:
        print_colored(f"❌ M4B conversion error: {e}", "red")
        return None


@dataclass
class Chapter:
    """Represents a book chapter with metadata"""

    number: int  # 1, 2, 3...
    title: str  # "The Great White Whale"
    dir_name: str  # "01-the-great-white-whale"
    text: str  # Full chapter text
    chunks: List[str]  # Chunked text (populated later)


class DocumentParser:
    """Parses EPUB and PDF files to extract text"""

    @staticmethod
    def sanitize_dir_name(text: str) -> str:
        """Convert text to safe directory name (lowercase alphanumeric with hyphens)"""
        # Remove special characters, convert to lowercase
        clean = re.sub(r"[^a-z0-9\s-]", "", text.lower())
        # Replace spaces with hyphens
        clean = re.sub(r"\s+", "-", clean)
        # Remove multiple hyphens
        clean = re.sub(r"-+", "-", clean)
        # Trim hyphens from ends
        return clean.strip("-")

    @staticmethod
    def extract_author_from_epub(file_path: str) -> Optional[str]:
        """
        Extract author metadata from EPUB file

        Args:
            file_path: Path to EPUB file

        Returns:
            Author name if found, None otherwise
        """
        try:
            book = epub.read_epub(file_path)

            # Try to get author from Dublin Core metadata
            author = book.get_metadata("DC", "creator")

            if author and len(author) > 0:
                # author is a list of tuples: [(author_name, metadata_dict)]
                author_name = author[0][0]
                if author_name and author_name.strip():
                    return author_name.strip()

            return None

        except Exception as e:
            print_colored(f"⚠️  Could not extract author from EPUB: {e}", "yellow")
            return None

    @staticmethod
    def extract_chapters_from_epub(file_path: str) -> List[Chapter]:
        """
        Extract chapters from EPUB with metadata
        Strategy: TOC → Headings → File Structure
        """
        print_colored(f"📚 Reading EPUB: {file_path}", "cyan")

        try:
            book = epub.read_epub(file_path)

            # Strategy 1: Try to parse TOC (ncx or nav)
            chapters = DocumentParser._extract_from_epub_toc(book)

            if chapters:
                print_colored(f"✅ Extracted {len(chapters)} chapters from TOC", "green")
                return chapters

            # Strategy 2: Fallback to heading detection
            print_colored("⚠️  No TOC found, detecting chapters from headings...", "yellow")
            chapters = DocumentParser._extract_from_epub_headings(book)

            if chapters:
                print_colored(f"✅ Extracted {len(chapters)} chapters from headings", "green")
                return chapters

            # Strategy 3: Fallback to file structure
            print_colored("⚠️  No headings found, using file structure...", "yellow")
            chapters = DocumentParser._extract_from_epub_files(book)

            print_colored(f"✅ Extracted {len(chapters)} sections from file structure", "green")
            return chapters

        except Exception as e:
            print_colored(f"❌ Error reading EPUB: {e}", "red")
            return []

    @staticmethod
    def _is_story_chapter(title: str) -> bool:
        """Detect if a TOC entry is an actual story chapter vs front matter"""
        title_lower = title.lower().strip()

        # Story chapter patterns (numbered chapters only)
        # Note: Prologue and Epilogue are treated as front matter (00- prefix)
        story_patterns = [
            r"^chapter\s+\d+",
            r"^chapter\s+[ivxlcdm]+",  # Roman numerals
            r"^part\s+\d+",
            r"^part\s+[ivxlcdm]+",
            r"^book\s+\d+",
            r"^\d+\.",  # "1.", "2.", etc.
        ]

        for pattern in story_patterns:
            if re.match(pattern, title_lower):
                return True

        return False

    @staticmethod
    def _extract_from_epub_toc(book: epub.EpubBook) -> List[Chapter]:
        """Extract chapters from EPUB Table of Contents with smart numbering"""
        chapters = []
        toc = book.toc

        if not toc:
            return []

        # Flatten TOC (handle nested sections)
        def flatten_toc(items, level=0):
            flat = []
            for item in items:
                if isinstance(item, tuple):
                    # Nested section
                    flat.extend(flatten_toc(item[1], level + 1))
                elif isinstance(item, epub.Link):
                    flat.append(item)
                elif isinstance(item, epub.Section):
                    flat.append(item)
            return flat

        toc_items = flatten_toc(toc)

        # First pass: identify where story chapters begin
        story_start_idx = None
        for idx, item in enumerate(toc_items):
            if hasattr(item, "title") and DocumentParser._is_story_chapter(item.title):
                story_start_idx = idx
                break

        # If no story chapters detected, treat everything as chapters
        if story_start_idx is None:
            story_start_idx = 0

        # Map TOC items to actual content
        front_matter_num = 0
        story_chapter_num = 0

        for idx, item in enumerate(toc_items):
            try:
                # Get title
                if hasattr(item, "title"):
                    title = item.title
                else:
                    title = f"Section {idx + 1}"

                # Get href/file
                if hasattr(item, "href"):
                    href = item.href.split("#")[0]  # Remove anchor

                    # Find corresponding item in book
                    content_item = None
                    for book_item in book.get_items():
                        if hasattr(book_item, "get_name") and href in book_item.get_name():
                            content_item = book_item
                            break

                    if content_item:
                        # Extract text
                        soup = BeautifulSoup(content_item.get_content(), "html.parser")
                        for script in soup(["script", "style"]):
                            script.decompose()

                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = "\n".join(chunk for chunk in chunks if chunk)

                        if text.strip():
                            # Determine numbering based on position
                            if idx < story_start_idx:
                                # Front matter: use 00-xx- prefix for unique sorting
                                front_matter_num += 1
                                chapter_number = front_matter_num  # Use front matter counter
                                # Format: 00-01-title, 00-02-title, etc.
                                sanitized = DocumentParser.sanitize_dir_name(title)
                                dir_name = f"00-{front_matter_num:02d}-{sanitized}"
                            else:
                                # Story content: normal numbering starting at 01
                                story_chapter_num += 1
                                chapter_number = story_chapter_num
                                dir_name = f"{story_chapter_num:02d}-{DocumentParser.sanitize_dir_name(title)}"

                            chapters.append(
                                Chapter(number=chapter_number, title=title, dir_name=dir_name, text=text, chunks=[])
                            )

            except Exception as e:
                print_colored(f"⚠️  Error processing TOC item: {e}", "yellow")
                continue

        return chapters

    @staticmethod
    def _extract_from_epub_headings(book: epub.EpubBook) -> List[Chapter]:
        """Extract chapters by detecting h1/h2 headings"""
        chapters = []
        chapter_num = 1

        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

        for item in items:
            soup = BeautifulSoup(item.get_content(), "html.parser")

            # Look for h1 or h2 tags
            headings = soup.find_all(["h1", "h2"])

            if headings:
                for heading in headings:
                    title = heading.get_text().strip()

                    # Get text after this heading (until next heading or end)
                    text_parts = []
                    for sibling in heading.find_all_next():
                        if sibling.name in ["h1", "h2"]:
                            break
                        if sibling.get_text().strip():
                            text_parts.append(sibling.get_text())

                    text = "\n".join(text_parts)

                    if text.strip():
                        dir_name = f"{chapter_num:02d}-{DocumentParser.sanitize_dir_name(title)}"
                        chapters.append(
                            Chapter(number=chapter_num, title=title, dir_name=dir_name, text=text, chunks=[])
                        )
                        chapter_num += 1

        return chapters

    @staticmethod
    def _extract_from_epub_files(book: epub.EpubBook) -> List[Chapter]:
        """Extract chapters using file structure (each file = chapter)"""
        chapters = []
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

        for i, item in enumerate(items, 1):
            soup = BeautifulSoup(item.get_content(), "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            if text.strip():
                # Try to get title from first heading or filename
                title = None
                first_heading = soup.find(["h1", "h2", "h3"])
                if first_heading:
                    title = first_heading.get_text().strip()

                if not title:
                    title = f"Section {i}"

                dir_name = f"{i:02d}-{DocumentParser.sanitize_dir_name(title)}"
                chapters.append(Chapter(number=i, title=title, dir_name=dir_name, text=text, chunks=[]))

        return chapters

    @staticmethod
    def extract_chapters_from_pdf(file_path: str) -> List[Chapter]:
        """
        Extract chapters from PDF with heading detection
        Fallback to single chapter if no headings detected
        """
        print_colored(f"📄 Reading PDF: {file_path}", "cyan")

        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            print_colored(f"📖 Found {total_pages} pages", "yellow")

            # Extract all text with page boundaries
            full_text = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    full_text.append(text)

                if i % 10 == 0:
                    print_colored(f"   Processed {i}/{total_pages} pages...", "yellow")

            combined_text = "\n\n".join(full_text)

            # Try to detect chapters using heading patterns
            chapters = DocumentParser._detect_pdf_chapters(combined_text)

            if chapters:
                print_colored(f"✅ Detected {len(chapters)} chapters from headings", "green")
                return chapters

            # Fallback: Single chapter
            print_colored("⚠️  No chapter headings detected, using single chapter mode", "yellow")
            return [
                Chapter(number=1, title="Full Document", dir_name="01-full-document", text=combined_text, chunks=[])
            ]

        except Exception as e:
            print_colored(f"❌ Error reading PDF: {e}", "red")
            return []

    @staticmethod
    def _detect_pdf_chapters(text: str) -> List[Chapter]:
        """
        Detect chapters in PDF text using heading patterns
        Looks for: "Chapter N", "CHAPTER N", "Part N", etc.
        """
        chapters = []

        # Common chapter heading patterns
        patterns = [
            r"^(CHAPTER\s+\w+)[:\.\s]*(.*)$",  # CHAPTER ONE: Title
            r"^(Chapter\s+\w+)[:\.\s]*(.*)$",  # Chapter 1: Title
            r"^(PART\s+\w+)[:\.\s]*(.*)$",  # PART I: Title
            r"^(Part\s+\w+)[:\.\s]*(.*)$",  # Part 1: Title
            r"^(\d+)[:\.\s]+(.+)$",  # 1. Title or 1: Title
        ]

        # Split into lines
        lines = text.split("\n")
        current_chapter = None
        current_text = []
        chapter_num = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check if line matches any chapter pattern
            is_chapter = False
            for pattern in patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    # Save previous chapter
                    if current_chapter:
                        chapter_text = "\n".join(current_text).strip()
                        if chapter_text:
                            current_chapter.text = chapter_text
                            chapters.append(current_chapter)

                    # Start new chapter
                    chapter_num += 1
                    chapter_label = match.group(1).strip()
                    chapter_title = match.group(2).strip() if len(match.groups()) > 1 else ""

                    if not chapter_title:
                        chapter_title = chapter_label

                    dir_name = f"{chapter_num:02d}-{DocumentParser.sanitize_dir_name(chapter_title)}"

                    current_chapter = Chapter(
                        number=chapter_num, title=chapter_title, dir_name=dir_name, text="", chunks=[]
                    )
                    current_text = []
                    is_chapter = True
                    break

            # Add line to current chapter text
            if not is_chapter and current_chapter:
                current_text.append(line)

        # Save last chapter
        if current_chapter:
            chapter_text = "\n".join(current_text).strip()
            if chapter_text:
                current_chapter.text = chapter_text
                chapters.append(current_chapter)

        return chapters

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract all text from PDF file (legacy method for backward compatibility)"""
        print_colored(f"📄 Reading PDF: {file_path}", "cyan")

        try:
            reader = PdfReader(file_path)
            text_parts = []

            total_pages = len(reader.pages)
            print_colored(f"📖 Found {total_pages} pages", "yellow")

            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)

                if i % 10 == 0:
                    print_colored(f"   Processed {i}/{total_pages} pages...", "yellow")

            full_text = "\n\n".join(text_parts)
            print_colored(f"✅ Extracted {len(full_text)} characters from PDF", "green")
            return full_text

        except Exception as e:
            print_colored(f"❌ Error reading PDF: {e}", "red")
            return ""

    @staticmethod
    def extract_text_from_epub(file_path: str) -> str:
        """Extract all text from EPUB file"""
        print_colored(f"📚 Reading EPUB: {file_path}", "cyan")

        try:
            book = epub.read_epub(file_path)
            text_parts = []

            # Get all document items
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            print_colored(f"📖 Found {len(items)} chapters/sections", "yellow")

            for i, item in enumerate(items, 1):
                # Parse HTML content
                soup = BeautifulSoup(item.get_content(), "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)

                if text.strip():
                    text_parts.append(text)

                if i % 5 == 0:
                    print_colored(f"   Processed {i}/{len(items)} sections...", "yellow")

            full_text = "\n\n".join(text_parts)
            print_colored(f"✅ Extracted {len(full_text)} characters from EPUB", "green")
            return full_text

        except Exception as e:
            print_colored(f"❌ Error reading EPUB: {e}", "red")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX (Microsoft Word) file"""
        if not DOCX_AVAILABLE:
            print_colored("❌ python-docx library not installed", "red")
            print_colored("Install with: pip install python-docx", "yellow")
            return ""

        print_colored(f"📄 Reading DOCX: {file_path}", "cyan")

        try:
            doc = DocxDocument(file_path)
            text_parts = []

            # Extract text from all paragraphs
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            print_colored(f"✅ Extracted {len(full_text)} characters from DOCX", "green")
            return full_text

        except Exception as e:
            print_colored(f"❌ Error reading DOCX: {e}", "red")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file with encoding detection"""
        print_colored(f"📄 Reading TXT: {file_path}", "cyan")

        try:
            # Try to detect encoding
            encoding = "utf-8"  # Default encoding

            if CHARDET_AVAILABLE:
                with open(file_path, "rb") as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    if result and result["encoding"]:
                        encoding = result["encoding"]
                        print_colored(f"📝 Detected encoding: {encoding}", "yellow")

            # Read file with detected encoding
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                text = f.read()

            print_colored(f"✅ Extracted {len(text)} characters from TXT", "green")
            return text

        except Exception as e:
            print_colored(f"❌ Error reading TXT: {e}", "red")
            return ""

    @staticmethod
    def extract_text_from_html(file_path: str) -> str:
        """Extract text from HTML file"""
        print_colored(f"📄 Reading HTML: {file_path}", "cyan")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script, style, and navigation elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Try to find main content area
            main_content = soup.find(["article", "main", "div"])
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            print_colored(f"✅ Extracted {len(text)} characters from HTML", "green")
            return text

        except Exception as e:
            print_colored(f"❌ Error reading HTML: {e}", "red")
            return ""

    @staticmethod
    def extract_text_from_markdown(file_path: str) -> str:
        """Extract text from Markdown file"""
        print_colored(f"📄 Reading Markdown: {file_path}", "cyan")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                markdown_content = f.read()

            if MISTUNE_AVAILABLE:
                # Parse markdown to HTML then extract text
                markdown = mistune.create_markdown()
                html = markdown(markdown_content)
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text()
            else:
                # Fallback: simple cleanup of markdown syntax
                print_colored("⚠️  mistune not available, using basic markdown parsing", "yellow")
                text = markdown_content
                # Remove markdown headers
                text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
                # Remove bold/italic markers
                text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
                # Remove links
                text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = "\n".join(line for line in lines if line)

            print_colored(f"✅ Extracted {len(text)} characters from Markdown", "green")
            return text

        except Exception as e:
            print_colored(f"❌ Error reading Markdown: {e}", "red")
            return ""

    @staticmethod
    def parse_document(file_path: str) -> str:
        """Automatically detect file type and extract text"""
        file_path = Path(file_path)

        if not file_path.exists():
            print_colored(f"❌ File not found: {file_path}", "red")
            return ""

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return DocumentParser.extract_text_from_pdf(str(file_path))
        elif suffix == ".epub":
            return DocumentParser.extract_text_from_epub(str(file_path))
        elif suffix == ".docx":
            return DocumentParser.extract_text_from_docx(str(file_path))
        elif suffix == ".txt":
            return DocumentParser.extract_text_from_txt(str(file_path))
        elif suffix in [".html", ".htm"]:
            return DocumentParser.extract_text_from_html(str(file_path))
        elif suffix in [".md", ".markdown"]:
            return DocumentParser.extract_text_from_markdown(str(file_path))
        else:
            print_colored(f"❌ Unsupported file type: {suffix}", "red")
            print_colored("Supported formats: .pdf, .epub, .docx, .txt, .html, .htm, .md, .markdown", "yellow")
            return ""


def chunk_chapter_text(chapter: Chapter, chunk_size: int = 1000):
    """
    Chunk chapter text while preserving sentence boundaries
    Modifies chapter.chunks in place
    """
    if not chapter.text:
        chapter.chunks = []
        return

    # Clean up text
    text = validate_text(chapter.text)

    # Remove excessive whitespace
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Max 2 newlines
    text = re.sub(r" +", " ", text)  # Single spaces

    chunks = []

    while len(text) > 0:
        if len(text) <= chunk_size:
            chunks.append(text.strip())
            break

        # Try to split at sentence boundary
        chunk = text[:chunk_size]

        # Look for sentence endings (. ! ?)
        sentence_end = max(chunk.rfind(". "), chunk.rfind("! "), chunk.rfind("? "))

        # If no sentence ending, look for comma
        if sentence_end == -1:
            sentence_end = chunk.rfind(", ")

        # If no comma, look for space
        if sentence_end == -1:
            sentence_end = chunk.rfind(" ")

        # If still nothing, just cut at chunk_size
        if sentence_end == -1:
            sentence_end = chunk_size
        else:
            sentence_end += 1  # Include the punctuation

        chunks.append(text[:sentence_end].strip())
        text = text[sentence_end:].lstrip()

    chapter.chunks = [chunk for chunk in chunks if chunk]


def split_text_smart(text: str, chunk_size: int = 1000) -> List[str]:
    """
    Smart text splitting that preserves sentence and paragraph boundaries
    (Legacy function for backward compatibility)
    """
    if not text:
        return []

    # Clean up text
    text = validate_text(text)

    # Remove excessive whitespace
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Max 2 newlines
    text = re.sub(r" +", " ", text)  # Single spaces

    chunks = []

    while len(text) > 0:
        if len(text) <= chunk_size:
            chunks.append(text.strip())
            break

        # Try to split at sentence boundary
        chunk = text[:chunk_size]

        # Look for sentence endings (. ! ?)
        sentence_end = max(chunk.rfind(". "), chunk.rfind("! "), chunk.rfind("? "))

        # If no sentence ending, look for comma
        if sentence_end == -1:
            sentence_end = chunk.rfind(", ")

        # If no comma, look for space
        if sentence_end == -1:
            sentence_end = chunk.rfind(" ")

        # If still nothing, just cut at chunk_size
        if sentence_end == -1:
            sentence_end = chunk_size
        else:
            sentence_end += 1  # Include the punctuation

        chunks.append(text[:sentence_end].strip())
        text = text[sentence_end:].lstrip()

    return [chunk for chunk in chunks if chunk]


def find_existing_audio_directory(output_name: str) -> Optional[str]:
    """
    Find existing audio directory for this output_name
    Returns the most recent directory path, or None if not found
    """
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        return None

    # Look for directories matching pattern: output_name_*
    pattern = f"{output_name}_"
    matching_dirs = []

    for dir_name in os.listdir(audio_dir):
        dir_path = os.path.join(audio_dir, dir_name)
        if os.path.isdir(dir_path) and dir_name.startswith(pattern):
            matching_dirs.append((dir_path, os.path.getmtime(dir_path)))

    if not matching_dirs:
        return None

    # Return most recent directory
    matching_dirs.sort(key=lambda x: x[1], reverse=True)
    return matching_dirs[0][0]


def analyze_progress(base_directory: str, chapters: List[Chapter]) -> Tuple[int, int, List[Tuple[int, int]]]:
    """
    Analyze existing progress in a directory

    Returns:
        (completed_chunks, total_chunks, missing_chunks)
        missing_chunks: List of (chapter_number, chunk_idx) that are missing
    """
    total_chunks = sum(len(ch.chunks) for ch in chapters)
    completed_chunks = 0
    missing_chunks = []

    for chapter in chapters:
        chapter_dir = os.path.join(base_directory, chapter.dir_name)

        if not os.path.exists(chapter_dir):
            # Entire chapter missing
            for chunk_idx in range(1, len(chapter.chunks) + 1):
                missing_chunks.append((chapter.number, chunk_idx))
            continue

        # Check if chapter has been concatenated into single file
        concatenated_file = os.path.join(chapter_dir, f"{chapter.dir_name}.mp3")
        if os.path.exists(concatenated_file) and os.path.getsize(concatenated_file) > 0:
            # Entire chapter is concatenated - all chunks are complete
            completed_chunks += len(chapter.chunks)
            continue

        # Check individual chunks
        for chunk_idx in range(1, len(chapter.chunks) + 1):
            # Determine expected filename
            dir_prefix = chapter.dir_name.split("-")[0]
            if chapter.dir_name.startswith("00-"):
                parts = chapter.dir_name.split("-")
                dir_prefix = f"{parts[0]}-{parts[1]}"

            chunk_file = os.path.join(chapter_dir, f"{dir_prefix}-chunk-{chunk_idx}.mp3")

            if os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 0:
                completed_chunks += 1
            else:
                missing_chunks.append((chapter.number, chunk_idx))

    return completed_chunks, total_chunks, missing_chunks


async def process_chapters_to_speech(
    browser: PersistentBrowser,
    voice_id: str,
    chapters: List[Chapter],
    output_name: str,
    chunk_size: int = 1000,
    author: str = "Unknown Author",
    cover_image_path: Optional[str] = None,
):
    """Process chapters to speech with nested directory structure

    Args:
        browser: PersistentBrowser instance for API requests
        voice_id: Voice ID for text-to-speech
        chapters: List of Chapter objects with text content
        output_name: Name for output files
        chunk_size: Maximum characters per chunk
        author: Author name for M4B metadata
        cover_image_path: Optional path to cover image file for M4B
    """

    if not chapters:
        print_colored("❌ No chapters to process", "red")
        return

    # Chunk all chapters
    print_colored(f"\n✂️  Chunking {len(chapters)} chapters (max {chunk_size} chars per chunk)...", "cyan")
    total_chunks = 0

    for chapter in chapters:
        chunk_chapter_text(chapter, chunk_size=chunk_size)
        total_chunks += len(chapter.chunks)
        print_colored(f"   📖 Chapter {chapter.number} '{chapter.title}': {len(chapter.chunks)} chunks", "yellow")

    print_colored(f"\n✅ Total chunks across all chapters: {total_chunks}", "green")

    # Check for existing progress
    existing_dir = find_existing_audio_directory(output_name)
    missing_chunks = []
    base_directory = None
    resume_mode = False

    if existing_dir:
        print_colored(f"\n🔍 Found existing audio directory:", "yellow")
        print_colored(f"   {existing_dir}", "cyan")

        # Analyze progress
        completed, total, missing = analyze_progress(existing_dir, chapters)

        print_colored(f"\n📊 Progress Analysis:", "cyan")
        print_colored(f"   ✅ Completed: {completed}/{total} chunks ({int(completed/total*100)}%)", "green")
        print_colored(f"   ⏳ Missing: {len(missing)} chunks", "yellow")

        if len(missing) == 0:
            print_colored(f"\n✅ All chunks already completed!", "green")
            print_colored(f"📁 Directory: {existing_dir}", "cyan")

            # Check if M4B already exists
            m4b_file = os.path.join(existing_dir, f"{output_name}.m4b")
            if os.path.exists(m4b_file):
                print_colored(f"📖 M4B audiobook already exists: {os.path.basename(m4b_file)}", "green")
                return
            else:
                print_colored(f"\n📖 Creating M4B audiobook from completed chunks...", "cyan")
                m4b_file = await create_m4b_audiobook(existing_dir, chapters, output_name, author, cover_image_path)
                if m4b_file:
                    print_colored(f"\n✅ M4B AUDIOBOOK READY", "green")
                    print_colored(f"📖 File: {os.path.basename(m4b_file)}", "cyan")
                return

        # Prompt user to resume or restart
        print_colored(f"\n🔄 Resume Options:", "blue")
        print_colored(f"   1. Resume from checkpoint (process {len(missing)} missing chunks)", "green")
        print_colored(f"   2. Start fresh (create new directory)", "yellow")

        while True:
            choice = input_colored(f"\nChoice (1 or 2): ", "blue").strip()
            if choice == "1":
                base_directory = existing_dir
                missing_chunks = missing
                resume_mode = True
                print_colored(f"\n✅ Resuming from checkpoint", "green")
                print_colored(f"📁 Using directory: {base_directory}", "cyan")
                break
            elif choice == "2":
                print_colored(f"\n🆕 Starting fresh conversion", "yellow")
                break
            else:
                print_colored("Please enter 1 or 2", "red")

    # Create new directory if not resuming
    if not base_directory:
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        base_directory = os.path.join("audio", f"{output_name}_{timestamp}")
        os.makedirs(base_directory, exist_ok=True)
        print_colored(f"\n📁 Base output directory: {base_directory}", "cyan")

    print_colored(f"🎬 Starting conversion...\n", "cyan")

    # Process each chapter
    success_count = 0
    failed_chunks = []
    overall_chunk_num = 0

    for chapter in chapters:
        if not chapter.chunks:
            continue

        # Create chapter directory
        chapter_dir = os.path.join(base_directory, chapter.dir_name)
        os.makedirs(chapter_dir, exist_ok=True)

        # Check if entire chapter is already concatenated
        concatenated_file = os.path.join(chapter_dir, f"{chapter.dir_name}.mp3")
        if resume_mode and os.path.exists(concatenated_file) and os.path.getsize(concatenated_file) > 0:
            # Entire chapter already done and concatenated, skip it
            print_colored(f"\n{'='*60}", "blue")
            if chapter.dir_name.startswith("00-"):
                print_colored(f"📖 {chapter.title}", "magenta")
            else:
                dir_prefix = chapter.dir_name.split("-")[0]
                print_colored(f"📖 Chapter {dir_prefix}: {chapter.title}", "magenta")
            print_colored(f"✅ Already complete (concatenated)", "green")
            print_colored(f"{'='*60}", "blue")

            # Update counters
            success_count += len(chapter.chunks)
            overall_chunk_num += len(chapter.chunks)
            continue

        print_colored(f"\n{'='*60}", "blue")
        # Display header based on front matter vs story chapter
        if chapter.dir_name.startswith("00-"):
            # Front matter: just show title without "Chapter N"
            print_colored(f"📖 {chapter.title}", "magenta")
        else:
            # Story chapter: extract prefix from dir_name (e.g., "01" from "01-prologue")
            dir_prefix = chapter.dir_name.split("-")[0]
            print_colored(f"📖 Chapter {dir_prefix}: {chapter.title}", "magenta")
        print_colored(f"📁 Directory: {chapter.dir_name}", "cyan")
        print_colored(f"🔢 Chunks: {len(chapter.chunks)}", "yellow")
        print_colored(f"{'='*60}", "blue")

        # Track successful chunks for this chapter
        chapter_chunk_files = []
        chapter_success_count = 0

        # Process each chunk in this chapter
        for chunk_idx, chunk_text in enumerate(chapter.chunks, 1):
            overall_chunk_num += 1

            # Skip if already completed in resume mode
            if resume_mode and (chapter.number, chunk_idx) not in missing_chunks:
                # This chunk already exists, skip it
                # Build expected file path to add to chapter_chunk_files
                dir_prefix = chapter.dir_name.split("-")[0]
                if chapter.dir_name.startswith("00-"):
                    parts = chapter.dir_name.split("-")
                    dir_prefix = f"{parts[0]}-{parts[1]}"

                file_name = f"{dir_prefix}-chunk-{chunk_idx}.mp3"
                file_path = os.path.join(chapter_dir, file_name)

                if os.path.exists(file_path):
                    chapter_chunk_files.append(file_path)
                    chapter_success_count += 1
                    success_count += 1
                    print_colored(f"⏭️  Skipping existing chunk {chunk_idx}/{len(chapter.chunks)}", "cyan")
                continue

            # Progress indicator with context-aware chapter label
            progress = f"[{overall_chunk_num}/{total_chunks}]"
            percent = int((overall_chunk_num / total_chunks) * 100)

            # Display chapter context in progress
            if chapter.dir_name.startswith("00-"):
                # Front matter: just show title
                chapter_label = chapter.title
            else:
                # Story chapter: use prefix from dir_name
                dir_prefix = chapter.dir_name.split("-")[0]
                chapter_label = f"Chapter {dir_prefix}"

            print_colored(
                f"\n{progress} {chapter_label}, Chunk {chunk_idx}/{len(chapter.chunks)} ({percent}%)...", "yellow"
            )
            print_colored(f"   Preview: {chunk_text[:80]}...", "cyan")

            max_retries = 3
            audio_data = None

            for attempt in range(max_retries):
                audio_data = await browser.request_audio(chunk_text, voice_id)

                # Check for rate limit
                if audio_data == "RATE_LIMIT":
                    # Check session health before presenting options
                    health_ok = await browser.check_session_health()

                    print_colored("\n" + "=" * 60, "yellow")
                    print_colored("⏸️  RATE LIMIT REACHED", "yellow")
                    print_colored("=" * 60, "yellow")
                    print_colored("The API has rate-limited your requests.", "yellow")
                    print_colored(f"Progress: {success_count}/{total_chunks} chunks completed", "cyan")
                    print_colored(f"Current: Chapter {chapter.number}, Chunk {chunk_idx}/{len(chapter.chunks)}", "cyan")
                    print_colored("\nOptions:", "yellow")
                    if not health_ok:
                        print_colored("  1. Restart browser session (STRONGLY RECOMMENDED - poor health)", "green")
                    else:
                        print_colored("  1. Restart browser session and solve CAPTCHA (recommended)", "green")
                    print_colored("  2. Wait a few minutes and retry with same session", "yellow")
                    print_colored("  3. Press Ctrl+C to stop and resume later", "red")
                    print_colored("=" * 60, "yellow")

                    while True:
                        choice = input_colored("\nChoice (1, 2, or 3): ", "blue").strip()
                        if choice == "1":
                            # Restart browser session - gets fresh cookies, bypasses rate limit
                            await browser.restart()
                            print_colored("🔄 Session restarted! Retrying chunk...", "green")
                            break
                        elif choice == "2":
                            # Wait and retry with same session (may not work if still rate-limited)
                            print_colored("⏳ Waiting... press Enter when ready to retry", "yellow")
                            input()
                            print_colored("🔄 Retrying...", "green")
                            break
                        elif choice == "3":
                            print_colored("⚠️  Press Ctrl+C to exit, or Enter to go back to menu", "yellow")
                            input()
                            # Loop back to menu
                            continue
                        else:
                            print_colored("Please enter 1, 2, or 3", "red")

                    # Continue to next retry attempt
                    continue

                if audio_data:
                    # Extract numeric prefix from directory name for consistent naming
                    # e.g., "01-prologue" -> "01", "00-02-copyright" -> "00-02"
                    dir_prefix = chapter.dir_name.split("-")[0]
                    if chapter.dir_name.startswith("00-"):
                        # Front matter: "00-02-copyright" -> "00-02"
                        parts = chapter.dir_name.split("-")
                        dir_prefix = f"{parts[0]}-{parts[1]}"

                    # Save with directory-prefix-aware naming
                    file_name = f"{dir_prefix}-chunk-{chunk_idx}.mp3"
                    file_path = os.path.join(chapter_dir, file_name)

                    with open(file_path, "wb") as f:
                        f.write(audio_data)

                    size_kb = len(audio_data) / 1024
                    print_colored(f"   ✅ Saved {file_name} ({size_kb:.1f} KB)", "green")
                    success_count += 1
                    chapter_success_count += 1
                    chapter_chunk_files.append(file_path)
                    break
                else:
                    if attempt < max_retries - 1:
                        print_colored(f"   ⚠️  Retry {attempt + 1}/{max_retries}...", "yellow")
                        await asyncio.sleep(2)

            if not audio_data:
                print_colored(f"   ❌ Failed chapter {chapter.number}, chunk {chunk_idx}", "red")
                failed_chunks.append((chapter.number, chunk_idx))

        # Concatenate chapter chunks if all succeeded and more than 1 chunk
        if chapter_success_count == len(chapter.chunks) and len(chapter.chunks) > 1:
            print_colored(f"\n🎵 Concatenating {len(chapter.chunks)} chunks for {chapter.title}...", "cyan")

            concatenated_file = await concatenate_chapter_mp3s(chapter_dir, chapter.dir_name, chapter_chunk_files)

            if concatenated_file:
                size_mb = os.path.getsize(concatenated_file) / 1024 / 1024
                print_colored(f"✅ Created {chapter.dir_name}.mp3 ({size_mb:.1f} MB)", "green")
                print_colored(f"   Original chunks deleted", "yellow")
            else:
                print_colored(f"⚠️  Concatenation failed, kept individual chunks", "yellow")

    # Final summary
    print_colored("\n" + "=" * 60, "cyan")
    print_colored("📊 CONVERSION SUMMARY", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored(f"📚 Chapters processed: {len(chapters)}", "green")
    print_colored(f"✅ Successful chunks: {success_count}/{total_chunks}", "green")

    if failed_chunks:
        print_colored(f"❌ Failed chunks: {failed_chunks}", "red")

    print_colored(f"\n📁 Output directory: {base_directory}", "cyan")
    print_colored(f"📂 Chapter subdirectories created", "yellow")
    print_colored("=" * 60, "cyan")

    # Create M4B audiobook if all chapters succeeded
    if success_count == total_chunks and not failed_chunks:
        print_colored("\n🎧 All chapters completed successfully!", "green")
        print_colored("📖 Creating M4B audiobook with chapter navigation...", "cyan")

        # Use output_name as book title (already sanitized)
        m4b_file = await create_m4b_audiobook(
            base_directory,
            chapters,
            output_name,
            author,
            cover_image_path,
        )

        if m4b_file:
            print_colored(f"\n✅ M4B AUDIOBOOK READY", "green")
            print_colored(f"📖 File: {os.path.basename(m4b_file)}", "cyan")
            print_colored(f"📂 Location: {base_directory}", "yellow")
        else:
            print_colored(f"\n⚠️  M4B creation failed, but MP3s are available", "yellow")
    else:
        print_colored(f"\n⚠️  Skipping M4B creation due to failed chunks", "yellow")
        print_colored(f"   Fix failed chunks and re-run to generate M4B", "cyan")


async def process_document_to_speech(
    browser: PersistentBrowser, voice_id: str, text: str, output_name: str, chunk_size: int = 1000
):
    """Process document text to speech with named output files (legacy function)"""

    # Split into chunks
    print_colored(f"\n✂️  Splitting text into chunks (max {chunk_size} chars)...", "cyan")
    chunks = split_text_smart(text, chunk_size=chunk_size)

    if not chunks:
        print_colored("❌ No text chunks created", "red")
        return

    print_colored(f"✅ Created {len(chunks)} chunks", "green")

    # Show chunk statistics
    avg_length = sum(len(c) for c in chunks) / len(chunks)
    print_colored(f"📊 Average chunk size: {int(avg_length)} characters", "yellow")

    # Create output directory
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    directory = os.path.join("audio", f"{output_name}_{timestamp}")
    os.makedirs(directory, exist_ok=True)

    print_colored(f"\n📁 Output directory: {directory}", "cyan")
    print_colored(f"🎬 Starting conversion...\n", "cyan")

    # Process each chunk
    success_count = 0
    failed_chunks = []

    for i, chunk in enumerate(chunks, 1):
        # Progress indicator
        progress = f"[{i}/{len(chunks)}]"
        percent = int((i / len(chunks)) * 100)
        print_colored(f"\n{progress} Processing chunk {i} ({percent}%)...", "yellow")
        print_colored(f"   Preview: {chunk[:80]}...", "cyan")

        max_retries = 3
        audio_data = None

        for attempt in range(max_retries):
            audio_data = await browser.request_audio(chunk, voice_id)

            # Check for rate limit
            if audio_data == "RATE_LIMIT":
                # Check session health before presenting options
                health_ok = await browser.check_session_health()

                print_colored("\n" + "=" * 60, "yellow")
                print_colored("⏸️  RATE LIMIT REACHED", "yellow")
                print_colored("=" * 60, "yellow")
                print_colored("The API has rate-limited your requests.", "yellow")
                print_colored(f"Progress: {success_count}/{len(chunks)} chunks completed", "cyan")
                print_colored(f"Current: Chunk {i}/{len(chunks)}", "cyan")
                print_colored("\nOptions:", "yellow")
                if not health_ok:
                    print_colored("  1. Restart browser session (STRONGLY RECOMMENDED - poor health)", "green")
                else:
                    print_colored("  1. Restart browser session and solve CAPTCHA (recommended)", "green")
                print_colored("  2. Wait a few minutes and retry with same session", "yellow")
                print_colored("  3. Press Ctrl+C to stop and resume later", "red")
                print_colored("=" * 60, "yellow")

                while True:
                    choice = input_colored("\nChoice (1, 2, or 3): ", "blue").strip()
                    if choice == "1":
                        # Restart browser session - gets fresh cookies, bypasses rate limit
                        await browser.restart()
                        print_colored("🔄 Session restarted! Retrying chunk...", "green")
                        break
                    elif choice == "2":
                        # Wait and retry with same session (may not work if still rate-limited)
                        print_colored("⏳ Waiting... press Enter when ready to retry", "yellow")
                        input()
                        print_colored("🔄 Retrying...", "green")
                        break
                    elif choice == "3":
                        print_colored("⚠️  Press Ctrl+C to exit, or Enter to go back to menu", "yellow")
                        input()
                        # Loop back to menu
                        continue
                    else:
                        print_colored("Please enter 1, 2, or 3", "red")

                # Continue to next retry attempt
                continue

            if audio_data:
                # Save with document name prefix
                file_name = f"{output_name}-{i}.mp3"
                file_path = os.path.join(directory, file_name)

                with open(file_path, "wb") as f:
                    f.write(audio_data)

                size_kb = len(audio_data) / 1024
                print_colored(f"   ✅ Saved {file_name} ({size_kb:.1f} KB)", "green")
                success_count += 1
                break
            else:
                if attempt < max_retries - 1:
                    print_colored(f"   ⚠️  Retry {attempt + 1}/{max_retries}...", "yellow")
                    await asyncio.sleep(2)

        if not audio_data:
            print_colored(f"   ❌ Failed chunk {i}", "red")
            failed_chunks.append(i)

    # Final summary
    print_colored("\n" + "=" * 60, "cyan")
    print_colored("📊 CONVERSION SUMMARY", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored(f"✅ Successful: {success_count}/{len(chunks)} chunks", "green")

    if failed_chunks:
        print_colored(f"❌ Failed chunks: {failed_chunks}", "red")

    print_colored(f"📁 Output: {directory}", "cyan")
    print_colored(f"🎵 Files: {output_name}-1.mp3 through {output_name}-{len(chunks)}.mp3", "yellow")
    print_colored("=" * 60, "cyan")


async def main():
    """Main application"""

    print_colored("\n" + "=" * 60, "cyan")
    print_colored("📚 Audiobook Creator TTS - Document Mode", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored("Convert documents and ebooks to audio", "yellow")
    print_colored("Supported: PDF, EPUB, DOCX, TXT, HTML, Markdown, Plaintext", "yellow")
    print_colored("=" * 60, "cyan")

    # Check for Playwright browser (first-run setup)
    if not check_playwright_browser():
        print_colored("\n⚠️  Playwright browser not installed", "yellow")
        if not install_playwright_browser():
            print_colored("\n❌ Cannot proceed without Playwright browser", "red")
            print_colored("Please run: playwright install chromium", "yellow")
            return

    # Load voices
    voices = load_voices()
    if not voices:
        print_colored("❌ No voices available", "red")
        return

    stats = count_voice_stats(voices)
    print_colored(f"\n📊 Voice Library: {stats['total']} voices", "yellow")

    # Check for CLI argument (file path)
    cli_file_path = None
    if len(sys.argv) > 1:
        cli_file_path = sys.argv[1].strip().strip('"').strip("'")
        if os.path.exists(cli_file_path):
            print_colored(f"\n📄 File provided via CLI: {cli_file_path}", "green")
        else:
            print_colored(f"\n❌ File not found: {cli_file_path}", "red")
            cli_file_path = None

    # Initialize browser (one-time)
    browser = PersistentBrowser()

    try:
        await browser.initialize()

        # Main loop
        while True:
            print_colored("\n" + "=" * 60, "blue")
            print_colored("NEW CONVERSION", "blue")
            print_colored("=" * 60, "blue")

            # Determine input method
            file_path = None
            text = None
            output_name = None

            # Use CLI file path if provided (only on first iteration)
            if cli_file_path:
                file_path = cli_file_path
                cli_file_path = None  # Clear so it doesn't repeat
            else:
                # Present choice menu
                print_colored("\n📝 Input Method:", "cyan")
                print_colored("   1. Select file (opens file browser)", "green")
                print_colored("   2. Type or paste text", "green")
                print_colored("   3. Enter file path manually", "green")

                while True:
                    choice = input_colored("\nChoice (1, 2, or 3): ", "blue").strip()

                    if choice == "1":
                        # Open file browser
                        file_path = select_file_with_dialog()
                        if not file_path:
                            print_colored("File selection cancelled", "yellow")
                            continue
                        break
                    elif choice == "2":
                        # Get plaintext input
                        text, output_name = get_plaintext_input()
                        if not text:
                            print_colored("Text input cancelled", "yellow")
                            continue
                        break
                    elif choice == "3":
                        # Manual file path entry
                        manual_path = input_colored("\n📄 Enter document path: ", "green").strip()
                        # Strip quotes (both single and double)
                        manual_path = manual_path.strip('"').strip("'")
                        # Unescape common shell escape sequences
                        manual_path = manual_path.replace("\\ ", " ")  # spaces
                        manual_path = manual_path.replace("\\(", "(")  # parentheses
                        manual_path = manual_path.replace("\\)", ")")
                        manual_path = manual_path.replace("\\'", "'")  # single quotes
                        manual_path = manual_path.replace('\\"', '"')  # double quotes
                        manual_path = manual_path.replace("\\&", "&")  # ampersands
                        manual_path = manual_path.replace("\\;", ";")  # semicolons
                        manual_path = manual_path.replace("\\[", "[")  # brackets
                        manual_path = manual_path.replace("\\]", "]")

                        if not manual_path:
                            print_colored("Please enter a file path", "red")
                            continue

                        if not os.path.exists(manual_path):
                            print_colored(f"❌ File not found: {manual_path}", "red")
                            continue

                        file_path = manual_path
                        break
                    else:
                        print_colored("Please enter 1, 2, or 3", "red")

            # Process file or plaintext
            chapters = None  # For chapter-based processing
            text = None  # For text-based processing
            author = None  # For M4B metadata

            if file_path:
                # Validate file format
                suffix = Path(file_path).suffix.lower()
                supported_formats = [".pdf", ".epub", ".docx", ".txt", ".html", ".htm", ".md", ".markdown"]
                if suffix not in supported_formats:
                    print_colored(f"❌ Unsupported format: {suffix}", "red")
                    print_colored("Supported: .pdf, .epub, .docx, .txt, .html, .htm, .md, .markdown", "yellow")
                    continue

                # Get output name from filename
                base_name = Path(file_path).stem
                # Clean filename for output (lowercase, alphanumeric only)
                output_name = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")

                # Extract text or chapters based on format
                print_colored(f"\n{'='*60}", "cyan")

                if suffix == ".epub":
                    # Extract chapters from EPUB
                    chapters = DocumentParser.extract_chapters_from_epub(file_path)
                    if not chapters:
                        print_colored("❌ No chapters extracted from EPUB", "red")
                        continue

                    # Extract author from EPUB metadata
                    author = DocumentParser.extract_author_from_epub(file_path)

                    # Remove author name from output_name if present
                    if author:
                        # Convert author to sanitized format (same as output_name)
                        author_sanitized = re.sub(r"[^a-z0-9]+", "-", author.lower()).strip("-")
                        # Remove author from end of output_name if present
                        if output_name.endswith("-" + author_sanitized):
                            output_name = output_name[: -(len(author_sanitized) + 1)]
                        elif output_name.endswith(author_sanitized):
                            output_name = output_name[: -len(author_sanitized)]
                elif suffix == ".pdf":
                    # Extract chapters from PDF
                    chapters = DocumentParser.extract_chapters_from_pdf(file_path)
                    if not chapters:
                        print_colored("❌ No chapters extracted from PDF", "red")
                        continue
                else:
                    # Use legacy text extraction for other formats
                    text = DocumentParser.parse_document(file_path)
                    if not text or len(text) < 10:
                        print_colored("❌ No text extracted or text too short", "red")
                        continue

                print_colored(f"{'='*60}", "cyan")

            elif text and output_name:
                # Plaintext input already has text and output_name set
                pass
            else:
                # Should not reach here
                print_colored("❌ No valid input provided", "red")
                continue

            # Show preview and statistics
            if chapters:
                # Chapter-based preview
                total_chars = sum(len(ch.text) for ch in chapters)
                print_colored(f"\n📚 Extracted {len(chapters)} chapters", "yellow")
                print_colored(f"📏 Total characters: {total_chars:,}", "yellow")

                # Show first few chapters
                print_colored(f"\n📖 Chapter List:", "cyan")
                for ch in chapters[:5]:
                    if ch.dir_name.startswith("00-"):
                        print_colored(f"   • {ch.title} ({len(ch.text):,} chars)", "yellow")
                    else:
                        dir_prefix = ch.dir_name.split("-")[0]
                        print_colored(f"   {dir_prefix}. {ch.title} ({len(ch.text):,} chars)", "yellow")

                if len(chapters) > 5:
                    print_colored(f"   ... and {len(chapters) - 5} more chapters", "yellow")

                # Estimate chunks
                estimated_chunks = (total_chars // 1000) + len(chapters)
                print_colored(f"🔢 Estimated chunks: ~{estimated_chunks}", "yellow")
            else:
                # Text-based preview
                preview = text[:200].replace("\n", " ")
                print_colored(f"\n📝 Text preview:", "yellow")
                print(f"   {preview}...")
                print_colored(f"\n📏 Total characters: {len(text):,}", "yellow")

                # Estimate chunks
                estimated_chunks = (len(text) // 1000) + 1
                print_colored(f"🔢 Estimated chunks: ~{estimated_chunks}", "yellow")

            # Confirm
            confirm = input_colored(f"\nProceed with conversion? (y/n): ", "blue").lower()
            if confirm != "y":
                continue

            # Use interactive voice selection
            voice_id, voice_name = select_voice_interactive(voices)
            if not voice_id:
                print_colored("Voice selection cancelled.", "yellow")
                continue

            if chapters:
                print_colored(f"\n🎵 Chapter-based output with nested directories", "cyan")
                print_colored(f"   Each chapter will have its own subdirectory", "yellow")
            else:
                print_colored(
                    f"\n🎵 Output files will be named: {output_name}-1.mp3, {output_name}-2.mp3, etc.", "cyan"
                )

            # Use optimal chunk size for API efficiency and natural speech flow
            chunk_size = 2000
            print_colored(f"✅ Using chunk size: {chunk_size} characters (optimal for performance)", "green")

            # Prompt for author if processing chapters (for M4B metadata)
            cover_image_path = None
            if chapters:
                author = prompt_for_author(author)

                # Prompt for cover art before processing (so user doesn't have to wait)
                print_colored(f"\n📖 Preparing to create M4B audiobook with metadata:", "cyan")
                print_colored(f"   Title: {kebab_to_title_case(output_name)}", "yellow")
                print_colored(f"   Author: {author}", "yellow")
                cover_image_path = prompt_for_cover_art(os.path.join("audio", output_name))

            # Process document (chapter-based or text-based)
            if chapters:
                await process_chapters_to_speech(
                    browser, voice_id, chapters, output_name, chunk_size, author, cover_image_path
                )
            else:
                await process_document_to_speech(browser, voice_id, text, output_name, chunk_size)

            # Continue?
            while True:
                choice = input_colored("\n🔄 Convert another document? (y/n): ", "blue").lower()
                if choice == "y":
                    break
                elif choice == "n":
                    print_colored("\n👋 Goodbye!", "magenta")
                    return
                else:
                    print_colored("Please enter 'y' or 'n'", "red")

    finally:
        print_colored("\n🔒 Closing browser...", "cyan")
        await browser.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Exiting...", "yellow")
