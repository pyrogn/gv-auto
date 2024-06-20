from datetime import datetime
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
        self.bingo_counter = 0
        self.last_bingo_time = datetime(2020, 1, 1)
        self.last_coupon_time = datetime(2020, 1, 1)

    @property
    def can_return(self):
        return self._return_counter

    @can_return.setter
    def _(self, val):
        self._return_counter = val

    def register_quest(self):
        self._return_counter += 1

    def reset_quest(self):
        self._return_counter = 0

    @property
    def is_bingo_available(self):
        return (self.bingo_counter < 3) and (
            (datetime.now() - self.last_bingo_time).seconds > 10 * 60
        )

    def register_bingo(self):
        self.bingo_counter += 1
        self.last_bingo_time = datetime.now()

    @property
    def is_coupon_available(self):
        # True if last coupon time less than today 00:06
        return self.last_coupon_time < datetime.now().replace(
            hour=0, minute=6, second=0, microsecond=0
        )

    def register_coupon(self):
        self.last_coupon_time = datetime.now()


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
                logger.error("There is a problem with choosing a strategy")
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

    def play_bingo(self):
        if self.hero_tracker.is_bingo_available:
            self.driver.uc_open("https://godville.net/news")
            self.driver.uc_click("#bgn_show")
            logger.info("Trying to play bingo")
            self.driver.reconnect(0.5)
            if self.driver.is_element_clickable("#bgn_use"):
                text = self.driver.get_text("#b_inv")  # to find number of matches
                self.driver.uc_click("#bgn_use")
                logger.info(f"Bingo played: {text}")
                self.hero_tracker.register_bingo()
                return
            logger.error("Bingo element is not clickable")
        logger.error("Bingo is not available (many clicks)")
