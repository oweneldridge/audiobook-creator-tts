"""
Unit tests for parallel_coordinator.py
Tests for ParallelCoordinator class and worker management
"""

import pytest
import time


class TestParallelCoordinatorInit:
    """Tests for ParallelCoordinator initialization"""

    def test_init_basic(self) -> None:
        """Test basic initialization"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=5)

        assert coordinator.total_chunks == 100
        assert coordinator.num_workers == 5
        assert coordinator.overall_completed == 0
        assert coordinator.overall_failed == 0
        assert coordinator.start_time is None
        assert coordinator.end_time is None
        assert len(coordinator.worker_progress) == 5
        assert len(coordinator.chunk_assignments) == 0

    def test_init_worker_progress_structure(self) -> None:
        """Test worker progress initialization"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=50, num_workers=3)

        for worker_id in range(1, 4):
            progress = coordinator.worker_progress[worker_id]
            assert progress.worker_id == worker_id
            assert progress.total_chunks == 0  # Set after distribution
            assert progress.completed_chunks == 0
            assert progress.failed_chunks == 0
            assert progress.status == "initializing"
            assert isinstance(progress.last_update_time, float)


class TestChunkDistribution:
    """Tests for chunk distribution logic"""

    def test_distribute_chunks_round_robin(self) -> None:
        """Test round-robin chunk distribution"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=12, num_workers=3)

        chunks = [(i, f"chunk_{i}") for i in range(1, 13)]
        coordinator.distribute_chunks(chunks)

        # Worker 1 should get chunks 1, 4, 7, 10
        assert coordinator.chunk_assignments[1] == [(1, "chunk_1"), (4, "chunk_4"), (7, "chunk_7"), (10, "chunk_10")]
        # Worker 2 should get chunks 2, 5, 8, 11
        assert coordinator.chunk_assignments[2] == [(2, "chunk_2"), (5, "chunk_5"), (8, "chunk_8"), (11, "chunk_11")]
        # Worker 3 should get chunks 3, 6, 9, 12
        assert coordinator.chunk_assignments[3] == [(3, "chunk_3"), (6, "chunk_6"), (9, "chunk_9"), (12, "chunk_12")]

    def test_distribute_chunks_uneven_split(self) -> None:
        """Test distribution with uneven chunk count"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=3)

        chunks = [(i, f"chunk_{i}") for i in range(1, 11)]
        coordinator.distribute_chunks(chunks)

        # Workers should get 4, 3, 3 chunks respectively
        assert len(coordinator.chunk_assignments[1]) == 4
        assert len(coordinator.chunk_assignments[2]) == 3
        assert len(coordinator.chunk_assignments[3]) == 3

    def test_distribute_chunks_updates_worker_progress(self) -> None:
        """Test that distribution updates worker progress"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=9, num_workers=3)

        chunks = [(i, f"chunk_{i}") for i in range(1, 10)]
        coordinator.distribute_chunks(chunks)

        # Each worker should have total_chunks updated to 3
        for worker_id in range(1, 4):
            assert coordinator.worker_progress[worker_id].total_chunks == 3

    def test_get_worker_assignment(self) -> None:
        """Test retrieving worker assignments"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=6, num_workers=2)

        chunks = [(i, f"chunk_{i}") for i in range(1, 7)]
        coordinator.distribute_chunks(chunks)

        assignment = coordinator.get_worker_assignment(1)
        assert len(assignment) == 3
        assert assignment[0] == (1, "chunk_1")


class TestWorkerProgressTracking:
    """Tests for worker progress tracking"""

    def test_update_worker_progress(self) -> None:
        """Test updating worker progress"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        coordinator.update_worker_progress(worker_id=1, completed=5, failed=1, status="working")

        progress = coordinator.worker_progress[1]
        assert progress.completed_chunks == 5
        assert progress.failed_chunks == 1
        assert progress.status == "working"

    def test_update_worker_progress_updates_overall_stats(self) -> None:
        """Test that worker progress updates overall statistics"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=20, num_workers=2)

        coordinator.update_worker_progress(1, completed=8, failed=1, status="working")
        coordinator.update_worker_progress(2, completed=6, failed=2, status="working")

        assert coordinator.overall_completed == 14
        assert coordinator.overall_failed == 3

    def test_mark_worker_started(self) -> None:
        """Test marking worker as started"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        assert coordinator.start_time is None

        coordinator.mark_worker_started(1)

        assert coordinator.start_time is not None
        assert coordinator.worker_progress[1].status == "working"

    def test_mark_worker_completed(self) -> None:
        """Test marking worker as completed"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        coordinator.mark_worker_completed(1)

        assert coordinator.worker_progress[1].status == "completed"
        assert coordinator.end_time is None  # Not all workers done

    def test_mark_all_workers_completed_sets_end_time(self) -> None:
        """Test that end time is set when all workers complete"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)
        coordinator.start_time = time.time()

        coordinator.mark_worker_completed(1)
        coordinator.mark_worker_completed(2)

        assert coordinator.end_time is not None

    def test_mark_worker_failed(self) -> None:
        """Test marking worker as failed"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        coordinator.mark_worker_failed(1)

        assert coordinator.worker_progress[1].status == "failed"

    def test_mark_worker_captcha(self) -> None:
        """Test marking worker as waiting for CAPTCHA"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        coordinator.mark_worker_captcha(1)

        assert coordinator.worker_progress[1].status == "captcha"


class TestProgressBarGeneration:
    """Tests for progress bar generation"""

    def test_get_progress_bar_empty(self) -> None:
        """Test progress bar with no progress"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        bar = coordinator.get_progress_bar(0, 100, width=10)

        assert bar == "[░░░░░░░░░░]"

    def test_get_progress_bar_half(self) -> None:
        """Test progress bar at 50%"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        bar = coordinator.get_progress_bar(50, 100, width=10)

        assert bar == "[█████░░░░░]"

    def test_get_progress_bar_full(self) -> None:
        """Test progress bar at 100%"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        bar = coordinator.get_progress_bar(100, 100, width=10)

        assert bar == "[██████████]"

    def test_get_progress_bar_zero_total(self) -> None:
        """Test progress bar with zero total"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        bar = coordinator.get_progress_bar(0, 0, width=10)

        assert bar == "[░░░░░░░░░░]"


class TestStatusEmoji:
    """Tests for status emoji mapping"""

    def test_get_status_emoji_all_states(self) -> None:
        """Test emoji for all worker states"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        assert coordinator.get_status_emoji("initializing") == "[~]"
        assert coordinator.get_status_emoji("working") == "[+]"
        assert coordinator.get_status_emoji("captcha") == "[.]"
        assert coordinator.get_status_emoji("failed") == "[X]"
        assert coordinator.get_status_emoji("completed") == "[*]"

    def test_get_status_emoji_unknown(self) -> None:
        """Test emoji for unknown status"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=10, num_workers=2)

        assert coordinator.get_status_emoji("unknown_status") == "[?]"


class TestETACalculation:
    """Tests for ETA calculation"""

    def test_calculate_eta_complete(self) -> None:
        """Test ETA when processing is complete"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=5)
        coordinator.overall_completed = 100

        eta = coordinator._calculate_eta()  # type: ignore[reportPrivateUsage]

        assert eta == "Complete!"

    def test_calculate_eta_no_start(self) -> None:
        """Test ETA when processing hasn't started"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=5)

        eta = coordinator._calculate_eta()  # type: ignore[reportPrivateUsage]

        assert eta == "Calculating..."

    def test_calculate_eta_in_progress(self) -> None:
        """Test ETA calculation during processing"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=5)
        coordinator.start_time = time.time() - 60  # Started 60 seconds ago
        coordinator.overall_completed = 50  # 50% done

        eta = coordinator._calculate_eta()  # type: ignore[reportPrivateUsage]

        # Should estimate ~60 seconds remaining (1 min)
        assert "min" in eta or "sec" in eta


class TestSummaryStatistics:
    """Tests for summary statistics"""

    def test_get_summary_stats_complete(self) -> None:
        """Test getting summary statistics"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=3)
        coordinator.start_time = time.time() - 120
        coordinator.end_time = time.time()
        coordinator.overall_completed = 95
        coordinator.overall_failed = 5
        coordinator.mark_worker_completed(1)
        coordinator.mark_worker_completed(2)
        coordinator.mark_worker_failed(3)

        stats = coordinator.get_summary_stats()

        assert stats["total_chunks"] == 100
        assert stats["completed_chunks"] == 95
        assert stats["failed_chunks"] == 5
        assert stats["workers_succeeded"] == 2
        assert stats["workers_failed"] == 1
        assert stats["duration_seconds"] > 0

    def test_get_summary_stats_no_timing(self) -> None:
        """Test summary stats without timing data"""
        from parallel_coordinator import ParallelCoordinator

        coordinator = ParallelCoordinator(total_chunks=50, num_workers=2)

        stats = coordinator.get_summary_stats()

        assert stats["duration_seconds"] == 0


class TestPrintMethods:
    """Tests for display/print methods"""

    def test_print_final_summary(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test final summary printing"""
        from parallel_coordinator import ParallelCoordinator

        # Mock print_colored
        printed = []
        monkeypatch.setattr("parallel_coordinator.print_colored", lambda text, color: printed.append(text))

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=2)
        coordinator.start_time = time.time() - 60
        coordinator.end_time = time.time()
        coordinator.overall_completed = 100
        coordinator.overall_failed = 0
        coordinator.mark_worker_completed(1)
        coordinator.mark_worker_completed(2)

        coordinator.print_final_summary()

        # Verify summary was printed
        assert any("PARALLEL CONVERSION SUMMARY" in p for p in printed)
        assert any("Completed: 100/100" in p for p in printed)
        assert any("Duration:" in p for p in printed)
        assert any("Workers: 2 total" in p for p in printed)
        assert any("Succeeded: 2" in p for p in printed)

    def test_render_progress_dashboard(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test progress dashboard rendering"""
        from parallel_coordinator import ParallelCoordinator

        # Mock print_colored and print
        printed = []
        monkeypatch.setattr("parallel_coordinator.print_colored", lambda text, color: printed.append(text))
        monkeypatch.setattr("builtins.print", lambda *args: None)

        coordinator = ParallelCoordinator(total_chunks=100, num_workers=3)
        coordinator.start_time = time.time()
        coordinator.overall_completed = 30

        chunks = [(i, f"chunk_{i}") for i in range(1, 101)]
        coordinator.distribute_chunks(chunks)

        coordinator.update_worker_progress(1, completed=15, failed=0, status="working")
        coordinator.update_worker_progress(2, completed=10, failed=0, status="working")
        coordinator.update_worker_progress(3, completed=5, failed=0, status="captcha")

        coordinator.render_progress_dashboard()

        # Verify dashboard elements
        assert any("PARALLEL CONVERSION PROGRESS" in p for p in printed)
        assert any("Completed: 30/100" in p for p in printed)
        assert any("Worker #1" in p for p in printed)
        assert any("Worker #2" in p for p in printed)
        assert any("Worker #3" in p for p in printed)
