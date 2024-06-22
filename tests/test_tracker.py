import pytest
from datetime import datetime
from unittest.mock import patch
import json
import os
import tempfile
from gv_auto.hero import HeroTracker


# Helper function to mock datetime
class MockDateTime(datetime):
    @classmethod
    def now(cls):
        return cls(2023, 6, 21, 0, 3)


@pytest.fixture
def temp_state_file():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_file_path = tmp.name
    yield temp_file_path
    try:
        os.remove(temp_file_path)
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def cleanup(temp_state_file):
    yield
    try:
        os.remove(temp_state_file)
    except FileNotFoundError:
        pass


# Mock the path to the state file in the HeroTracker class
@pytest.fixture()
def mock_load_save_state(temp_state_file):
    original_load_state = HeroTracker._load_state
    original_save_state = HeroTracker._save_state

    def _load_state(self):
        try:
            with open(temp_state_file, "r") as f:
                state = json.load(f)
                self._return_counter = state["return_counter"]
                self.bingo_counter = state["bingo_counter"]
                self.last_bingo_time = datetime.fromisoformat(state["last_bingo_time"])
                self.last_melting_time = datetime.fromisoformat(
                    state["last_melting_time"]
                )
                self.last_sync_time = datetime.fromisoformat(state["last_sync_time"])
        except (FileNotFoundError, ValueError):
            pass

    def _save_state(self):
        state = {
            "return_counter": self._return_counter,
            "bingo_counter": self.bingo_counter,
            "last_bingo_time": self.last_bingo_time.isoformat(),
            "last_melting_time": self.last_melting_time.isoformat(),
            "last_sync_time": self.last_sync_time.isoformat(),
        }
        with open(temp_state_file, "w") as f:
            json.dump(state, f)

    HeroTracker._load_state = _load_state
    HeroTracker._save_state = _save_state

    yield

    HeroTracker._load_state = original_load_state
    HeroTracker._save_state = original_save_state


def test_register_return(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    assert tracker.can_return
    tracker.register_return()
    assert tracker.return_counter == 1
    tracker.register_return()
    assert not tracker.can_return
    tracker.update_return_cnt()
    assert tracker.return_counter == 0


@patch("gv_auto.hero.datetime", MockDateTime)
def test_sync_bingo_time(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    tracker.register_bingo_attempt()
    tracker.bingo_counter = 3
    tracker.register_bingo_play()
    tracker.bingo_counter = 2
    with patch("gv_auto.hero.datetime", MockDateTime(2023, 7, 20, 0, 0)):
        tracker.is_bingo_available
        assert tracker.last_sync_time == MockDateTime(2023, 7, 20, 0, 0)
        assert tracker.bingo_counter == 3


@patch("gv_auto.hero.datetime", MockDateTime)
def test_is_bingo_available(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    tracker.last_bingo_time = MockDateTime(2023, 6, 20, 0, 0)
    tracker.bingo_counter = 3
    assert tracker.is_bingo_available


@patch("gv_auto.hero.datetime", MockDateTime)
def test_register_bingo_play(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    tracker.bingo_counter = 3
    tracker.register_bingo_play()
    assert tracker.bingo_counter == 2


@patch("gv_auto.hero.datetime", MockDateTime)
def test_is_melting_available(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    tracker.last_melting_time = MockDateTime(2023, 6, 20, 0, 0)
    assert tracker.is_melting_available
    tracker.register_melting()
    assert not tracker.is_melting_available


@patch("gv_auto.hero.datetime", MockDateTime)
def test_bingo_last_call(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    assert tracker.bingo_last_call


def test_save_and_load_state(temp_state_file, mock_load_save_state):
    tracker = HeroTracker()
    tracker.return_counter = 1
    tracker.bingo_counter = 2
    tracker.last_bingo_time = datetime(2023, 6, 20, 0, 0)
    tracker.last_melting_time = datetime(2023, 6, 20, 0, 0)
    tracker._save_state()

    new_tracker = HeroTracker()
    assert new_tracker.return_counter == 1
    assert new_tracker.bingo_counter == 2
    assert new_tracker.last_bingo_time == datetime(2023, 6, 20, 0, 0)
    assert new_tracker.last_melting_time == datetime(2023, 6, 20, 0, 0)
