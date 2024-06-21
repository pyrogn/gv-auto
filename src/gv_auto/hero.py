from datetime import datetime, timedelta
import random
import logging
from gv_auto.logger import setup_logging
from gv_auto.states import INFLUENCE_TYPE, VOICEGOD_TASK, voicegods_map
from selenium.webdriver.common.keys import Keys  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)


class HeroTracker:
    """Tracks available options for a hero (like timeouts and restrictions)."""

    def __init__(self):
        self._return_counter = 0
        self.bingo_counter = 3
        self.last_bingo_time = datetime(2020, 1, 1)
        self.last_coupon_time = datetime(2020, 1, 1)
        self.last_melting_time = datetime(2020, 1, 1)

    @property
    def can_return(self):
        # add 6 non working voices in a row
        return self._return_counter < 2

    def register_return(self):
        self._return_counter += 1

    def register_quest(self):
        self._return_counter += 1

    def reset_return_cnt(self):
        self._return_counter = 0

    def _sync_bingo_time(self):
        if self.last_bingo_time < datetime.now().replace(
            hour=0, minute=7, second=0, microsecond=0
        ):
            logger.info("Bingo counter is resetted")
            self.bingo_counter = 3

    @property
    def bingo_last_call(self):
        current_time = datetime.now()
        deadline = current_time.replace(hour=0, minute=5, second=0, microsecond=0)

        if current_time > deadline:
            deadline += timedelta(days=1)

        seconds_left_to_deadline = (deadline - current_time).total_seconds()
        return seconds_left_to_deadline / 60 < 120

    @property
    def is_bingo_available(self):
        self._sync_bingo_time()

        timeout_minutes = 15
        return (self.bingo_counter > 0) and (
            (datetime.now() - self.last_bingo_time).seconds > timeout_minutes * 60
        )

    def register_bingo_attempt(self):
        self.last_bingo_time = datetime.now()

    def register_bingo_play(self):
        self.bingo_counter -= 1

    @property
    def is_coupon_available(self):
        # True if last coupon time less than today 00:06
        return self.last_coupon_time < datetime.now().replace(
            hour=0, minute=6, second=0, microsecond=0
        )

    def register_coupon(self):
        self.last_coupon_time = datetime.now()

    @property
    def is_melting_available(self):
        return (datetime.now() - self.last_melting_time).seconds > 20

    def register_melting(self):
        self.last_melting_time = datetime.now()

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
        if not self.driver.is_element_visible("#bgn_end"):
            self.hero_tracker.is_bingo_ended = True
            logging.info("Bingo ended")
        else:
            self.hero_tracker.is_bingo_ended = False
        if self.hero_tracker.is_bingo_available:
            self.driver.uc_open("https://godville.net/news")
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
                        logger.error("Tried to end bingo, but button isn't clickable")

            # coupon
            if self.hero_tracker.is_coupon_available:
                button_selector = "#coupon_b"
                if self.driver.is_element_clickable(button_selector):
                    self.driver.uc_click(button_selector)
                else:
                    logger.error("Coupon element is not clickable")
                self.hero_tracker.register_coupon()

            # come back
            self.driver.uc_open("https://godville.net/superhero")

    def go_to_zpg_arena(self): ...
