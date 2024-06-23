from enum import Enum, auto
import logging
import random
import time
from seleniumbase import Driver

from gv_auto.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class SleepTime(Enum):
    STEP = auto()
    BREAK = auto()
    DUEL = auto()


class DriverManager:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.create_driver()

    def create_driver(self) -> None:
        self.driver = Driver(
            uc=True,
            headless2=self.headless,
            user_data_dir="./chrome_profile",
            # these options speed up loading:
            pls="none",
            # ad_block_on=True,
            # only works in SB:
            # sjw=True,
        )

    def sleep(self, sleep_case: SleepTime) -> None:
        match sleep_case:
            case SleepTime.STEP:
                sleep_duration = random.randint(8, 15)
                disconnect = False
            case SleepTime.BREAK:
                sleep_duration = random.randint(5 * 60, 15 * 60)
                disconnect = True
            case SleepTime.DUEL:
                sleep_duration = random.randint(6 * 60, 8 * 60)
                disconnect = True

        if sleep_duration >= 60:
            logger.info(f"Going to sleep for {sleep_duration/60:.1f} minutes")

        if disconnect:
            self._deep_sleep(sleep_duration)
        else:
            # this only disconnects WebDriver for sleep_duration seconds
            self.driver.reconnect(sleep_duration)

    def _deep_sleep(self, sleep_duration) -> None:
        """Close and open a browser after a timeout."""
        self.driver.quit()
        time.sleep(sleep_duration)
        self.create_driver()

    def quit_driver(self) -> None:
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed successfully.")
