from datetime import datetime
import json
import random
import logging
import re

from gv_auto.environment import TIMEZONE, TimeManager, EnvironmentInfo
from gv_auto.logger import setup_logging
from gv_auto.response import Responses, UnderstandResponse
from gv_auto.game_info import (
    INFLUENCE_TYPE,
    VOICEGOD_TASK,
    HeroStates,
    voicegods_map,
    USEFUL_AND_FUN_ACTIVATABLES,
)
from selenium.webdriver.common.keys import Keys  # noqa: F401
from selenium.webdriver.common.by import By

setup_logging()
logger = logging.getLogger(__name__)


BINGO_TIMEOUT = 15


# need to test extensively these timezones, looks complicated
class StateManager:
    def __init__(self, file_path="hero_tracker_state.json"):
        self.file_path = file_path
        self.default_state = {
            "return_counter": 0,
            "bingo_counter": 3,
            "last_bingo_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
            "last_melting_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
            "last_sync_time": datetime(2020, 1, 1, tzinfo=TIMEZONE),
            "when_godvoice_available": datetime(2020, 1, 1, tzinfo=TIMEZONE),
            "quest_n": 0,
        }
        self.time_attributes = [
            "last_bingo_time",
            "last_melting_time",
            "last_sync_time",
            "when_godvoice_available",
        ]

    def _convert_state_times_to_str(self, state):
        for key in self.time_attributes:
            state[key] = state[key].isoformat()
        return state

    def _convert_state_times_to_datetime(self, state):
        for key in self.time_attributes:
            state[key] = datetime.fromisoformat(state[key]).astimezone(TIMEZONE)
        return state

    def load_state(self):
        try:
            with open(self.file_path, "r") as f:
                state = json.load(f)
                state = self._convert_state_times_to_datetime(state)
                return state
        except (FileNotFoundError, ValueError, KeyError):
            return self.default_state.copy()

    def save_state(self, state):
        state = self._convert_state_times_to_str(state)
        with open(self.file_path, "w") as f:
            json.dump(state, f, indent=4)
        state = self._convert_state_times_to_datetime(state)
        return state


def sync_bingo_time(method):
    def wrapper(self, *args, **kwargs):
        """If last sync is past deadline, then reset counter."""
        # with small offset, but previous deadline
        previous_deadline = TimeManager.get_game_refresh_time(
            offset_min=2, previous=True
        )
        if self.state["last_sync_time"] < previous_deadline:
            self.state["bingo_counter"] = 3
            self.state["last_sync_time"] = TimeManager.current_time()
            self.state = self.state_manager.save_state(self.state)  # can be a decorator
            logger.info("Bingo counter is reset")
        return method(self, *args, **kwargs)

    return wrapper


def save_state(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.state = self.state_manager.save_state(self.state)
        return result

    return wrapper


class HeroTracker:
    """Tracks available options for a hero (like timeouts and restrictions)."""

    def __init__(self, env: EnvironmentInfo, state_manager: StateManager):
        self.env = env
        self.state_manager = state_manager
        self.state = self.state_manager.load_state()
        self.logger = logging.getLogger(__name__)

    @property
    def can_return(self) -> bool:
        self.update_return_cnt(self.env.quest[0])
        return self.state["return_counter"] < 2

    @save_state
    def register_return(self) -> None:
        self.state["return_counter"] += 1

    def update_return_cnt(self, quest_n: int) -> None:
        # maybe add logic on mini quest (when its done) (it's hard)
        # how to know if a player has finished a mini quest and not dropped it?
        if quest_n != self.state["quest_n"]:
            self.state["return_counter"] = 0
            self.state["quest_n"] = quest_n
            self.state_manager.save_state(self.state)

    @property
    @sync_bingo_time
    def is_bingo_available(self) -> bool:
        return (self.state["bingo_counter"] > 0) and (
            TimeManager.seconds_from_time(self.state["last_bingo_time"])
            > BINGO_TIMEOUT * 60
        )

    @save_state
    def register_bingo_attempt(self) -> None:
        self.state["last_bingo_time"] = TimeManager.current_time()

    @save_state
    def register_bingo_play(self) -> None:
        if self.state["bingo_counter"] <= 0:
            raise ValueError("Bingo counter cannot be less than 0")
        self.state["bingo_counter"] -= 1

    @save_state
    def update_bingo_counter(self, left_plays):
        self.state["bingo_counter"] = left_plays

    @property
    @sync_bingo_time
    def is_bingo_ended(self):
        return self.state["bingo_counter"] <= 0

    @property
    def is_melting_available(self) -> bool:
        return TimeManager.seconds_from_time(self.state["last_melting_time"]) > 20

    @save_state
    def register_melting(self) -> None:
        self.state["last_melting_time"] = TimeManager.current_time()

    @property
    def is_godvoice_available(self):
        return TimeManager.current_time() > self.state["when_godvoice_available"]

    @save_state
    def register_godvoice(self, response: Responses):
        match response:
            case Responses.IGNORED:
                self.state["when_godvoice_available"] = TimeManager.get_future_time(20)
            case Responses.RESPONDED:
                self.state["when_godvoice_available"] = TimeManager.get_future_time(60)


class HeroActions:
    def __init__(self, driver, hero_tracker: HeroTracker, env: EnvironmentInfo) -> None:
        self.driver = driver
        self.hero_tracker = hero_tracker
        self.env = env

    def _make_influence(self, influence: INFLUENCE_TYPE):
        match influence:
            case INFLUENCE_TYPE.ENCOURAGE:
                selector_add = "enc_link"
                element_text = "Сделать хорошо"
            case INFLUENCE_TYPE.PUNISH:
                selector_add = "pun_link"
                element_text = "Сделать плохо"

        selector = "#cntrl1 > a.no_link.div_link." + selector_add
        random_choice = random.randint(1, 3)  # no preference
        match random_choice:
            case 1:
                self.driver.click(selector)
            case 2:
                self.driver.click_link(element_text)
            case 3:
                self.driver.hover_and_click(selector, selector)
            case 4:  # doesn't work with UI+
                self.driver.focus(selector)
                self.driver.send_keys(selector, Keys.RETURN)
            case _:
                logger.error(
                    f"{random_choice} is not a valid choice "
                    "for influence methods roulette"
                )
        if influence == INFLUENCE_TYPE.PUNISH:
            self.hero_tracker.register_melting()
        logger.info(f"Influence was made with {random_choice} strategy")

    def influence(self, infl_type: INFLUENCE_TYPE):
        try:
            self._make_influence(infl_type)
            logger.info(f"Influence action '{infl_type.name}' executed successfully.")
        except Exception as e:
            logger.error(f"Error in influence method: {e}")

    def godvoice(self, task: VOICEGOD_TASK):
        try:
            text = random.choice(voicegods_map[task])
            self.driver.type("#godvoice", text)
            self.driver.uc_click("#voice_submit")
            self.driver.reconnect(1)  # wait for response
            response = UnderstandResponse(self.driver).understand_response()
            self.hero_tracker.register_godvoice(response)
            logger.info(f"Godvoice command '{text}' executed. Hero {response.name}.")

            if (
                task == VOICEGOD_TASK.RETURN
                and response is Responses.RESPONDED
                and self.env.state_enum == HeroStates.RETURNING
            ):
                self.hero_tracker.register_return()
                logger.info(f"Return counter: {self.hero_tracker.return_counter}")

        except Exception as e:
            logger.error(f"Error in godvoice method: {e}")

    def play_bingo(self, finish=False):
        self.driver.uc_open("https://godville.net/news")
        try:
            # Sync bingo progress
            if not self.driver.is_element_visible("#bgn_show"):
                self.hero_tracker.update_bingo_counter(0)
                logger.info("Bingo ended")
            else:
                left_plays_text = self.driver.get_text("#l_clicks")
                left_plays = int(
                    re.search(r"Осталось нажатий: (\d+)\.", left_plays_text).group(1)
                )
                self.hero_tracker.update_bingo_counter(left_plays)
                logger.info(f"Осталось игр в бинго: {left_plays}")

            if self.hero_tracker.is_bingo_available:
                self.driver.uc_click("#bgn_show")
                self.hero_tracker.register_bingo_attempt()
                logger.info("Trying to play bingo and get coupon")
                self.driver.reconnect(0.5)

                # bingo
                if self.driver.is_element_clickable("#bgn_use"):
                    text = self.driver.get_text("#b_inv")  # to find number of matches
                    self.driver.uc_click("#bgn_use")
                    linear_text = re.sub(r"\s+", " ", text)
                    logger.info(f"Bingo played: {linear_text}")
                    self.hero_tracker.register_bingo_play()
                else:
                    logger.info("Bingo element is not clickable")
                    end_bingo_elem = "#bgn_end"
                    if finish and not self.hero_tracker.is_bingo_ended:
                        if self.driver.is_element_clickable(end_bingo_elem):
                            self.driver.uc_click(end_bingo_elem)
                            logger.info("Finished bingo before end")
                        else:
                            logger.error(
                                "Tried to end bingo, but button isn't clickable"
                            )

                coupon_selector = "#coupon_b"
                if self.driver.is_element_clickable(coupon_selector):
                    coupon_name = re.sub(r"\s+", " ", self.driver.get_text("#cpn_name"))
                    self.driver.uc_click(coupon_selector)
                    logger.info(f"Got coupon: {coupon_name}")
        finally:
            # come back
            self.driver.uc_open("https://godville.net/superhero")

    def go_to_zpg_arena(self):
        selector_arena = "#cntrl2 > div.arena_link_wrap > a"

        if not self.driver.is_element_visible(selector_arena):
            logger.error("Didn't see arena selector")
            return

        self.driver.find_element(selector_arena, timeout=1).click()
        self.driver.sleep(0.5)
        self.driver.accept_alert(2)
        logger.info("Accepted first confirm for arena")
        try:
            second_alert_text = self.driver.switch_to_alert(2).text
            self.driver.sleep(0.5)
            if "ZPG" in second_alert_text:
                self.driver.accept_alert(5)
                logger.info(f"Went to ZPG arena: {second_alert_text}")
            else:
                logger.error(f"Unknown text in second alert: {second_alert_text}")
        except Exception:
            logger.info("We got normal arena, didn't we?")

    def open_activatables(self):
        # add smelter and better management with prana
        inventory_items = self.driver.find_elements("ul.ul_inv > li")

        # REF: might get stale during iteration
        for item in inventory_items:
            class_attribute = item.get_attribute("class")
            match_good_activatables = any(
                name in class_attribute for name in USEFUL_AND_FUN_ACTIVATABLES
            )
            if match_good_activatables:
                item_name = item.find_element(By.TAG_NAME, "span").text
                title_element = item.find_element(By.CSS_SELECTOR, "div > a")
                title = title_element.get_attribute("title") if title_element else ""

                parentheses_text = None
                prana_price = None
                match = re.search(r"\((.*?)\)", title)
                if match:
                    parentheses_text = match.group(1)
                    price = re.search(r"\d+", parentheses_text)
                    if price:
                        prana_price = int(price.group(0))
                    else:
                        prana_price = 0

                if self.env.prana >= prana_price:
                    logger.info(
                        f"I have {item_name}, class: {class_attribute}, {title}, price: {prana_price}"
                    )
                    elem_click = item.find_element(By.CSS_SELECTOR, "div > a")
                    elem_click.click()
                    logger.info("Activated this item")
                    self.driver.reconnect(1)
                    response_str = UnderstandResponse(self.driver).get_response()
                    logger.info(f"Hero's response: {response_str}")

    def craft_items(self) -> None:
        # if element is here:
        # click on it and then press on sending godvoice
        # and then wait as in usual godvoice

        # and don't forget about settings of UI+
        # (craft enabled, certain combinations)

        # self.driver.uc_click("#voice_submit")
        # self.driver.reconnect(1)  # wait for response
        # response = UnderstandResponse(self.driver).understand_response()
        # self.hero_tracker.register_godvoice(response)
        # response_text = UnderstandResponse(self.driver).get_response()
        # logger.info(f"Crafting command executed. Hero {response.name}. {response_text}")
        ...
