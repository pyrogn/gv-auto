from datetime import datetime, timedelta
import json
import random
import logging
import re
from gv_auto.logger import setup_logging
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
        except (FileNotFoundError, ValueError):
            pass

    def _save_state(self):
        state = {
            "return_counter": self._return_counter,
            "bingo_counter": self.bingo_counter,
            "last_bingo_time": self.last_bingo_time.isoformat(),
            "last_melting_time": self.last_melting_time.isoformat(),
            "last_sync_time": self.last_sync_time.isoformat(),
        }
        with open("hero_tracker_state.json", "w") as f:
            json.dump(state, f)

    @property
    def can_return(self):
        # add 6 non working voices in a row
        return self._return_counter < 2

    def register_return(self):
        self._return_counter += 1
        self._save_state()

    def reset_return_cnt(self):
        # if quest is new or there was mini quest
        self._return_counter = 0
        self._save_state()

    def _sync_bingo_time(self):
        current_time = datetime.now()
        # with small offset
        next_deadline = self.deadline_bingo.replace(
            hour=0, minute=7, second=0, microsecond=0
        )
        if self.last_sync_time < next_deadline <= current_time:
            self.bingo_counter = 3
            self.last_sync_time = current_time
            self._save_state()
            logger.info("Bingo counter is reset")

    @property
    def deadline_bingo(self):
        current_time = datetime.now()
        deadline = current_time.replace(hour=0, minute=5, second=0, microsecond=0)

        if current_time > deadline:
            deadline += timedelta(days=1)
        return deadline

    @property
    def bingo_last_call(self):
        current_time = datetime.now()

        seconds_left_to_deadline = (self.deadline_bingo - current_time).total_seconds()
        return seconds_left_to_deadline / 60 < 120

    @property
    def is_bingo_available(self):
        self._sync_bingo_time()

        return (self.bingo_counter > 0) and (
            (datetime.now() - self.last_bingo_time).seconds > BINGO_TIMEOUT * 60
        )

    def register_bingo_attempt(self):
        self.last_bingo_time = datetime.now()
        self._save_state()

    def register_bingo_play(self):
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
        random_choice = random.randint(1, 4)
        match random_choice:
            case 1:
                self.driver.click(selector)
            case 2:
                self.driver.click_link(element_text)
            case 3:
                self.driver.hover_and_click(selector, selector)
            case 4:
                self.driver.focus(selector)
                self.driver.send_keys(selector, Keys.RETURN)
            case _:
                logger.error(f"{random_choice} is not a valid choice for influcence")
        if influence == INFLUENCE_TYPE.PUNISH:
            self.hero_tracker.register_melting()
        logger.info(f"Influence was made with {random_choice} strategy")

    def influence(self, infl_type: INFLUENCE_TYPE):
        try:
            self._make_influence(infl_type)
            logger.info(f"Influence action '{infl_type}' executed successfully.")
        except Exception as e:
            logger.error(f"Error in influence method: {e}")

    def godvoice(self, task: VOICEGOD_TASK):
        try:
            text = random.choice(voicegods_map[task])
            self.driver.type("#godvoice", text)
            self.driver.uc_click("#voice_submit")
            logger.info(f"Godvoice command '{text}' executed successfully.")
        except Exception as e:
            logger.error(f"Error in godvoice method: {e}")

    def play_bingo(self, finish=False):
        self.driver.uc_open("https://godville.net/news")
        try:
            # sync bingo progress
            if not self.driver.is_element_visible("#bgn_end"):
                self.hero_tracker.bingo_counter = 0
                logger.info("Bingo ended")
            else:
                left_plays_text = self.driver.get_text("#l_clicks")
                left_plays = int(
                    re.search(r"Осталось нажатий: (\d+)\.", left_plays_text).group(1)
                )
                self.hero_tracker.bingo_counter = left_plays
                logger.info("Осталось игр в бинго:", left_plays)

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

    def go_to_zpg_arena(self): ...
