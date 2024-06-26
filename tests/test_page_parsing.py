from pathlib import Path
from seleniumbase import SB
from unittest.mock import patch
from bs4 import BeautifulSoup

from gv_auto.environment import EnvironmentInfo
from gv_auto.game_info import HeroStates


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


def test_parsing():
    with SB(uc=True, headless2=True) as sb:
        uri = get_uri_for_html("pages/response.mhtml")
        sb.open(uri)
        env = EnvironmentInfo(sb)

        # Initial checks
        assert env.state_enum == HeroStates.WALKING
        assert env.prana == 41
        assert env.money == 83
        assert env.inventory_perc == 36
        assert env.bricks == 11
        assert env.health_perc == 100
        assert env.position[0] == 56
        assert env.closest_town == "Храмовище"
        assert env.position == (56, "В пути")
        assert env.level == 9
        assert env.quest == (6, "замолвить слово о бедном гусаре")

        # Simulate cache expiration by advancing time beyond the timeout and changing the content
        new_html = env.driver.get_page_source()
        soup = BeautifulSoup(new_html, "html.parser")

        # Modify some elements to simulate a change
        quest_element = soup.select_one("#hk_quests_completed > div.q_name")
        if quest_element:
            quest_element.string = "новый квест"

        prana_element = soup.select_one("#cntrl > div.pbar.line > div.gp_val")
        if prana_element:
            prana_element.string = "42"

        # Use the modified HTML content
        modified_html = str(soup)

        with patch("time.time") as mock_time:
            # Initial cache check within the timeout
            mock_time.return_value = env._cache_time + 0.5
            assert env.state_enum == HeroStates.WALKING
            assert env.prana == 41
            assert env.money == 83
            assert env.inventory_perc == 36
            assert env.bricks == 11
            assert env.health_perc == 100
            assert env.position[0] == 56
            assert env.closest_town == "Храмовище"
            assert env.position == (56, "В пути")
            assert env.level == 9
            assert env.quest == (6, "замолвить слово о бедном гусаре")

            # Update cache with new content after timeout
            mock_time.return_value = env._cache_time + 1.5
            env._cache = modified_html
            env._soup = BeautifulSoup(env._cache, "html.parser")
            env._cache_time = mock_time.return_value

            assert env.state_enum == HeroStates.WALKING
            assert env.prana == 42  # Updated value
            assert env.money == 83
            assert env.inventory_perc == 36
            assert env.bricks == 11
            assert env.health_perc == 100
            assert env.position[0] == 56
            assert env.closest_town == "Храмовище"
            assert env.position == (56, "В пути")
            assert env.level == 9
            assert env.quest == (6, "новый квест")  # Updated value
