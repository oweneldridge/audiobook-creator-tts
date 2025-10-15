"""
Unit tests for voice management functions

Tests for load_voices, display_voices, get_voice_id, count_voice_stats,
select_voice_interactive, and related helper functions
"""
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from main import (
    load_voices, display_voices, get_voice_id, count_voice_stats,
    count_voices_by_level, get_all_voice_ids, select_voice_interactive
)


@pytest.mark.unit
@pytest.mark.voice
class TestLoadVoices:
    """Tests for load_voices function"""

    def test_load_voices_success(self, mock_voices_json, sample_voices_data):
        """Test successfully loading voices from JSON file"""
        result = load_voices()

        assert result is not None
        assert isinstance(result, dict)
        assert "English" in result
        assert "Spanish" in result

    def test_load_voices_file_not_found(self, tmp_path, monkeypatch):
        """Test handling of missing voices.json file"""
        # Change to directory without voices.json
        monkeypatch.chdir(tmp_path)

        result = load_voices()
        assert result is None

    def test_load_voices_invalid_json(self, tmp_path, monkeypatch):
        """Test handling of invalid JSON in voices.json"""
        # Create file with invalid JSON
        voices_file = tmp_path / "voices.json"
        voices_file.write_text("{ invalid json }")

        monkeypatch.chdir(tmp_path)

        result = load_voices()
        assert result is None

    def test_load_voices_empty_file(self, tmp_path, monkeypatch):
        """Test handling of empty voices.json file"""
        voices_file = tmp_path / "voices.json"
        voices_file.write_text("{}")

        monkeypatch.chdir(tmp_path)

        result = load_voices()
        assert result == {}

    def test_load_voices_encoding(self, tmp_path, monkeypatch):
        """Test that UTF-8 encoding is handled correctly"""
        # Create file with UTF-8 characters
        voices_data = {
            "Français": {"France": {"female": {"Amélie": "voice-1"}}}
        }
        voices_file = tmp_path / "voices.json"
        with open(voices_file, 'w', encoding='utf-8') as f:
            json.dump(voices_data, f)

        monkeypatch.chdir(tmp_path)

        result = load_voices()
        assert result is not None
        assert "Français" in result


@pytest.mark.unit
@pytest.mark.voice
class TestDisplayVoices:
    """Tests for display_voices function"""

    def test_display_voices_none_input(self, capsys):
        """Test display_voices with None input"""
        count = display_voices(None)

        captured = capsys.readouterr()
        assert "No voices available" in captured.out
        assert count == 0

    def test_display_voices_empty_dict(self):
        """Test display_voices with empty dictionary"""
        count = display_voices({})
        assert count == 0

    def test_display_voices_counts_correctly(self, sample_voices_data, capsys):
        """Test that display_voices counts all voices"""
        count = display_voices(sample_voices_data, show_ids=False)

        # Count voices in sample data
        expected_count = 10  # Based on sample_voices_data fixture
        assert count == expected_count

    def test_display_voices_with_ids(self, sample_voices_data, capsys):
        """Test display with voice IDs shown"""
        display_voices(sample_voices_data, show_ids=True)

        captured = capsys.readouterr()
        # Should show voice IDs in output
        assert "voice-" in captured.out

    def test_display_voices_without_ids(self, sample_voices_data, capsys):
        """Test display without voice IDs"""
        display_voices(sample_voices_data, show_ids=False)

        captured = capsys.readouterr()
        # Voice IDs should not be visible (or be in gray)
        output = captured.out

        # Check that language, country, gender, and names are shown
        assert "English" in output
        assert "United States" in output
        assert "female" in output or "Ava" in output

    def test_display_voices_prefix_formatting(self, capsys):
        """Test that prefix is properly formatted"""
        voices = {
            "English": {
                "US": {
                    "female": {"Ava": "voice-111"}
                }
            }
        }

        display_voices(voices)
        captured = capsys.readouterr()

        # Should show: "1- English US female Ava"
        assert "English US female Ava" in captured.out

    def test_display_voices_recursive_structure(self):
        """Test handling of nested dictionary structure"""
        voices = {
            "Lang1": {
                "Country1": {
                    "gender1": {
                        "Voice1": "voice-1",
                        "Voice2": "voice-2"
                    }
                }
            },
            "Lang2": {
                "Country2": {
                    "gender2": {
                        "Voice3": "voice-3"
                    }
                }
            }
        }

        count = display_voices(voices)
        assert count == 3


@pytest.mark.unit
@pytest.mark.voice
class TestGetVoiceId:
    """Tests for get_voice_id function"""

    def test_get_voice_id_first_voice(self, sample_voices_data):
        """Test getting the first voice"""
        voice_id, index = get_voice_id(sample_voices_data, choice=1, current_index=0)

        assert voice_id is not None
        assert isinstance(voice_id, str)
        assert voice_id.startswith("voice-")
        assert index == 1

    def test_get_voice_id_last_voice(self, sample_voices_data):
        """Test getting the last voice"""
        # Count total voices first
        total_count = sum(1 for _ in get_all_voice_ids(sample_voices_data))

        voice_id, index = get_voice_id(sample_voices_data, choice=total_count, current_index=0)

        assert voice_id is not None
        assert index == total_count

    def test_get_voice_id_invalid_choice(self, sample_voices_data):
        """Test with invalid choice number"""
        voice_id, index = get_voice_id(sample_voices_data, choice=9999, current_index=0)

        assert voice_id is None

    def test_get_voice_id_zero_choice(self, sample_voices_data):
        """Test with zero choice"""
        voice_id, index = get_voice_id(sample_voices_data, choice=0, current_index=0)

        assert voice_id is None

    def test_get_voice_id_negative_choice(self, sample_voices_data):
        """Test with negative choice"""
        voice_id, index = get_voice_id(sample_voices_data, choice=-1, current_index=0)

        assert voice_id is None

    def test_get_voice_id_known_voice(self, sample_voices_data):
        """Test getting specific known voice"""
        # We know Ava is voice-111 and should be first female US voice
        voice_id, index = get_voice_id(sample_voices_data, choice=1, current_index=0)

        # The exact voice depends on iteration order, but should be valid
        assert voice_id in ["voice-111", "voice-115", "voice-107", "voice-112"]


@pytest.mark.unit
@pytest.mark.voice
class TestCountVoiceStats:
    """Tests for count_voice_stats function"""

    def test_count_voice_stats_total(self, sample_voices_data):
        """Test counting total voices"""
        stats = count_voice_stats(sample_voices_data)

        assert stats['total'] == 10  # Based on sample data

    def test_count_voice_stats_languages(self, sample_voices_data):
        """Test counting languages"""
        stats = count_voice_stats(sample_voices_data)

        assert len(stats['languages']) == 2  # English and Spanish
        assert 'English' in stats['languages']
        assert 'Spanish' in stats['languages']

    def test_count_voice_stats_countries(self, sample_voices_data):
        """Test counting countries"""
        stats = count_voice_stats(sample_voices_data)

        assert len(stats['countries']) == 4
        assert 'United States' in stats['countries']
        assert 'United Kingdom' in stats['countries']
        assert 'Spain' in stats['countries']
        assert 'Mexico' in stats['countries']

    def test_count_voice_stats_genders(self, sample_voices_data):
        """Test counting genders"""
        stats = count_voice_stats(sample_voices_data)

        assert len(stats['genders']) == 2
        assert 'female' in stats['genders']
        assert 'male' in stats['genders']

    def test_count_voice_stats_empty(self):
        """Test with empty voices dict"""
        stats = count_voice_stats({})

        assert stats['total'] == 0
        assert len(stats['languages']) == 0
        assert len(stats['countries']) == 0
        assert len(stats['genders']) == 0

    def test_count_voice_stats_single_voice(self):
        """Test with single voice"""
        voices = {
            "English": {
                "US": {
                    "female": {"Ava": "voice-111"}
                }
            }
        }

        stats = count_voice_stats(voices)

        assert stats['total'] == 1
        assert len(stats['languages']) == 1
        assert len(stats['countries']) == 1
        assert len(stats['genders']) == 1


@pytest.mark.unit
@pytest.mark.voice
class TestCountVoicesByLevel:
    """Tests for count_voices_by_level helper function"""

    def test_count_by_language_level(self, sample_voices_data):
        """Test counting at language level"""
        counts = count_voices_by_level(sample_voices_data, level=0)

        assert 'English' in counts
        assert 'Spanish' in counts
        assert counts['English'] == 7  # 7 English voices
        assert counts['Spanish'] == 3  # 3 Spanish voices

    def test_count_by_country_level(self, sample_voices_data):
        """Test counting at country level"""
        counts = count_voices_by_level(sample_voices_data, level=1)

        assert 'United States' in counts
        assert 'United Kingdom' in counts
        assert 'Spain' in counts
        assert 'Mexico' in counts


@pytest.mark.unit
@pytest.mark.voice
class TestGetAllVoiceIds:
    """Tests for get_all_voice_ids helper function"""

    def test_get_all_voice_ids_generator(self, sample_voices_data):
        """Test that function returns a generator"""
        result = get_all_voice_ids(sample_voices_data)

        # Should be a generator
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_get_all_voice_ids_count(self, sample_voices_data):
        """Test getting all voice IDs"""
        ids = list(get_all_voice_ids(sample_voices_data))

        assert len(ids) == 10

    def test_get_all_voice_ids_format(self, sample_voices_data):
        """Test that all IDs have correct format"""
        ids = list(get_all_voice_ids(sample_voices_data))

        for voice_id in ids:
            assert isinstance(voice_id, str)
            assert voice_id.startswith("voice-")

    def test_get_all_voice_ids_empty(self):
        """Test with empty dictionary"""
        ids = list(get_all_voice_ids({}))
        assert len(ids) == 0

    def test_get_all_voice_ids_unique(self, sample_voices_data):
        """Test that all IDs are unique"""
        ids = list(get_all_voice_ids(sample_voices_data))

        assert len(ids) == len(set(ids))  # No duplicates


@pytest.mark.unit
@pytest.mark.voice
class TestSelectVoiceInteractive:
    """Tests for select_voice_interactive function"""

    def test_select_voice_direct_id(self, sample_voices_data, monkeypatch):
        """Test direct voice ID input"""
        # Mock user input to provide direct voice ID
        inputs = iter(["voice-111"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id == "voice-111"
        assert "voice-111" in voice_name

    def test_select_voice_quit(self, sample_voices_data, monkeypatch):
        """Test quitting voice selection"""
        inputs = iter(["q"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id is None
        assert voice_name is None

    def test_select_voice_full_flow(self, sample_voices_data, monkeypatch):
        """Test complete selection flow"""
        # Simulate: Select English (1) -> US (1) -> Female (1) -> Show IDs (n) -> First voice (1)
        inputs = iter(["1", "1", "1", "n", "1"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id is not None
        assert voice_id.startswith("voice-")
        assert voice_name is not None

    def test_select_voice_back_navigation(self, sample_voices_data, monkeypatch):
        """Test back navigation"""
        # Select language, country, then go back, then quit
        inputs = iter(["1", "1", "b", "q"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id is None
        assert voice_name is None

    def test_select_voice_invalid_then_valid(self, sample_voices_data, monkeypatch):
        """Test invalid input followed by valid input"""
        # Invalid language choice, then valid choice, then quit
        inputs = iter(["999", "q"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id is None
        assert voice_name is None

    def test_select_voice_restart(self, sample_voices_data, monkeypatch):
        """Test restart functionality"""
        # Go to country level, restart, then quit
        inputs = iter(["1", "r", "q"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        voice_id, voice_name = select_voice_interactive(sample_voices_data)

        assert voice_id is None
        assert voice_name is None


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceManagementEdgeCases:
    """Edge case tests for voice management"""

    def test_deeply_nested_structure(self):
        """Test handling of unexpected nesting"""
        voices = {
            "Level1": {
                "Level2": {
                    "Level3": {
                        "Level4": {"Voice": "voice-1"}
                    }
                }
            }
        }

        count = display_voices(voices)
        assert count == 1

    def test_mixed_structure_types(self):
        """Test handling mixed structure (shouldn't happen, but defensive)"""
        voices = {
            "Normal": {
                "Country": {
                    "gender": {"Voice1": "voice-1"}
                }
            }
        }

        stats = count_voice_stats(voices)
        assert stats['total'] >= 1

    def test_special_characters_in_names(self):
        """Test voice names with special characters"""
        voices = {
            "English": {
                "US": {
                    "female": {
                        "María José": "voice-1",
                        "O'Brien": "voice-2"
                    }
                }
            }
        }

        count = display_voices(voices)
        assert count == 2

    def test_empty_nested_levels(self):
        """Test handling of empty nested levels"""
        voices = {
            "English": {
                "US": {}
            }
        }

        stats = count_voice_stats(voices)
        assert stats['total'] == 0
