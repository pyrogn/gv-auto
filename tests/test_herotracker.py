import pytest
from datetime import datetime
from unittest import mock
from gv_auto.hero import (
    HeroTracker,
    StateManager,
    TimeManager,
    TIMEZONE,
    BINGO_TIMEOUT_MIN,
)
from gv_auto.environment import EnvironmentInfo
from gv_auto.response import Responses


@pytest.fixture
def mock_env():
    return mock.Mock(spec=EnvironmentInfo)


@pytest.fixture
def mock_state_manager():
    state_manager = mock.Mock(spec=StateManager)
    state_manager.default_state = {
        "return_counter": 0,
        "bingo_counter": 3,
        "last_bingo_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
        "last_melting_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
        "last_sync_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
        "when_godvoice_available": datetime(2020, 1, 1, tzinfo=TIMEZONE),
        "quest_n": 0,
    }
    state_manager.load_state.return_value = state_manager.default_state.copy()
    return state_manager


@pytest.fixture
def hero_tracker(mock_env, mock_state_manager):
    return HeroTracker(env=mock_env, state_manager=mock_state_manager)


def test_can_return(hero_tracker):
    hero_tracker.env.quest = [0]
    assert hero_tracker.can_return
    hero_tracker.state["return_counter"] = 2
    assert not hero_tracker.can_return


def test_register_return(hero_tracker):
    hero_tracker.register_return()
    assert hero_tracker.state["return_counter"] == 1
    hero_tracker.state_manager.save_state.assert_called_once()


def test_update_return_cnt(hero_tracker):
    hero_tracker.update_return_cnt(1)
    assert hero_tracker.state["return_counter"] == 0
    assert hero_tracker.state["quest_n"] == 1
    hero_tracker.state_manager.save_state.assert_called_once()


def test_is_bingo_available(hero_tracker):
    with mock.patch.object(
        TimeManager, "seconds_from_time", return_value=BINGO_TIMEOUT_MIN * 60 + 1
    ):
        assert hero_tracker.is_bingo_available
    hero_tracker.state["bingo_counter"] = 0
    assert not hero_tracker.is_bingo_available


def test_register_bingo_attempt(hero_tracker):
    hero_tracker.register_bingo_attempt()
    assert hero_tracker.state["last_bingo_time"] == TimeManager.current_time()
    hero_tracker.state_manager.save_state.assert_called_once()


def test_register_bingo_play(hero_tracker):
    hero_tracker.state["bingo_counter"] = 1
    hero_tracker.register_bingo_play()
    assert hero_tracker.state["bingo_counter"] == 0
    hero_tracker.state_manager.save_state.assert_called_once()
    with pytest.raises(ValueError):
        hero_tracker.register_bingo_play()


def test_update_bingo_counter(hero_tracker):
    hero_tracker.update_bingo_counter(2)
    assert hero_tracker.state["bingo_counter"] == 2
    hero_tracker.state_manager.save_state.assert_called_once()


def test_is_bingo_ended(hero_tracker):
    hero_tracker.state["bingo_counter"] = 0
    assert hero_tracker.is_bingo_ended
    hero_tracker.state["bingo_counter"] = 1
    assert not hero_tracker.is_bingo_ended


def test_is_melting_available(hero_tracker):
    with mock.patch.object(TimeManager, "seconds_from_time", return_value=21):
        assert hero_tracker.is_melting_available
    with mock.patch.object(TimeManager, "seconds_from_time", return_value=19):
        assert not hero_tracker.is_melting_available


def test_register_melting(hero_tracker):
    hero_tracker.register_melting()
    assert hero_tracker.state["last_melting_time"] == TimeManager.current_time()
    hero_tracker.state_manager.save_state.assert_called_once()


def test_is_godvoice_available(hero_tracker):
    with mock.patch.object(
        TimeManager,
        "current_time",
        return_value=datetime(2024, 6, 24, 21, 0, 0, tzinfo=TIMEZONE),
    ):
        assert hero_tracker.is_godvoice_available
    with mock.patch.object(
        TimeManager,
        "current_time",
        return_value=datetime(2024, 6, 24, 20, 0, 0, tzinfo=TIMEZONE),
    ):
        assert not hero_tracker.is_godvoice_available


def test_register_godvoice(hero_tracker):
    hero_tracker.register_godvoice(Responses.IGNORED)
    assert hero_tracker.state["when_godvoice_available"] == TimeManager.get_future_time(
        20
    )
    hero_tracker.state_manager.save_state.assert_called_once()
    hero_tracker.register_godvoice(Responses.RESPONDED)
    assert hero_tracker.state["when_godvoice_available"] == TimeManager.get_future_time(
        60
    )
    hero_tracker.state_manager.save_state.assert_called()


if __name__ == "__main__":
    pytest.main()
