from datetime import datetime, timedelta
import re
import logging
import traceback
from bs4 import BeautifulSoup
import pytz
from gv_auto.logger import LogError, setup_logging
from gv_auto.game_info import (
    USEFUL_AND_FUN_ACTIVATABLES,
    HeroStates,
    HERO_STATE_STR2ENUM,
)

import time
from functools import wraps

setup_logging()
logger = logging.getLogger(__name__)
TIMEZONE = pytz.timezone("Europe/Moscow")


class TimeManager:
    """Менеджмент времени (обновление игры и задержки для влияний)."""

    def __init__(self): ...

    @staticmethod
    def current_time() -> datetime:
        return datetime.now(TIMEZONE)

    @classmethod
    def get_game_refresh_time(cls, offset_min: int = 0, previous=False) -> datetime:
        """Get time of next game refresh (map update and bingo reset)."""
        current_time = cls.current_time()
        deadline = current_time.replace(
            hour=0, minute=5, second=0, microsecond=0
        ) + timedelta(minutes=offset_min)

        if current_time > deadline:
            deadline += timedelta(days=1)

        if previous:
            deadline -= timedelta(days=1)

        return deadline

    @classmethod
    def bingo_last_call(cls) -> bool:
        seconds_left_to_deadline = (
            cls.get_game_refresh_time() - cls.current_time()
        ).total_seconds()
        return seconds_left_to_deadline / 60 < 120

    @classmethod
    def get_future_time(cls, offset_sec: int) -> datetime:
        return cls.current_time() + timedelta(seconds=offset_sec)

    @classmethod
    def seconds_from_time(cls, time: datetime) -> int:
        return (cls.current_time() - time).total_seconds()

    @classmethod
    def is_zpg_time(cls) -> bool:
        current_time = cls.current_time()
        current_seconds = current_time.minute * 60 + current_time.second
        offset = 15
        # first 3 minutes of every hour
        return 0 + offset // 2 < current_seconds < 3 * 60 - offset


def cache_with_timeout(timeout):
    """Cache source page and use it for 1 seconds for parsing attributes."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            current_time = time.time()
            if (not hasattr(self, "_cache")) or (
                current_time - self._cache_time > timeout
            ):
                self._cache = self.driver.get_page_source()
                self._cache_time = current_time
                self._soup = BeautifulSoup(self._cache, "html.parser")
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class GameState:
    """Game map (towns and their position)."""

    def __init__(self, driver):
        self.driver = driver
        self.town_map = self._get_town_map()
        self.next_update_time = TimeManager.get_game_refresh_time(offset_min=1)

    def _get_town_map(self) -> dict[int, str]:
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

    def _update_town_map_if_needed(self) -> None:
        now = TimeManager.current_time()
        if now > self.next_update_time:
            logger.info("Updated world map")
            self.town_map = self._get_town_map()
            self.next_update_time = TimeManager.get_game_refresh_time(offset_min=1)

    def find_closest_town(self, position) -> str:
        self._update_town_map_if_needed()
        possible_towns = {k: v for k, v in self.town_map.items() if k <= position}
        if not possible_towns:
            return "No towns found in range"
        closest_distance = max(possible_towns.keys())
        return possible_towns[closest_distance]


class EnvironmentInfo:
    """Парсинг информации о герое и окружении из главной страницы."""

    def __init__(self, driver):
        self.driver = driver
        self._cache = None
        self._cache_time = 0
        self._soup = None
        self.game_state = GameState(self.driver)

    def _get_text(self, selector):
        try:
            element = self._soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
        except Exception as e:
            logger.error(
                f"Error retrieving text from {selector}: {e}\n{traceback.format_exc()}"
            )
            LogError(self.driver).log_error()
            return ""

    def _get_re_from_text(self, selector, regex=r"\d+"):
        try:
            text = self._get_text(selector)
            if text == "нет":  # for gold
                return 0
            return re.search(regex, text).group()
        except Exception as e:
            logger.error(
                f"Error parsing integer from {selector}: {e}. Text: {text}\n{traceback.format_exc()}"
            )
            LogError(self.driver).log_error()
            return ""

    @property
    @cache_with_timeout(1)
    def state(self) -> str:
        if self._soup.select_one("#diary"):
            state = self._get_text("#news > div.block_h > h2").split(" ")[0]
        elif self._soup.select_one("#m_fight_log"):
            state = "Битва"
        return state or "Unknown"

    @property
    @cache_with_timeout(1)
    def state_enum(self) -> HeroStates:
        return HERO_STATE_STR2ENUM.get(self.state, HeroStates.UNKNOWN)

    @property
    @cache_with_timeout(1)
    def money(self) -> int:
        try:
            return int(self._get_re_from_text("#hk_gold_we > div.l_val"))
        except Exception:  # in case of some greater problem
            return 0

    @property
    @cache_with_timeout(1)
    def prana(self) -> int:
        return int(
            self._get_re_from_text("#cntrl > div.pbar.line > div.gp_val", regex=r"\d+")
        )

    @property
    @cache_with_timeout(1)
    def bricks(self) -> int:
        selector_bricks = "#hk_bricks_cnt > div.l_val"
        if self._soup.select_one(selector_bricks):
            return int(float(self._get_text(selector_bricks)[:-1]) * 10)
        return 0

    @property
    @cache_with_timeout(1)
    def health(self) -> tuple[int, int]:
        try:
            health_str = self._get_text("#hk_health > div.l_val")
            cur_health, all_health = map(int, re.findall(r"\d+", health_str))
            return cur_health, all_health
        except Exception as e:
            logger.error(f"Error retrieving health: {e}")
            return 1, 2

    @property
    @cache_with_timeout(1)
    def health_perc(self) -> int:
        cur_health, all_health = self.health
        return int(cur_health / all_health * 100)

    @property
    @cache_with_timeout(1)
    def is_in_town(self) -> bool:
        where = self._get_text("#hk_distance > div.l_capt")
        return where == "Город"

    @property
    @cache_with_timeout(1)
    def closest_town(self) -> str:
        position, _ = self.position
        return self.game_state.find_closest_town(position)

    @property
    @cache_with_timeout(1)
    def position(self) -> tuple[int, str]:
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
            logger.error(f"Error retrieving position: {e}\n{traceback.format_exc()}")
            LogError(self.driver).log_error()
            return 0, "Unknown"

    @property
    @cache_with_timeout(1)
    def inventory(self) -> tuple[int, int]:
        try:
            inv_str = self._get_text("#hk_inventory_num > div.l_val")
            cur_inv, all_inv = map(int, re.findall(r"\d+", inv_str))
            return cur_inv, all_inv
        except Exception as e:
            logger.error(f"Error retrieving inventory: {e}")
            return 1, 2

    @property
    @cache_with_timeout(1)
    def inventory_perc(self) -> int:
        cur_inv, all_inv = self.inventory
        return int(cur_inv / all_inv * 100)

    @property
    @cache_with_timeout(1)
    def quest(self) -> tuple[int, str]:
        try:
            quest = self._get_text("#hk_quests_completed > div.q_name")
            quest_n = int(
                self._get_re_from_text("#hk_quests_completed > div.l_val", r"\d+")
            )
            return quest_n, quest
        except Exception as e:
            logger.error(f"Error retrieving quest: {e}")
            return 0, ""

    @property
    @cache_with_timeout(1)
    def level(self) -> int:
        return int(self._get_re_from_text("#hk_level > div.l_val", r"\d+"))

    @property
    @cache_with_timeout(1)
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
        if zpg and not TimeManager.is_zpg_time():
            return False
        return self.driver.is_link_text_visible("Отправить на арену")

    @staticmethod
    def get_relevant_class(class_attribute):
        classes = class_attribute
        for cls in classes:
            if cls.startswith("type-"):
                return cls
        return None

    @property
    @cache_with_timeout(1)
    def activatables(self):
        items = self._soup.select("ul.ul_inv > li")
        activatables = []
        for item in items:
            class_attribute = item.get("class")
            if class_attribute:
                relevant_class = self.get_relevant_class(class_attribute)
                if relevant_class in USEFUL_AND_FUN_ACTIVATABLES:
                    item_name = item.select_one("span").text
                    title_element = item.select_one("div > a")
                    title = title_element.get("title") if title_element else ""
                    prana_price = None
                    match = re.search(r"\((.*?)\)", title)
                    if match:
                        parentheses_text = match.group(1)
                        price = re.search(r"\d+", parentheses_text)
                        prana_price = int(price.group(0)) if price else 0
                    activatables.append(
                        {
                            "item": item,
                            "name": item_name,
                            "class": relevant_class,
                            "title": title,
                            "prana_price": prana_price,
                        }
                    )
        return activatables
