from datetime import datetime, timedelta
import json
import random
import logging
import re
from gv_auto.logger import setup_logging
from gv_auto.response import Responses, UnderstandResponse
from gv_auto.states import INFLUENCE_TYPE, VOICEGOD_TASK, voicegods_map
from selenium.webdriver.common.keys import Keys  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)


BINGO_TIMEOUT = 15


class HeroTracker:
    """Tracks available options for a hero (like timeouts and restrictions)."""

    def __init__(self):
        self._return_counter = 0
        self.bingo_counter = 3
        self.last_bingo_time = datetime(2020, 1, 1)
        self.last_melting_time = datetime(2020, 1, 1)
        self.last_sync_time = datetime(2020, 1, 1)
        self.when_godvoice_available = datetime(2020, 1, 1)

        self._load_state()

    def _load_state(self):
        try:
            with open("hero_tracker_state.json", "r") as f:
                state = json.load(f)
                self._return_counter = state["return_counter"]
                self.bingo_counter = state["bingo_counter"]
                self.last_bingo_time = datetime.fromisoformat(state["last_bingo_time"])
                self.last_melting_time = datetime.fromisoformat(
                    state["last_melting_time"]
                )
                self.last_sync_time = datetime.fromisoformat(state["last_sync_time"])
                self.when_godvoice_available = datetime.fromisoformat(
                    state["when_godvoice_available"]
                )
                # self.current_quest = state['current_quest']
        except (FileNotFoundError, ValueError):
            pass

    def _save_state(self):
        state = {
            "return_counter": self._return_counter,
            "bingo_counter": self.bingo_counter,
            "last_bingo_time": self.last_bingo_time.isoformat(),
            "last_melting_time": self.last_melting_time.isoformat(),
            "last_sync_time": self.last_sync_time.isoformat(),
            "when_godvoice_available": self.when_godvoice_available.isoformat(),
            # "current_quest": EnvironmentInfo(self.driver),
        }
        with open("hero_tracker_state.json", "w") as f:
            json.dump(state, f, indent=4)

    @property
    def can_return(self) -> bool:
        # add 6 non working voices in a row
        return self._return_counter < 2

    def register_return(self) -> None:
        self._return_counter += 1
        self._save_state()

    def reset_return_cnt(self) -> None:
        # if quest is new or there was mini quest
        self._return_counter = 0
        self._save_state()

    def _sync_bingo_time(self) -> None:
        """If last sync is past deadline, then reset counter."""
        current_time = datetime.now()
        # with small offset, but previous deadline
        previous_deadline = (
            self.deadline_bingo + timedelta(minutes=2) - timedelta(days=1)
        )
        if self.last_sync_time < previous_deadline:
            self.bingo_counter = 3
            self.last_sync_time = current_time
            self._save_state()
            logger.info("Bingo counter is reset")

    @property
    def deadline_bingo(self) -> datetime:
        current_time = datetime.now()
        deadline = current_time.replace(hour=0, minute=5, second=0, microsecond=0)

        if current_time > deadline:
            deadline += timedelta(days=1)
        return deadline

    @property
    def bingo_last_call(self) -> bool:
        current_time = datetime.now()

        seconds_left_to_deadline = (self.deadline_bingo - current_time).total_seconds()
        return seconds_left_to_deadline / 60 < 120

    @property
    def is_bingo_available(self) -> bool:
        self._sync_bingo_time()

        return (self.bingo_counter > 0) and (
            (datetime.now() - self.last_bingo_time).seconds > BINGO_TIMEOUT * 60
        )

    def register_bingo_attempt(self) -> None:
        self.last_bingo_time = datetime.now()
        self._save_state()

    def register_bingo_play(self) -> None:
        if self.bingo_counter <= 0:
            raise ValueError("Bingo counter cannot be less than 0")
        self.bingo_counter -= 1
        self._save_state()

    @property
    def is_melting_available(self):
        return (datetime.now() - self.last_melting_time).seconds > 20

    def register_melting(self):
        self.last_melting_time = datetime.now()
        self._save_state()

    @property
    def is_bingo_ended(self):
        self._sync_bingo_time()
        return self.bingo_counter > 0

    @property
    def is_godvoice_available(self):
        return datetime.now() > self.when_godvoice_available

    def register_godvoice(self, response: Responses):
        match response:
            case Responses.IGNORED:
                self.when_godvoice_available = datetime.now() + timedelta(seconds=20)
            case Responses.RESPONDED:
                self.when_godvoice_available = datetime.now() + timedelta(seconds=60)
        self._save_state()


class HeroActions:
    def __init__(self, driver, hero_tracker: HeroTracker) -> None:
        self.driver = driver
        self.hero_tracker = hero_tracker

    def _make_influence(self, influence: INFLUENCE_TYPE):
        match influence:
            case INFLUENCE_TYPE.ENCOURAGE:
                selector_add = "enc_link"
                element_text = "Сделать хорошо"
            case INFLUENCE_TYPE.PUNISH:
                selector_add = "pun_link"
                element_text = "Сделать плохо"

        selector = "#cntrl1 > a.no_link.div_link." + selector_add
        random_choice = random.randint(1, 3)
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
        except Exception as e:
            logger.error(f"Error in godvoice method: {e}")

    def play_bingo(self, finish=False):
        self.driver.uc_open("https://godville.net/news")
        try:
            # sync bingo progress
            if not self.driver.is_element_visible("#bgn_show"):
                self.hero_tracker.bingo_counter = 0
                logger.info("Bingo ended")
            else:
                left_plays_text = self.driver.get_text("#l_clicks")
                left_plays = int(
                    re.search(r"Осталось нажатий: (\d+)\.", left_plays_text).group(1)
                )
                self.hero_tracker.bingo_counter = left_plays
                logger.info(f"Осталось игр в бинго: {left_plays}")
            self.hero_tracker._save_state()

            if self.hero_tracker.is_bingo_available:
                self.driver.uc_click("#bgn_show")
                self.hero_tracker.register_bingo_attempt()
                logger.info("Trying to play bingo and get coupon")
                self.driver.reconnect(0.5)

                # bingo
                if self.driver.is_element_clickable("#bgn_use"):
                    text = self.driver.get_text("#b_inv")  # to find number of matches
                    self.driver.uc_click("#bgn_use")
                    logger.info(f"Bingo played: {text}")
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
                    self.driver.uc_click(coupon_selector)
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
        # add sleep (reconnect) during arena
