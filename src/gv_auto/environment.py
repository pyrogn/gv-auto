import re
import logging
from gv_auto.states import HeroStates
from gv_auto.states import str_state2enum_state


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
        return int(float(self._get_text("#hk_bricks_cnt > div.l_val")[:-1]) * 10)

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
    def position(self):
        try:
            where = self._get_text("#hk_distance > div.l_capt")
            is_in_town = where == "Город"
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
    def all_info(self):
        try:
            return f"{self.state}|money:{self.money}|prana:{self.prana}|inv:{self.inventory}|bricks:{self.bricks}|hp:{self.health}|where:{','.join(map(str, self.position))}"
        except Exception as e:
            logging.error(f"Error retrieving all information: {e}")
            return "Error retrieving all information"
