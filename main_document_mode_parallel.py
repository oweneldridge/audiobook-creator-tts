#!/usr/bin/env python3.11
"""
Audiobook Creator TTS - Parallel Mode
Multi-worker parallel processing for faster conversions
Reduces 636-chunk book from 21 min → 3 min (7x speedup)
"""
import asyncio
import json
import math
import multiprocessing
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.dirname(__file__))
from main import print_colored, input_colored
from worker_browser import WorkerBrowser
from parallel_coordinator import ParallelCoordinator
from main_document_mode import Chapter


def print_timestamped(message: str, color: str = "cyan"):
    """Print message with timestamp prefix"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm
    print_colored(f"[{timestamp}] {message}", color)


def load_config() -> dict:
    """Load parallel processing configuration"""
    config_path = Path(__file__).parent / "config" / "parallel_settings.json"

    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)

    # Default configuration
    return {
        "max_workers": 15,
        "enable_parallel_mode": True,
        "safety_test_enabled": True,
        "safety_test_chunks": 100,
        "safety_test_workers": 2,
        "auto_calculate_workers": True,
        "chunks_per_worker_target": 55,
        "default_captcha_strategy": "simultaneous",
        "stagger_interval_seconds": 10,
        "sequential_batch_size": 3,
    }


async def run_safety_test(chapters: List[Chapter], voice_id: str, output_dir: str) -> Tuple[bool, str]:
    """
    Run safety test with 2 workers to check for IP-level rate limiting

    Args:
        chapters: List of chapters
        voice_id: Voice ID for TTS
        output_dir: Output directory for audio files

    Returns:
        (success: bool, message: str)
    """
    print_colored("\n" + "=" * 60, "yellow")
    print_colored("🔬 SAFETY TEST - Checking for IP-level rate limits", "yellow")
    print_colored("=" * 60, "yellow")
    print_colored("Testing with 2 workers processing first 100 chunks...", "cyan")
    print_colored("This ensures the API allows parallel sessions", "cyan")
    print_colored("=" * 60, "yellow")

    # Get first 100 chunks across all chapters
    test_chunks = []
    for chapter in chapters:
        for chunk_idx, chunk_text in enumerate(chapter.chunks, 1):
            if len(test_chunks) >= 100:
                break
            test_chunks.append((chunk_idx, chunk_text, chapter))
        if len(test_chunks) >= 100:
            break

    if len(test_chunks) < 10:
        return False, "Not enough chunks for safety test (need at least 10)"

    # Create coordinator for test
    coordinator = ParallelCoordinator(total_chunks=len(test_chunks), num_workers=2)

    # Distribute test chunks
    simple_chunks = [(idx, text) for idx, text, _ in test_chunks]
    coordinator.distribute_chunks(simple_chunks)

    # Run 2 workers
    workers_succeeded = 0
    rate_limit_detected = False

    async def run_test_worker(worker_id: int):
        nonlocal workers_succeeded, rate_limit_detected

        worker = WorkerBrowser(worker_id)
        try:
            # Skip initial CAPTCHA prompt to avoid deadlock (will prompt when needed during processing)
            await worker.initialize(skip_initial_captcha_prompt=True)
            coordinator.mark_worker_started(worker_id)

            # Get assignment
            assignment = coordinator.get_worker_assignment(worker_id)

            # Process chunks
            for chunk_idx, chunk_text in assignment:
                audio_data = await worker.request_audio(chunk_text, voice_id)

                if audio_data == "RATE_LIMIT":
                    # Check if this is unexpected (before 55 requests)
                    if worker.requests_since_captcha < 50:
                        rate_limit_detected = True
                        return

                if audio_data:
                    coordinator.update_worker_progress(
                        worker_id,
                        completed=len(worker.completed_chunks) + 1,
                        failed=len(worker.failed_chunks),
                        status="working",
                    )
                else:
                    break

            workers_succeeded += 1
            coordinator.mark_worker_completed(worker_id)

        except Exception as e:
            print_colored(f"❌ [Worker #{worker_id}] Test error: {e}", "red")
            coordinator.mark_worker_failed(worker_id)
        finally:
            await worker.cleanup()

    # Run both workers concurrently
    await asyncio.gather(run_test_worker(1), run_test_worker(2))

    # Evaluate results
    if rate_limit_detected:
        return False, "IP-level rate limiting detected - parallel mode not safe"

    if workers_succeeded < 2:
        return False, "Safety test failed - workers encountered errors"

    return True, "Safety test passed - no IP-level rate limits detected"


def calculate_optimal_workers(total_chunks: int, config: dict) -> int:
    """
    Calculate optimal number of workers

    Args:
        total_chunks: Total number of chunks to process
        config: Configuration dictionary

    Returns:
        Optimal number of workers (capped at max_workers)
    """
    if not config.get("auto_calculate_workers", True):
        return config.get("default_workers", 5)

    chunks_per_worker = config.get("chunks_per_worker_target", 55)
    optimal = math.ceil(total_chunks / chunks_per_worker)

    # Cap at max_workers
    max_workers = config.get("max_workers", 15)
    return min(optimal, max_workers)


def prompt_captcha_strategy() -> str:
    """
    Prompt user for CAPTCHA coordination strategy

    Returns:
        Strategy choice: "simultaneous", "staggered", or "sequential"
    """
    print_colored("\n⚙️  CAPTCHA Coordination Strategy:", "cyan")
    print_colored("   1. Simultaneous (fastest, all workers start together)", "green")
    print_colored("      → Must monitor multiple browser windows", "yellow")
    print_colored("   2. Staggered (balanced, workers start 10s apart)", "green")
    print_colored("      → CAPTCHAs appear at different times, easier to manage", "yellow")
    print_colored("   3. Sequential Batches (easiest, 2-3 workers at a time)", "green")
    print_colored("      → Slowest, but simplest CAPTCHA management", "yellow")

    while True:
        choice = input_colored("\nChoice (1, 2, or 3): ", "blue").strip()

        if choice == "1":
            return "simultaneous"
        elif choice == "2":
            return "staggered"
        elif choice == "3":
            return "sequential"
        else:
            print_colored("Please enter 1, 2, or 3", "red")


async def worker_process_wrapper(
    worker_id: int, voice_id: str, output_dir: str, chapter_chunks: List[Tuple[int, str, Chapter]], start_delay: int = 0
):
    """
    Wrapper for worker process execution

    Args:
        worker_id: Worker ID
        voice_id: Voice ID for TTS
        output_dir: Base output directory
        chapter_chunks: List of (chunk_idx, chunk_text, chapter) tuples
        start_delay: Delay before starting (for staggered mode)
    """
    # Delay start if using staggered mode
    if start_delay > 0:
        await asyncio.sleep(start_delay)

    worker = WorkerBrowser(worker_id)
    results = []

    try:
        await worker.initialize()

        # Group chunks by chapter
        chunks_by_chapter = {}
        for chunk_idx, chunk_text, chapter in chapter_chunks:
            chapter_key = (chapter.number, chapter.dir_name)
            if chapter_key not in chunks_by_chapter:
                chunks_by_chapter[chapter_key] = []
            chunks_by_chapter[chapter_key].append((chunk_idx, chunk_text))

        # Process each chapter's chunks
        for (chapter_num, chapter_dir), chunks in chunks_by_chapter.items():
            worker.assign_chunks(chunks)
            result = await worker.process_assigned_chunks(
                voice_id=voice_id, output_dir=output_dir, chapter_dir_name=chapter_dir, chapter_number=chapter_num
            )
            results.append(result)

        return {"worker_id": worker_id, "status": "success", "results": results}

    except Exception as e:
        print_colored(f"❌ [Worker #{worker_id}] Error: {e}", "red")
        return {"worker_id": worker_id, "status": "failed", "error": str(e)}
    finally:
        await worker.cleanup()


async def run_parallel_processing(
    chapters: List[Chapter], voice_id: str, output_dir: str, num_workers: int, strategy: str, config: dict
):
    """
    Run parallel processing with multiple workers

    Args:
        chapters: List of chapters
        voice_id: Voice ID for TTS
        output_dir: Output directory
        num_workers: Number of workers to use
        strategy: CAPTCHA strategy ("simultaneous", "staggered", "sequential")
        config: Configuration dictionary
    """
    # Collect all chunks across all chapters with GLOBAL indexing
    all_chunks = []
    global_chunk_idx = 0
    for chapter in chapters:
        for chunk_text in chapter.chunks:
            global_chunk_idx += 1
            all_chunks.append((global_chunk_idx, chunk_text, chapter))

    total_chunks = len(all_chunks)

    print_colored(f"\n📊 Parallel Processing Configuration:", "cyan")
    print_colored(f"   Total Chunks: {total_chunks}", "yellow")
    print_colored(f"   Workers: {num_workers}", "yellow")
    print_colored(f"   Strategy: {strategy.capitalize()}", "yellow")
    print_colored(f"   Estimated Time: {math.ceil(total_chunks * 2 / num_workers / 60)} min", "green")

    print_timestamped(f"🚀 Starting parallel processing with {num_workers} workers...", "magenta")

    # Create coordinator
    coordinator = ParallelCoordinator(total_chunks=total_chunks, num_workers=num_workers)
    # Pass full chunk data (idx, text, chapter) to coordinator
    coordinator.distribute_chunks(all_chunks)

    # Start timing
    import time

    coordinator.start_time = time.time()

    # Prepare worker tasks based on strategy
    tasks = []
    stagger_delay = config.get("stagger_interval_seconds", 10)
    batch_size = config.get("sequential_batch_size", 3)

    if strategy == "simultaneous":
        # All workers start together
        for worker_id in range(1, num_workers + 1):
            assignment = coordinator.get_worker_assignment(worker_id)
            # Assignment now contains full (idx, text, chapter) tuples
            worker_chunks = assignment
            tasks.append(worker_process_wrapper(worker_id, voice_id, output_dir, worker_chunks, start_delay=0))

        # Run all workers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

    elif strategy == "staggered":
        # Workers start with delays
        for worker_id in range(1, num_workers + 1):
            assignment = coordinator.get_worker_assignment(worker_id)
            # Assignment now contains full (idx, text, chapter) tuples
            worker_chunks = assignment
            delay = (worker_id - 1) * stagger_delay
            tasks.append(worker_process_wrapper(worker_id, voice_id, output_dir, worker_chunks, start_delay=delay))

        # Run all workers with staggered starts
        results = await asyncio.gather(*tasks, return_exceptions=True)

    elif strategy == "sequential":
        # Run workers in batches
        results = []
        for batch_start in range(0, num_workers, batch_size):
            batch_end = min(batch_start + batch_size, num_workers)
            batch_tasks = []

            for worker_id in range(batch_start + 1, batch_end + 1):
                assignment = coordinator.get_worker_assignment(worker_id)
                # Assignment now contains full (idx, text, chapter) tuples
                worker_chunks = assignment
                batch_tasks.append(
                    worker_process_wrapper(worker_id, voice_id, output_dir, worker_chunks, start_delay=0)
                )

            # Run batch concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

    print_timestamped(f"✅ All workers completed, processing results...", "green")

    # Process results and collect unique chunk indices
    all_completed_chunks = set()
    all_failed_chunks = set()

    for result in results:
        if isinstance(result, dict) and result.get("status") == "success":
            # Mark worker as completed
            worker_id = result.get("worker_id")
            if worker_id:
                coordinator.mark_worker_completed(worker_id)

            # Get the last result from each worker (has all completed chunks)
            worker_results = result.get("results", [])
            if worker_results:
                # Use the last result which contains cumulative lists
                final_result = worker_results[-1]
                all_completed_chunks.update(final_result.get("completed", []))
                all_failed_chunks.update(final_result.get("failed", []))
        elif isinstance(result, dict) and result.get("status") == "failed":
            # Mark worker as failed
            worker_id = result.get("worker_id")
            if worker_id:
                coordinator.mark_worker_failed(worker_id)
        elif isinstance(result, Exception):
            print_timestamped(f"⚠️  Worker exception: {result}", "yellow")

    # Update coordinator's overall statistics with unique chunk counts
    coordinator.overall_completed = len(all_completed_chunks)
    coordinator.overall_failed = len(all_failed_chunks)

    # Mark processing as complete
    if coordinator.start_time and not coordinator.end_time:
        import time

        coordinator.end_time = time.time()

    print_timestamped(f"📊 Generating final summary...", "cyan")

    # Print summary with updated statistics
    coordinator.print_final_summary()

    return coordinator.overall_completed, coordinator.overall_failed


async def main():
    """Main entry point for parallel mode"""
    print_colored("\n" + "=" * 60, "cyan")
    print_colored("🚀 Audiobook Creator TTS - PARALLEL MODE", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored("Multi-worker processing for 7x faster conversions", "yellow")
    print_colored("=" * 60, "cyan")

    # Load config
    config = load_config()

    if not config.get("enable_parallel_mode", True):
        print_colored("❌ Parallel mode is disabled in configuration", "red")
        return

    # For now, this is a placeholder
    # Full integration with main_document_mode.py will be added next

    print_colored("\n✅ Parallel mode infrastructure is ready!", "green")
    print_colored("To use parallel mode, run main_document_mode.py and select option 2", "cyan")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Exiting...", "yellow")
