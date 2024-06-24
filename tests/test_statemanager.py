import pytest
import json
from datetime import datetime, timedelta
from unittest import mock
from tempfile import NamedTemporaryFile
from gv_auto.environment import TIMEZONE, TimeManager
from gv_auto.hero import StateManager, sync_bingo_time
import os


@pytest.fixture
def state_manager():
    with NamedTemporaryFile(delete=False) as tmp_file:
        state_manager = StateManager(file_path=tmp_file.name)
        yield state_manager
    # Cleanup after test
    os.remove(tmp_file.name)


def test_convert_state_times_to_str(state_manager):
    state = state_manager.default_state.copy()
    state_str = state_manager._convert_state_times_to_str(state)
    for key in state_manager.time_attributes:
        assert isinstance(state_str[key], str)


def test_convert_state_times_to_datetime(state_manager):
    state = state_manager.default_state.copy()
    state_str = state_manager._convert_state_times_to_str(state)
    state_dt = state_manager._convert_state_times_to_datetime(state_str)
    for key in state_manager.time_attributes:
        assert isinstance(state_dt[key], datetime)


def test_load_state_file_not_found(state_manager):
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        state = state_manager.load_state()
    assert state == state_manager.default_state


def test_load_state_invalid_json(state_manager):
    with mock.patch("builtins.open", mock.mock_open(read_data="invalid json")):
        state = state_manager.load_state()
    assert state == state_manager.default_state


def test_load_state_valid_json(state_manager):
    state_data = state_manager.default_state.copy()
    state_data = state_manager._convert_state_times_to_str(state_data)
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(state_data))):
        state = state_manager.load_state()
    for key in state_manager.time_attributes:
        assert isinstance(state[key], datetime)


def test_save_state(state_manager):
    state = state_manager.default_state.copy()
    with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
        state_manager.save_state(state)
        mocked_file.assert_called_once_with(state_manager.file_path, "w")
        handle = mocked_file()
        written_data = handle.write.call_args[0][0]
        written_state = json.loads(written_data)
        for key in state_manager.time_attributes:
            assert isinstance(written_state[key], str)


def test_sync_bingo_time_decorator(state_manager):
    def dummy_method(self):
        return "dummy result"

    decorated_method = sync_bingo_time(dummy_method)
    hero_tracker_mock = mock.Mock()
    hero_tracker_mock.state_manager = state_manager
    hero_tracker_mock.state = state_manager.default_state.copy()

    previous_deadline = TimeManager.get_game_refresh_time(offset_min=2, previous=True)
    hero_tracker_mock.state["last_sync_time"] = previous_deadline - timedelta(days=1)

    with mock.patch.object(
        TimeManager, "current_time", return_value=datetime.now(TIMEZONE)
    ):
        result = decorated_method(hero_tracker_mock)

    assert result == "dummy result"
    assert hero_tracker_mock.state["bingo_counter"] == 3
    assert hero_tracker_mock.state["last_sync_time"] == TimeManager.current_time()
    hero_tracker_mock.state_manager.save_state.assert_called_once()


if __name__ == "__main__":
    pytest.main()
