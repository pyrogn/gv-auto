import pytest
from datetime import datetime, timedelta
from unittest import mock
import pytz
from gv_auto.environment import TIMEZONE
from gv_auto.hero import TimeManager


@pytest.fixture
def mock_time():
    return datetime(2024, 6, 24, 23, 0, 0, tzinfo=pytz.timezone("UTC"))


def test_current_time(mock_time):
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        current_time = TimeManager.current_time()
        assert current_time == mock_time


def test_get_game_refresh_time(mock_time):
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        refresh_time = TimeManager.get_game_refresh_time(offset_min=5)
        expected_time = mock_time.replace(
            hour=0, minute=5, second=0, microsecond=0
        ) + timedelta(minutes=5)
        if mock_time > expected_time:
            expected_time += timedelta(days=1)
        assert refresh_time == expected_time


def test_get_game_refresh_time_previous(mock_time):
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        refresh_time = TimeManager.get_game_refresh_time(offset_min=5, previous=True)
        expected_time = (
            mock_time.replace(hour=0, minute=5, second=0, microsecond=0)
            + timedelta(minutes=5)
            - timedelta(days=1)
        )
        if mock_time > expected_time + timedelta(days=1):
            expected_time += timedelta(days=1)
        assert refresh_time == expected_time


def test_bingo_last_call(mock_time):
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        refresh_time = TimeManager.get_game_refresh_time()
        bingo_last_call = TimeManager.bingo_last_call()
        seconds_left_to_deadline = (refresh_time - mock_time).total_seconds()
        expected = seconds_left_to_deadline / 60 < 120
        assert bingo_last_call == expected


def test_get_future_time(mock_time):
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        future_time = TimeManager.get_future_time(3600)  # 1 hour into the future
        expected_time = mock_time + timedelta(seconds=3600)
        assert future_time == expected_time


def test_seconds_from_time(mock_time):
    past_time = mock_time - timedelta(seconds=3600)
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=mock_time):
        seconds = TimeManager.seconds_from_time(past_time)
        assert seconds == 3600


def test_timezone_conversion():
    local_time = datetime(
        2024, 6, 24, 20, 0, 0, tzinfo=pytz.timezone("America/New_York")
    )
    moscow_time = local_time.astimezone(TIMEZONE)
    assert moscow_time.tzinfo == TIMEZONE


def test_next_deadline_moved_by_one_day():
    current_time = datetime(2024, 6, 24, 23, 0, 0, tzinfo=TIMEZONE)
    with mock.patch("gv_auto.hero.TimeManager.current_time", return_value=current_time):
        refresh_time = TimeManager.get_game_refresh_time()
        assert refresh_time.day == (current_time + timedelta(days=1)).day
        refresh_time_previous = TimeManager.get_game_refresh_time(previous=True)
        assert refresh_time_previous.day == current_time.day


if __name__ == "__main__":
    pytest.main()
