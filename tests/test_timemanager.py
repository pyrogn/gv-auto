import pytest
from datetime import datetime, timedelta
from unittest import mock
import pytz
from gv_auto.environment import TIMEZONE
from gv_auto.hero import TimeManager


@pytest.fixture
def mock_time():
    return datetime(2024, 6, 24, 23, 0, 0, tzinfo=pytz.timezone("UTC"))


current_time_var = "gv_auto.hero.TimeManager.current_time"


def test_current_time(mock_time):
    with mock.patch(current_time_var, return_value=mock_time):
        current_time = TimeManager.current_time()
        assert current_time == mock_time


def test_get_game_refresh_time(mock_time):
    with mock.patch(current_time_var, return_value=mock_time):
        offset_min = 5
        refresh_time = TimeManager.get_game_refresh_time(offset_min=offset_min)
        expected_time = mock_time.replace(
            hour=0, minute=5, second=0, microsecond=0
        ) + timedelta(minutes=offset_min)
        if mock_time > expected_time:
            expected_time += timedelta(days=1)
        assert refresh_time == expected_time


def test_get_game_refresh_time_previous(mock_time):
    with mock.patch(current_time_var, return_value=mock_time):
        offset_min = 5
        refresh_time = TimeManager.get_game_refresh_time(
            offset_min=offset_min, previous=True
        )
        expected_time = (
            mock_time.replace(hour=0, minute=5, second=0, microsecond=0)
            + timedelta(minutes=offset_min)
            - timedelta(days=1)
        )
        if mock_time > expected_time + timedelta(days=1):
            expected_time += timedelta(days=1)
        assert refresh_time == expected_time


def test_bingo_last_call(mock_time):
    with mock.patch(current_time_var, return_value=mock_time):
        refresh_time = TimeManager.get_game_refresh_time()
        bingo_last_call = TimeManager.bingo_last_call()
        seconds_left_to_deadline = (refresh_time - mock_time).total_seconds()
        expected = seconds_left_to_deadline / 60 < 120
        assert bingo_last_call == expected


def test_get_future_time(mock_time):
    with mock.patch(current_time_var, return_value=mock_time):
        # 1 hour into the future
        seconds_offset = 60 * 60
        future_time = TimeManager.get_future_time(offset_sec=seconds_offset)
        expected_time = mock_time + timedelta(seconds=seconds_offset)
        assert future_time == expected_time


def test_seconds_from_time(mock_time):
    seconds_offset = 3600
    past_time = mock_time - timedelta(seconds=seconds_offset)
    with mock.patch(current_time_var, return_value=mock_time):
        seconds = TimeManager.seconds_from_time(past_time)
        assert seconds == seconds_offset


def test_next_deadline_moved_by_one_day():
    current_time = datetime(2024, 6, 24, 23, 0, 0, tzinfo=TIMEZONE)
    with mock.patch(current_time_var, return_value=current_time):
        refresh_time = TimeManager.get_game_refresh_time()
        assert refresh_time.day == (current_time + timedelta(days=1)).day
        refresh_time_previous = TimeManager.get_game_refresh_time(previous=True)
        assert refresh_time_previous.day == current_time.day


def test_next_deadline_early_night():
    current_time = datetime(2024, 6, 24, 0, 3, 0, tzinfo=TIMEZONE)
    with mock.patch(current_time_var, return_value=current_time):
        refresh_time = TimeManager.get_game_refresh_time()
        assert refresh_time.day == (current_time).day
        refresh_time_previous = TimeManager.get_game_refresh_time(previous=True)
        assert refresh_time_previous.day == (current_time - timedelta(days=1)).day
