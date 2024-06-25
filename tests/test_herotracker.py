import pytest
from unittest import mock
from datetime import datetime, timedelta
import tempfile
import os
import pytz
from gv_auto.environment import TIMEZONE
from gv_auto.hero import HeroTracker, StateManager, TimeManager, BINGO_TIMEOUT_MIN
from gv_auto.response import Responses


@pytest.fixture(scope="function")
def temp_state_file():
    temp_dir = tempfile.TemporaryDirectory()
    yield os.path.join(temp_dir.name, "hero_tracker_state.json")
    temp_dir.cleanup()


@pytest.fixture(scope="function")
def state_manager(temp_state_file):
    return StateManager(file_path=temp_state_file)


@pytest.fixture(scope="function")
def hero_tracker(state_manager):
    env_mock = mock.Mock()
    env_mock.quest = [0]  # Initialize with some default value
    return HeroTracker(env=env_mock, state_manager=state_manager)


def test_return_scenarios(hero_tracker):
    # Check initial return
    assert hero_tracker.can_return

    # Register two returns and check
    hero_tracker.register_return()
    hero_tracker.update_return_cnt(hero_tracker.env.quest[0])
    hero_tracker.register_return()
    hero_tracker.update_return_cnt(hero_tracker.env.quest[0])
    assert not hero_tracker.can_return

    # Mock quest completion and check reset
    hero_tracker.env.quest = [1]
    hero_tracker.update_return_cnt(hero_tracker.env.quest[0])
    assert hero_tracker.can_return


def test_bingo_scenarios(hero_tracker):
    fixed_time = datetime(2023, 6, 25, 23, 0, tzinfo=pytz.utc)
    timeout_duration = timedelta(minutes=BINGO_TIMEOUT_MIN + 1)
    time_increment = timedelta(minutes=30)

    with mock.patch.object(TimeManager, "current_time") as mock_current_time:
        mock_current_time.return_value = fixed_time

        for _ in range(3):
            assert hero_tracker.is_bingo_available
            hero_tracker.register_bingo_attempt()
            hero_tracker.register_bingo_play()

            # right after won't be available because of timeout
            assert not hero_tracker.is_bingo_available

            # Move time forward by the timeout duration to make bingo available again
            fixed_time += timeout_duration
            mock_current_time.return_value = fixed_time

        assert not hero_tracker.is_bingo_available


def test_update_bingo_counter(hero_tracker):
    # like it's some old game so bingo isn't reset
    with mock.patch.object(TimeManager, "get_game_refresh_time") as refresh_time:
        refresh_time.return_value = datetime(2000, 1, 1, tzinfo=TIMEZONE)
        hero_tracker.update_bingo_counter(1)
        assert hero_tracker.is_bingo_available

        hero_tracker.register_bingo_play()
        assert not hero_tracker.is_bingo_available


def test_melting_scenarios(hero_tracker):
    # Mock TimeManager to control time
    initial_time = TimeManager.current_time()
    with mock.patch.object(TimeManager, "current_time", return_value=initial_time):
        hero_tracker.register_melting()

    # Immediately check melting availability
    with mock.patch.object(TimeManager, "seconds_from_time", return_value=10):
        assert not hero_tracker.is_melting_available

    # Check melting availability after 20 seconds
    with mock.patch.object(TimeManager, "seconds_from_time", return_value=21):
        assert hero_tracker.is_melting_available


def test_godvoice_scenarios(hero_tracker):
    # Mock TimeManager to control future time
    initial_time = TimeManager.current_time()
    with mock.patch.object(TimeManager, "current_time", return_value=initial_time):
        hero_tracker.register_godvoice(Responses.IGNORED)
        godvoice_unavailable_time = initial_time + timedelta(seconds=10)
        with mock.patch.object(
            TimeManager, "current_time", return_value=godvoice_unavailable_time
        ):
            assert not hero_tracker.is_godvoice_available
        godvoice_available_time = initial_time + timedelta(seconds=21)
        with mock.patch.object(
            TimeManager, "current_time", return_value=godvoice_available_time
        ):
            assert hero_tracker.is_godvoice_available

    initial_time = TimeManager.current_time()
    with mock.patch.object(TimeManager, "current_time", return_value=initial_time):
        hero_tracker.register_godvoice(Responses.RESPONDED)
        godvoice_unavailable_time = initial_time + timedelta(seconds=21)
        with mock.patch.object(
            TimeManager, "current_time", return_value=godvoice_unavailable_time
        ):
            assert not hero_tracker.is_godvoice_available
        godvoice_available_time = initial_time + timedelta(seconds=61)
        with mock.patch.object(
            TimeManager, "current_time", return_value=godvoice_available_time
        ):
            assert hero_tracker.is_godvoice_available
