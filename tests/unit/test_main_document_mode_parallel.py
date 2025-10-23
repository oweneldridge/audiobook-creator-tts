"""
Unit tests for main_document_mode_parallel.py
Tests for parallel processing functions and configuration
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock, mock_open
from pathlib import Path


class TestConfigLoading:
    """Tests for configuration loading"""

    def test_load_config_from_file(self, tmp_path, monkeypatch):
        """Test loading configuration from file"""
        from main_document_mode_parallel import load_config
        import main_document_mode_parallel

        # Create config file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "parallel_settings.json"

        config_data = {
            "max_workers": 10,
            "enable_parallel_mode": True,
            "chunks_per_worker_target": 60
        }

        config_file.write_text(json.dumps(config_data))

        # Mock __file__ attribute to point to tmp_path
        monkeypatch.setattr(main_document_mode_parallel, "__file__", str(tmp_path / "main_document_mode_parallel.py"))

        config = load_config()

        assert config["max_workers"] == 10
        assert config["enable_parallel_mode"] is True
        assert config["chunks_per_worker_target"] == 60

    def test_load_config_default(self, tmp_path, monkeypatch):
        """Test loading default configuration when file doesn't exist"""
        from main_document_mode_parallel import load_config
        import main_document_mode_parallel

        # Mock __file__ to point to a location with no config directory
        monkeypatch.setattr(main_document_mode_parallel, "__file__", str(tmp_path / "main_document_mode_parallel.py"))

        config = load_config()

        assert config["max_workers"] == 15
        assert config["enable_parallel_mode"] is True
        assert config["safety_test_enabled"] is True
        assert config["chunks_per_worker_target"] == 55


class TestWorkerCalculation:
    """Tests for optimal worker calculation"""

    def test_calculate_optimal_workers_auto(self):
        """Test automatic worker calculation"""
        from main_document_mode_parallel import calculate_optimal_workers

        config = {
            "auto_calculate_workers": True,
            "chunks_per_worker_target": 55,
            "max_workers": 15
        }

        # 636 chunks / 55 = 11.56, rounded up = 12
        workers = calculate_optimal_workers(total_chunks=636, config=config)

        assert workers == 12

    def test_calculate_optimal_workers_capped(self):
        """Test worker calculation capped at max_workers"""
        from main_document_mode_parallel import calculate_optimal_workers

        config = {
            "auto_calculate_workers": True,
            "chunks_per_worker_target": 55,
            "max_workers": 10
        }

        # Would calculate 12 but capped at 10
        workers = calculate_optimal_workers(total_chunks=636, config=config)

        assert workers == 10

    def test_calculate_optimal_workers_manual(self):
        """Test manual worker count"""
        from main_document_mode_parallel import calculate_optimal_workers

        config = {
            "auto_calculate_workers": False,
            "default_workers": 5
        }

        workers = calculate_optimal_workers(total_chunks=636, config=config)

        assert workers == 5

    def test_calculate_optimal_workers_small_book(self):
        """Test calculation for small number of chunks"""
        from main_document_mode_parallel import calculate_optimal_workers

        config = {
            "auto_calculate_workers": True,
            "chunks_per_worker_target": 55,
            "max_workers": 15
        }

        # 50 chunks / 55 = 0.9, rounded up = 1
        workers = calculate_optimal_workers(total_chunks=50, config=config)

        assert workers == 1


class TestCaptchaStrategy:
    """Tests for CAPTCHA strategy selection"""

    def test_prompt_captcha_strategy_simultaneous(self, monkeypatch):
        """Test selecting simultaneous strategy"""
        from main_document_mode_parallel import prompt_captcha_strategy

        monkeypatch.setattr("main_document_mode_parallel.input_colored", lambda prompt, color: "1")

        printed = []
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: printed.append(text))

        strategy = prompt_captcha_strategy()

        assert strategy == "simultaneous"

    def test_prompt_captcha_strategy_staggered(self, monkeypatch):
        """Test selecting staggered strategy"""
        from main_document_mode_parallel import prompt_captcha_strategy

        monkeypatch.setattr("main_document_mode_parallel.input_colored", lambda prompt, color: "2")
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        strategy = prompt_captcha_strategy()

        assert strategy == "staggered"

    def test_prompt_captcha_strategy_sequential(self, monkeypatch):
        """Test selecting sequential strategy"""
        from main_document_mode_parallel import prompt_captcha_strategy

        monkeypatch.setattr("main_document_mode_parallel.input_colored", lambda prompt, color: "3")
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        strategy = prompt_captcha_strategy()

        assert strategy == "sequential"

    def test_prompt_captcha_strategy_invalid_then_valid(self, monkeypatch):
        """Test invalid input then valid"""
        from main_document_mode_parallel import prompt_captcha_strategy

        inputs = ["5", "invalid", "1"]
        input_iter = iter(inputs)
        monkeypatch.setattr("main_document_mode_parallel.input_colored", lambda prompt, color: next(input_iter))

        printed = []
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: printed.append(text))

        strategy = prompt_captcha_strategy()

        assert strategy == "simultaneous"
        assert any("Please enter 1, 2, or 3" in p for p in printed)


class TestPrintTimestamped:
    """Tests for timestamped printing"""

    def test_print_timestamped(self, monkeypatch):
        """Test timestamped message printing"""
        from main_document_mode_parallel import print_timestamped

        printed = []
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: printed.append(text))

        print_timestamped("Test message", "cyan")

        assert len(printed) == 1
        assert "Test message" in printed[0]
        assert "[" in printed[0]  # Has timestamp
        assert "]" in printed[0]


@pytest.mark.asyncio
class TestSafetyTest:
    """Tests for safety test functionality"""

    async def test_run_safety_test_not_enough_chunks(self, monkeypatch):
        """Test safety test with insufficient chunks"""
        from main_document_mode_parallel import run_safety_test
        from main_document_mode import Chapter

        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        # Create chapter with only 5 chunks
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="test", chunks=["chunk1", "chunk2", "chunk3", "chunk4", "chunk5"])

        success, message = await run_safety_test(
            chapters=[chapter],
            voice_id="voice-1",
            output_dir="/tmp"
        )

        assert success is False
        assert "Not enough chunks" in message

    async def test_run_safety_test_success(self, monkeypatch):
        """Test successful safety test"""
        from main_document_mode_parallel import run_safety_test
        from main_document_mode import Chapter

        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        # Create chapter with enough chunks
        chunks = [f"chunk_{i}" for i in range(100)]
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="test"*100, chunks=chunks)

        # Mock WorkerBrowser
        mock_worker_class = MagicMock()
        mock_worker_instance = AsyncMock()
        mock_worker_instance.initialize = AsyncMock()
        mock_worker_instance.request_audio = AsyncMock(return_value=b"audio_data")
        mock_worker_instance.cleanup = AsyncMock()
        mock_worker_instance.requests_since_captcha = 1
        mock_worker_instance.completed_chunks = []
        mock_worker_instance.failed_chunks = []
        mock_worker_class.return_value = mock_worker_instance

        monkeypatch.setattr("main_document_mode_parallel.WorkerBrowser", mock_worker_class)

        success, message = await run_safety_test(
            chapters=[chapter],
            voice_id="voice-1",
            output_dir="/tmp"
        )

        assert success is True
        assert "Safety test passed" in message


@pytest.mark.asyncio
class TestWorkerProcessWrapper:
    """Tests for worker process wrapper"""

    async def test_worker_process_wrapper_success(self, monkeypatch, tmp_path):
        """Test successful worker execution"""
        from main_document_mode_parallel import worker_process_wrapper
        from main_document_mode import Chapter

        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        # Mock WorkerBrowser
        mock_worker_class = MagicMock()
        mock_worker_instance = AsyncMock()
        mock_worker_instance.initialize = AsyncMock()
        mock_worker_instance.assign_chunks = MagicMock()
        mock_worker_instance.process_assigned_chunks = AsyncMock(return_value={
            "worker_id": 1,
            "completed": [1, 2],
            "failed": [],
            "success_count": 2,
            "failure_count": 0
        })
        mock_worker_instance.cleanup = AsyncMock()
        mock_worker_class.return_value = mock_worker_instance

        monkeypatch.setattr("main_document_mode_parallel.WorkerBrowser", mock_worker_class)

        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="test text", chunks=["chunk1", "chunk2"])
        chapter_chunks = [(1, "chunk1", chapter), (2, "chunk2", chapter)]

        result = await worker_process_wrapper(
            worker_id=1,
            voice_id="voice-1",
            output_dir=str(tmp_path),
            chapter_chunks=chapter_chunks,
            start_delay=0
        )

        assert result["worker_id"] == 1
        assert result["status"] == "success"
        assert len(result["results"]) == 1

    async def test_worker_process_wrapper_with_delay(self, monkeypatch, tmp_path):
        """Test worker with start delay"""
        from main_document_mode_parallel import worker_process_wrapper
        from main_document_mode import Chapter

        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        mock_worker_class = MagicMock()
        mock_worker_instance = AsyncMock()
        mock_worker_instance.initialize = AsyncMock()
        mock_worker_instance.assign_chunks = MagicMock()
        mock_worker_instance.process_assigned_chunks = AsyncMock(return_value={
            "worker_id": 2,
            "completed": [],
            "failed": [],
            "success_count": 0,
            "failure_count": 0
        })
        mock_worker_instance.cleanup = AsyncMock()
        mock_worker_class.return_value = mock_worker_instance

        monkeypatch.setattr("main_document_mode_parallel.WorkerBrowser", mock_worker_class)

        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="test", chunks=["chunk1"])
        chapter_chunks = [(1, "chunk1", chapter)]

        import time
        start_time = time.time()

        result = await worker_process_wrapper(
            worker_id=2,
            voice_id="voice-1",
            output_dir=str(tmp_path),
            chapter_chunks=chapter_chunks,
            start_delay=1  # 1 second delay
        )

        elapsed = time.time() - start_time

        assert result["status"] == "success"
        assert elapsed >= 1.0  # Verify delay was applied

    async def test_worker_process_wrapper_error(self, monkeypatch, tmp_path):
        """Test worker error handling"""
        from main_document_mode_parallel import worker_process_wrapper
        from main_document_mode import Chapter

        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: None)

        # Mock WorkerBrowser to raise exception
        mock_worker_class = MagicMock()
        mock_worker_instance = AsyncMock()
        mock_worker_instance.initialize = AsyncMock(side_effect=Exception("Test error"))
        mock_worker_instance.cleanup = AsyncMock()
        mock_worker_class.return_value = mock_worker_instance

        monkeypatch.setattr("main_document_mode_parallel.WorkerBrowser", mock_worker_class)

        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="test", chunks=["chunk1"])
        chapter_chunks = [(1, "chunk1", chapter)]

        result = await worker_process_wrapper(
            worker_id=3,
            voice_id="voice-1",
            output_dir=str(tmp_path),
            chapter_chunks=chapter_chunks,
            start_delay=0
        )

        assert result["worker_id"] == 3
        assert result["status"] == "failed"
        assert "error" in result
        assert "Test error" in result["error"]


@pytest.mark.asyncio
class TestMain:
    """Tests for main entry point"""

    async def test_main_parallel_mode_disabled(self, monkeypatch):
        """Test main when parallel mode is disabled"""
        from main_document_mode_parallel import main

        printed = []
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: printed.append(text))

        # Mock load_config to return disabled parallel mode
        monkeypatch.setattr("main_document_mode_parallel.load_config", lambda: {
            "enable_parallel_mode": False
        })

        await main()

        assert any("Parallel mode is disabled" in p for p in printed)

    async def test_main_parallel_mode_enabled(self, monkeypatch):
        """Test main with parallel mode enabled"""
        from main_document_mode_parallel import main

        printed = []
        monkeypatch.setattr("main_document_mode_parallel.print_colored", lambda text, color: printed.append(text))

        monkeypatch.setattr("main_document_mode_parallel.load_config", lambda: {
            "enable_parallel_mode": True
        })

        await main()

        assert any("Parallel mode infrastructure is ready" in p for p in printed)
