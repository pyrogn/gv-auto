import re
import logging
from bs4 import BeautifulSoup
from gv_auto.states import HeroStates, str_state2enum_state


class EnvironmentInfo:
    def __init__(self, driver):
        self.driver = driver

    def _get_text(self, selector):
        try:
            return self.driver.get_text(selector)
        except Exception as e:
            logging.error(f"Error retrieving text from {selector}: {e}")
            return ""

    def _get_re_from_text(self, selector, regex=r"\d+"):
        try:
            text = self._get_text(selector)
            return re.search(regex, text).group()
        except Exception as e:
            logging.error(f"Error parsing integer from {selector}: {e}")
            return 0

    @property
    def state(self):
        state = self._get_text("#news > div.block_h > h2").split(" ")[0]
        return state if state else "Unknown"

    @property
    def state_enum(self):
        return str_state2enum_state.get(self.state, HeroStates.UNKNOWN)

    @property
    def money(self):
        return int(self._get_re_from_text("#hk_gold_we > div.l_val"))

    @property
    def prana(self):
        return int(
            self._get_re_from_text("#cntrl > div.pbar.line > div.gp_val", regex=r"\d+")
        )

    @property
    def bricks(self):
        try:
            return int(float(self._get_text("#hk_bricks_cnt > div.l_val")[:-1]) * 10)
        except Exception:
            return 0

    @property
    def health(self):
        try:
            health_str = self._get_text("#hk_health > div.l_val")
            cur_health, all_health = map(int, re.findall(r"\d+", health_str))
            return int(cur_health / all_health * 100)
        except Exception as e:
            logging.error(f"Error retrieving health: {e}")
            return 0

    @property
    def is_in_town(self):
        where = self._get_text("#hk_distance > div.l_capt")
        return where == "Город"

    @property
    def closest_city(self):
        position, _ = self.position
        return GameState(self.driver).find_closest_town(position)

    @property
    def position(self):
        try:
            is_in_town = self.is_in_town
            miles = self._get_text("#hk_distance > div.l_val")
            if not is_in_town:
                miles = int(re.search(r"\d+", miles).group())
                area = "В пути"
            else:
                area = self.driver.get_attribute("g.tl.sl title", "textContent")
                miles = int(re.search(r"\d+", area).group())
                area = re.search(r"(.+?)\s*\(", area).group(1)
            return miles, area
        except Exception as e:
            logging.error(f"Error retrieving position: {e}")
            return 0, "Unknown"

    @property
    def inventory(self):
        try:
            inv_str = self._get_text("#hk_inventory_num > div.l_val")
            cur_inv, all_inv = map(int, re.findall(r"\d+", inv_str))
            return int(cur_inv / all_inv * 100)
        except Exception as e:
            logging.error(f"Error retrieving inventory: {e}")
            return 0

    @property
    def quest(self):
        try:
            quest = self._get_text("#hk_quests_completed > div.q_name")
            return quest
        except Exception as e:
            logging.error(f"Error retrieving inventory: {e}")
            return ""

    @property
    def all_info(self):
        try:
            return f"{self.state}|money:{self.money}|prana:{self.prana}|inv:{self.inventory}|bricks:{self.bricks}|hp:{self.health}|where:{','.join(map(str, self.position))}|city:{self.closest_city}|quest:{self.quest}"
        except Exception as e:
            logging.error(f"Error retrieving all information: {e}")
            return "Error retrieving all information"


class GameState:
    def __init__(self, driver):
        self.driver = driver
        self.town_map = self.city_map()

    def city_map(self):
        html_content = self.driver.get_page_source()
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
