#!/usr/bin/env python3.11
"""
Parallel Coordinator - Manages worker distribution, progress tracking, and coordination
"""
import asyncio
import math
import os
import sys
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(__file__))
from main import print_colored


@dataclass
class WorkerProgress:
    """Progress data for a single worker"""

    worker_id: int
    total_chunks: int
    completed_chunks: int
    failed_chunks: int
    status: str  # "initializing", "working", "captcha", "failed", "completed"
    last_update_time: float


class ParallelCoordinator:
    """
    Coordinates multiple worker browsers for parallel processing

    Responsibilities:
    - Distribute chunks across workers (round-robin)
    - Track progress for each worker
    - Display real-time progress dashboard
    - Monitor worker health
    - Aggregate statistics
    """

    def __init__(self, total_chunks: int, num_workers: int):
        """
        Initialize coordinator

        Args:
            total_chunks: Total number of chunks to process
            num_workers: Number of worker processes to spawn
        """
        self.total_chunks = total_chunks
        self.num_workers = num_workers

        # Chunk assignments: worker_id -> [(chunk_idx, chunk_text), ...]
        self.chunk_assignments: Dict[int, List[Tuple[int, str]]] = {}

        # Worker progress tracking
        self.worker_progress: Dict[int, WorkerProgress] = {}

        # Overall statistics
        self.overall_completed = 0
        self.overall_failed = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Initialize worker progress tracking
        for worker_id in range(1, num_workers + 1):
            self.worker_progress[worker_id] = WorkerProgress(
                worker_id=worker_id,
                total_chunks=0,  # Will be set after chunk distribution
                completed_chunks=0,
                failed_chunks=0,
                status="initializing",
                last_update_time=time.time(),
            )

    def distribute_chunks(self, chunks: List[Tuple[int, str]]):
        """
        Distribute chunks across workers using round-robin algorithm

        Round-robin ensures even distribution and resilience:
        - If one worker fails, only scattered chunks are lost (not contiguous block)
        - Each worker gets roughly equal workload

        Example (12 chunks, 3 workers):
        Worker 1: chunks [1, 4, 7, 10]
        Worker 2: chunks [2, 5, 8, 11]
        Worker 3: chunks [3, 6, 9, 12]

        Args:
            chunks: List of (chunk_index, chunk_text) tuples to distribute
        """
        # Initialize empty lists for each worker
        for worker_id in range(1, self.num_workers + 1):
            self.chunk_assignments[worker_id] = []

        # Round-robin distribution
        for idx, chunk_data in enumerate(chunks):
            worker_id = (idx % self.num_workers) + 1  # Worker IDs start at 1
            self.chunk_assignments[worker_id].append(chunk_data)

        # Update worker progress with chunk counts
        for worker_id, assigned_chunks in self.chunk_assignments.items():
            self.worker_progress[worker_id].total_chunks = len(assigned_chunks)

        # Log distribution
        print_colored(f"\n📊 Chunk Distribution (Round-Robin):", "cyan")
        for worker_id in range(1, self.num_workers + 1):
            chunk_count = len(self.chunk_assignments[worker_id])
            # Handle both (idx, text) and (idx, text, chapter) tuple formats
            first_chunks = self.chunk_assignments[worker_id][:3]
            chunk_indices = [c[0] for c in first_chunks]
            preview = (
                f"{chunk_indices[0]}, {chunk_indices[1]}, {chunk_indices[2]}, ..."
                if len(chunk_indices) >= 3
                else str(chunk_indices)
            )
            print_colored(f"   Worker #{worker_id}: {chunk_count} chunks (starting with: {preview})", "yellow")

    def get_worker_assignment(self, worker_id: int) -> List[Tuple[int, str]]:
        """
        Get chunk assignment for specific worker

        Args:
            worker_id: Worker ID (1-indexed)

        Returns:
            List of (chunk_index, chunk_text) tuples assigned to this worker
        """
        return self.chunk_assignments.get(worker_id, [])

    def update_worker_progress(self, worker_id: int, completed: int, failed: int, status: str):
        """
        Update progress for a specific worker

        Args:
            worker_id: Worker ID (1-indexed)
            completed: Number of completed chunks
            failed: Number of failed chunks
            status: Current worker status
        """
        if worker_id in self.worker_progress:
            progress = self.worker_progress[worker_id]
            progress.completed_chunks = completed
            progress.failed_chunks = failed
            progress.status = status
            progress.last_update_time = time.time()

            # Update overall statistics
            self._update_overall_stats()

    def _update_overall_stats(self):
        """Recalculate overall statistics from all workers"""
        self.overall_completed = sum(p.completed_chunks for p in self.worker_progress.values())
        self.overall_failed = sum(p.failed_chunks for p in self.worker_progress.values())

    def mark_worker_started(self, worker_id: int):
        """Mark worker as started and begin timing"""
        if self.start_time is None:
            self.start_time = time.time()

        if worker_id in self.worker_progress:
            self.worker_progress[worker_id].status = "working"

    def mark_worker_completed(self, worker_id: int):
        """Mark worker as completed"""
        if worker_id in self.worker_progress:
            self.worker_progress[worker_id].status = "completed"

        # Check if all workers completed
        if all(p.status == "completed" for p in self.worker_progress.values()):
            self.end_time = time.time()

    def mark_worker_failed(self, worker_id: int):
        """Mark worker as failed"""
        if worker_id in self.worker_progress:
            self.worker_progress[worker_id].status = "failed"

    def mark_worker_captcha(self, worker_id: int):
        """Mark worker as waiting for CAPTCHA"""
        if worker_id in self.worker_progress:
            self.worker_progress[worker_id].status = "captcha"

    def get_progress_bar(self, completed: int, total: int, width: int = 20) -> str:
        """
        Generate ASCII progress bar

        Args:
            completed: Number of completed items
            total: Total number of items
            width: Width of progress bar in characters

        Returns:
            Progress bar string (e.g., "[████████░░░░░░░░░░░░]")
        """
        if total == 0:
            return "[" + "░" * width + "]"

        filled = int((completed / total) * width)
        empty = width - filled
        return "[" + "█" * filled + "░" * empty + "]"

    def get_status_emoji(self, status: str) -> str:
        """Get emoji for worker status"""
        status_emojis = {"initializing": "🔄", "working": "✅", "captcha": "⏸️", "failed": "❌", "completed": "🎉"}
        return status_emojis.get(status, "❓")

    def render_progress_dashboard(self):
        """
        Render real-time progress dashboard showing all workers

        Dashboard format:
        ╔════════════════════════════════════════════════════════════╗
        ║  📊 PARALLEL CONVERSION PROGRESS                          ║
        ╠════════════════════════════════════════════════════════════╣
        ║  Total: 636 | Workers: 12 | Completed: 312/636 (49%)     ║
        ║  Failed: 0 | ETA: 8 min                                   ║
        ╠════════════════════════════════════════════════════════════╣
        ║  Worker #1  [████████████░░░░░░░░] 28/53  ✅ Working     ║
        ║  Worker #2  [██████████████░░░░░░] 32/53  ⏸️  CAPTCHA    ║
        ║  ...                                                      ║
        ╚════════════════════════════════════════════════════════════╝
        """
        # Clear screen (ANSI escape code)
        print("\033[2J\033[H")

        # Header
        print_colored("╔" + "═" * 60 + "╗", "cyan")
        print_colored("║  📊 PARALLEL CONVERSION PROGRESS" + " " * 27 + "║", "cyan")
        print_colored("╠" + "═" * 60 + "╣", "cyan")

        # Overall statistics
        percent = int((self.overall_completed / self.total_chunks) * 100) if self.total_chunks > 0 else 0
        eta = self._calculate_eta()

        stats_line1 = f"  Total: {self.total_chunks} | Workers: {self.num_workers} | Completed: {self.overall_completed}/{self.total_chunks} ({percent}%)"
        stats_line2 = f"  Failed: {self.overall_failed} | ETA: {eta}"

        print_colored("║" + stats_line1 + " " * (60 - len(stats_line1)) + "║", "yellow")
        print_colored("║" + stats_line2 + " " * (60 - len(stats_line2)) + "║", "yellow")
        print_colored("╠" + "═" * 60 + "╣", "cyan")

        # Worker progress bars
        for worker_id in sorted(self.worker_progress.keys()):
            progress = self.worker_progress[worker_id]

            # Progress bar
            bar = self.get_progress_bar(progress.completed_chunks, progress.total_chunks, width=20)

            # Status
            status_emoji = self.get_status_emoji(progress.status)
            status_text = progress.status.capitalize()

            # Worker line
            worker_line = f"  Worker #{worker_id:2d}  {bar} {progress.completed_chunks:3d}/{progress.total_chunks:3d}  {status_emoji} {status_text}"

            # Color based on status
            color = "green"
            if progress.status == "captcha":
                color = "yellow"
            elif progress.status == "failed":
                color = "red"
            elif progress.status == "completed":
                color = "magenta"

            print_colored("║" + worker_line + " " * (60 - len(worker_line)) + "║", color)

        # Footer
        print_colored("╚" + "═" * 60 + "╝", "cyan")

        # CAPTCHA alerts
        captcha_workers = [worker_id for worker_id, p in self.worker_progress.items() if p.status == "captcha"]
        if captcha_workers:
            print_colored(f"\n🔔 Workers need CAPTCHA: {', '.join(f'#{w}' for w in captcha_workers)}", "yellow")

    def _calculate_eta(self) -> str:
        """
        Calculate estimated time to completion

        Returns:
            ETA string (e.g., "5 min", "2 hr 15 min", "Complete!")
        """
        if self.overall_completed == self.total_chunks:
            return "Complete!"

        if self.start_time is None or self.overall_completed == 0:
            return "Calculating..."

        elapsed = time.time() - self.start_time
        chunks_per_second = self.overall_completed / elapsed
        remaining_chunks = self.total_chunks - self.overall_completed

        if chunks_per_second == 0:
            return "Unknown"

        eta_seconds = remaining_chunks / chunks_per_second

        # Format ETA
        if eta_seconds < 60:
            return f"{int(eta_seconds)} sec"
        elif eta_seconds < 3600:
            return f"{int(eta_seconds / 60)} min"
        else:
            hours = int(eta_seconds / 3600)
            minutes = int((eta_seconds % 3600) / 60)
            return f"{hours} hr {minutes} min"

    def get_summary_stats(self) -> dict:
        """
        Get final summary statistics

        Returns:
            Dictionary with:
            - total_chunks: int
            - completed_chunks: int
            - failed_chunks: int
            - duration_seconds: float
            - workers_succeeded: int
            - workers_failed: int
        """
        duration = 0
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time

        workers_succeeded = sum(1 for p in self.worker_progress.values() if p.status == "completed")
        workers_failed = sum(1 for p in self.worker_progress.values() if p.status == "failed")

        return {
            "total_chunks": self.total_chunks,
            "completed_chunks": self.overall_completed,
            "failed_chunks": self.overall_failed,
            "duration_seconds": duration,
            "workers_succeeded": workers_succeeded,
            "workers_failed": workers_failed,
        }

    def print_final_summary(self):
        """Print final summary after all workers complete"""
        stats = self.get_summary_stats()

        print_colored("\n" + "=" * 60, "cyan")
        print_colored("📊 PARALLEL CONVERSION SUMMARY", "magenta")
        print_colored("=" * 60, "cyan")

        # Overall stats
        success_rate = (
            int((stats["completed_chunks"] / stats["total_chunks"]) * 100) if stats["total_chunks"] > 0 else 0
        )
        print_colored(
            f"✅ Completed: {stats['completed_chunks']}/{stats['total_chunks']} chunks ({success_rate}%)", "green"
        )

        if stats["failed_chunks"] > 0:
            print_colored(f"❌ Failed: {stats['failed_chunks']} chunks", "red")

        # Duration
        duration_min = int(stats["duration_seconds"] / 60)
        duration_sec = int(stats["duration_seconds"] % 60)
        print_colored(f"⏱️  Duration: {duration_min} min {duration_sec} sec", "yellow")

        # Worker stats
        print_colored(f"\n👷 Workers: {self.num_workers} total", "cyan")
        print_colored(f"   ✅ Succeeded: {stats['workers_succeeded']}", "green")
        if stats["workers_failed"] > 0:
            print_colored(f"   ❌ Failed: {stats['workers_failed']}", "red")

        print_colored("=" * 60, "cyan")

    def get_all_failed_chunks(self) -> List[int]:
        """
        Collect all failed chunk indices from all workers

        Returns:
            List of failed chunk indices
        """
        failed_chunks = []
        for worker_id, assigned_chunks in self.chunk_assignments.items():
            progress = self.worker_progress[worker_id]
            # Get indices of chunks that were assigned but not completed
            assigned_indices = set(chunk[0] for chunk in assigned_chunks)
            completed_indices = set()  # Would need to track this during processing
            # For now, rely on worker progress tracking
            if progress.failed_chunks > 0:
                # This is a count, not indices - would need to enhance tracking
                pass

        return failed_chunks
