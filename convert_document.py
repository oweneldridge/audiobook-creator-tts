#!/usr/bin/env python3.11
"""
Convert documents with any voice ID (Chapter-aware version with M4B audiobook output)
Usage: python3.11 convert_document.py [-y|--yes] <voice-id> <file-path>
Example: python3.11 convert_document.py voice-111 ~/Documents/macbeth.epub
Output: Chapter-organized MP3s + single M4B audiobook with chapter navigation

Backend follows TTS_BACKEND (kokoro|speechma). With -y/--yes all confirmation
prompts are skipped, making this the headless entrypoint for automation.
"""
import asyncio
import sys
from pathlib import Path
from main_document_mode import (
    DocumentParser,
    process_chapters_to_speech,
    print_colored,
    check_ffmpeg_installed,
    show_ffmpeg_install_instructions,
)
from tts_backend import make_backend


async def convert_document(voice_id: str, file_path: str, auto_yes: bool = False):
    print_colored("\n" + "=" * 60, "cyan")
    print_colored("Document to Audio Converter (Chapter Mode)", "magenta")
    print_colored("=" * 60, "cyan")

    # Check for ffmpeg
    ffmpeg_available = check_ffmpeg_installed()
    if not ffmpeg_available:
        show_ffmpeg_install_instructions()
        if auto_yes:
            print_colored("\n--yes: continuing without MP3 concatenation", "yellow")
        else:
            confirm = input("\nContinue without MP3 concatenation? (y/n): ").lower()
            if confirm != "y":
                print_colored("\nCancelled", "yellow")
                return
    else:
        print_colored("✅ ffmpeg detected - chapters will be concatenated and M4B audiobook will be created", "green")

    # Detect file type and extract chapters
    file_path_obj = Path(file_path)
    suffix = file_path_obj.suffix.lower()

    if suffix == ".epub":
        chapters = DocumentParser.extract_chapters_from_epub(file_path)
    elif suffix == ".pdf":
        chapters = DocumentParser.extract_chapters_from_pdf(file_path)
    else:
        print_colored(f"\n❌ Unsupported file type: {suffix}", "red")
        print_colored("Supported formats: .epub, .pdf", "yellow")
        return

    if not chapters:
        print_colored("\n❌ No chapters extracted", "red")
        return

    # Get filename for output
    base_name = file_path_obj.stem
    import re

    output_name = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")

    # Calculate total characters
    total_chars = sum(len(ch.text) for ch in chapters)

    print_colored(f"\nVoice ID: {voice_id}", "green")
    print_colored(f"File: {file_path_obj.name}", "yellow")
    print_colored(f"Chapters: {len(chapters)}", "yellow")
    print_colored(f"Total characters: {total_chars:,}", "yellow")

    # Show chapter preview
    print_colored(f"\nChapter structure:", "cyan")
    for ch in chapters[:5]:  # Show first 5
        print_colored(f"   {ch.number:02d}. {ch.title}", "yellow")
    if len(chapters) > 5:
        print_colored(f"   ... and {len(chapters) - 5} more chapters", "yellow")

    # Estimate chunks
    estimated_chunks = (total_chars // 1000) + 1
    print_colored(f"\nEstimated total chunks: ~{estimated_chunks}", "yellow")

    # Confirm
    if not auto_yes:
        confirm = input("\nStart conversion? (y/n): ").lower()
        if confirm != "y":
            print_colored("Cancelled", "yellow")
            return

    # Initialize TTS backend (Kokoro or speechma, per TTS_BACKEND)
    browser = make_backend()

    try:
        await browser.initialize()
        await process_chapters_to_speech(browser, voice_id, chapters, output_name, chunk_size=1000)
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\nConvert EPUB/PDF to Audio with Custom Voice")
        print("=" * 60)
        print("\nUsage:")
        print(f"  python3.11 {sys.argv[0]} <voice-id> <file-path>")
        print("\nExamples:")
        print(f"  python3.11 {sys.argv[0]} voice-111 ~/Documents/book.epub")
        print(f"  python3.11 {sys.argv[0]} voice-18 ~/Documents/macbeth.epub")
        print("\nOutput:")
        print("  • Chapter-organized MP3 files in nested directories")
        print("  • Single M4B audiobook with chapter navigation (requires ffmpeg)")
        print("\nKnown Voice IDs:")
        print("  voice-111 - Ava (English US Female)")
        print("  voice-18  - Unknown (test to find out)")
        print("\n" + "=" * 60)
        sys.exit(1)

    auto_yes = any(a in ("-y", "--yes") for a in sys.argv[1:])
    args = [a for a in sys.argv[1:] if a not in ("-y", "--yes")]
    voice_id = args[0]
    file_path = args[1].strip('"').strip("'")

    try:
        asyncio.run(convert_document(voice_id, file_path, auto_yes=auto_yes))
    except KeyboardInterrupt:
        print_colored("\n\nCancelled", "yellow")
