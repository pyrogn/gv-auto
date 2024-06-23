from datetime import datetime
import re
import logging
from bs4 import BeautifulSoup
from gv_auto.logger import setup_logging
from gv_auto.states import HeroStates, str_state2enum_state

setup_logging()
logger = logging.getLogger(__name__)


class EnvironmentInfo:
    def __init__(self, dm):
        self.dm = dm

    def _get_text(self, selector):
        try:
            return self.dm.driver.get_text(selector)
        except Exception as e:
            logger.error(f"Error retrieving text from {selector}: {e}")
            return ""

    def _get_re_from_text(self, selector, regex=r"\d+"):
        try:
            text = self._get_text(selector)
            if text == "нет":  # for gold
                return 0
            return re.search(regex, text).group()
        except Exception as e:
            logger.error(f"Error parsing integer from {selector}: {e}. Text: {text}")
            return ""

    @property
    def state(self) -> str:
        if self.dm.driver.is_element_present("#diary"):
            state = self._get_text("#news > div.block_h > h2").split(" ")[0]
        elif self.dm.driver.is_element_present("#m_fight_log"):
            state = "Битва"
        return state or "Unknown"

    @property
    def state_enum(self) -> HeroStates:
        return str_state2enum_state.get(self.state, HeroStates.UNKNOWN)

    @property
    def money(self) -> int:
        try:
            return int(self._get_re_from_text("#hk_gold_we > div.l_val"))
        except Exception:  # in case of some greater problem
            return 0

    @property
    def prana(self) -> int:
        return int(
            self._get_re_from_text("#cntrl > div.pbar.line > div.gp_val", regex=r"\d+")
        )

    @property
    def bricks(self) -> int:
        try:
            return int(float(self._get_text("#hk_bricks_cnt > div.l_val")[:-1]) * 10)
        except Exception:
            return 0

    @property
    def health(self) -> tuple[int, int]:
        try:
            health_str = self._get_text("#hk_health > div.l_val")
            cur_health, all_health = map(int, re.findall(r"\d+", health_str))
            return cur_health, all_health
        except Exception as e:
            logger.error(f"Error retrieving health: {e}")
            return 1, 2

    @property
    def health_perc(self) -> int:
        cur_health, all_health = self.health
        return int(cur_health / all_health * 100)

    @property
    def is_in_town(self) -> bool:
        where = self._get_text("#hk_distance > div.l_capt")
        return where == "Город"

    @property
    def closest_town(self) -> str:
        position, _ = self.position
        return GameState(self.dm).find_closest_town(position)

    @property
    def position(self) -> tuple[int, str]:
        try:
            is_in_town = self.is_in_town
            miles = self._get_text("#hk_distance > div.l_val")
            if not is_in_town:
                miles = int(re.search(r"\d+", miles).group())
                area = "В пути"
            else:
                area = self.dm.driver.get_attribute("g.tl.sl title", "textContent")
                miles = int(re.search(r"\d+", area).group())
                area = re.search(r"(.+?)\s*\(", area).group(1)
            return miles, area
        except Exception as e:
            logger.error(f"Error retrieving position: {e}")
            return 0, "Unknown"

    @property
    def inventory(self) -> tuple[int, int]:
        try:
            inv_str = self._get_text("#hk_inventory_num > div.l_val")
            cur_inv, all_inv = map(int, re.findall(r"\d+", inv_str))
            return cur_inv, all_inv
        except Exception as e:
            logger.error(f"Error retrieving inventory: {e}")
            return 1, 2

    @property
    def inventory_perc(self) -> int:
        cur_inv, all_inv = self.inventory
        return int(cur_inv / all_inv * 100)

    @property
    def quest(self) -> tuple[int, str]:
        try:
            quest = self._get_text("#hk_quests_completed > div.q_name")
            quest_n = int(
                self._get_re_from_text("#hk_quests_completed > div.l_val", r"\d+")
            )
            return quest_n, quest
        except Exception as e:
            logger.error(f"Error retrieving inventory: {e}")
            return 0, ""

    @property
    def all_info(self) -> str:
        try:
            if self.state_enum is HeroStates.DUEL:
                return "Duel is in progress"
            return (
                f"{self.state}|"
                f"money:{self.money}|"
                f"prana:{self.prana}|"
                f"inv:{self.inventory_perc}|"
                f"bricks:{self.bricks}|"
                f"hp:{self.health_perc}|"
                f"where:{','.join(map(str, self.position))}|"
                f"town:{self.closest_town}|"
                f"quest:{','.join(map(str, self.quest))}"
            )
        except Exception as e:
            logger.error(f"Error retrieving all information: {e}")
            return "Error retrieving all information"

    def is_arena_available(self, zpg=True) -> bool:
        if zpg:
            current_time = datetime.now()
            current_seconds = current_time.minute * 60 + current_time.second
            offset = 15
            # first 3 minutes of every hour
            if not (0 + offset // 2 < current_seconds < 180 - offset):
                return False
        return self.dm.driver.is_link_text_visible("Отправить на арену")


class GameState:
    def __init__(self, dm):
        self.dm = dm
        # we may cache this map
        # because it updates daily
        self.town_map = self.get_town_map()

    def get_town_map(self):
        html_content = self.dm.driver.get_page_source()
        soup = BeautifulSoup(html_content, "html.parser")
        towns = soup.find_all("g", class_="tl")
        town_map = {}

        for town in towns:
            title = town.find("title")
            if title:
                town_text = title.get_text()
                match = re.search(r"(.*?) \((\d+)\)", town_text)
                if match:
                    town_name = match.group(1)
                    miles = int(match.group(2))
                    town_map[miles] = town_name
        return town_map

    def find_closest_town(self, position):
        possible_towns = {k: v for k, v in self.town_map.items() if k <= position}
        if not possible_towns:
            return "No towns found in range"
        closest_distance = max(possible_towns.keys())
        return possible_towns[closest_distance]
