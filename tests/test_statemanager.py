import pytest
import tempfile
import os
from datetime import datetime
from gv_auto.hero import StateManager, HeroState, TIMEZONE


@pytest.fixture
def temp_state_file():
    temp_dir = tempfile.TemporaryDirectory()
    yield os.path.join(temp_dir.name, "hero_tracker_state.json")
    temp_dir.cleanup()


def test_save_and_load_state(temp_state_file):
    state_manager = StateManager(file_path=temp_state_file)
    initial_state = HeroState(
        return_counter=2,
        bingo_counter=1,
        last_bingo_time=datetime(2022, 6, 25, 15, 0, tzinfo=TIMEZONE),
        last_melting_time=datetime(2022, 6, 25, 15, 0, tzinfo=TIMEZONE),
        last_sync_time=datetime(2022, 6, 25, 15, 0, tzinfo=TIMEZONE),
        when_godvoice_available=datetime(2022, 6, 25, 15, 0, tzinfo=TIMEZONE),
        quest_n=5,
    )

    # Save the state
    state_manager.save_state(initial_state)

    # Load the state
    loaded_state = state_manager.load_state()

    # Assert that the loaded state matches the initial state
    assert loaded_state == initial_state


def test_load_default_state_on_missing_file(temp_state_file):
    state_manager = StateManager(file_path=temp_state_file)

    # Ensure the state file does not exist
    if os.path.exists(temp_state_file):
        os.remove(temp_state_file)

    # Load the state
    loaded_state = state_manager.load_state()

    # Assert that the loaded state matches the default state
    assert loaded_state == state_manager.default_state


def test_load_default_state_on_corrupt_file(temp_state_file):
    state_manager = StateManager(file_path=temp_state_file)

    # Create a corrupt state file
    with open(temp_state_file, "w") as f:
        f.write("corrupt data")

    # Load the state
    loaded_state = state_manager.load_state()

    # Assert that the loaded state matches the default state
    assert loaded_state == state_manager.default_state


def test_save_and_load_state_with_different_values(temp_state_file):
    state_manager = StateManager(file_path=temp_state_file)
    modified_state = HeroState(
        return_counter=1,
        bingo_counter=2,
        last_bingo_time=datetime(2023, 7, 15, 18, 0, tzinfo=TIMEZONE),
        last_melting_time=datetime(2023, 7, 15, 18, 0, tzinfo=TIMEZONE),
        last_sync_time=datetime(2023, 7, 15, 18, 0, tzinfo=TIMEZONE),
        when_godvoice_available=datetime(2023, 7, 15, 18, 0, tzinfo=TIMEZONE),
        quest_n=10,
    )

    # Save the state
    state_manager.save_state(modified_state)

    # Load the state
    loaded_state = state_manager.load_state()

    # Assert that the loaded state matches the modified state
    assert loaded_state == modified_state
