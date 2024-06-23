from enum import Enum, auto
import logging
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
            # these options speed up loading
            # sjw=True,
            pls="none",
            # ad_block_on=True,
        )

    def sleep(self, sleep_case: SleepTime) -> None:
        match sleep_case:
            case SleepTime.STEP:
                sleep_duration = 3
                disconnect = False
            case SleepTime.BREAK:
                sleep_duration = 5
                disconnect = True
            case SleepTime.DUEL:
                sleep_duration = 10
                disconnect = True

        if sleep_duration >= 60:
            logger.info(f"Going to sleep for {sleep_duration/60:.1f} minutes")

        if disconnect:
            self._deep_sleep(sleep_duration)
        else:
            # this only disconnects WebDriver for sleep_duration seconds
            print("going to sleep", sleep_duration)
            self.driver.reconnect(sleep_duration)

    def _deep_sleep(self, sleep_duration) -> None:
        self.driver.quit()
        time.sleep(sleep_duration)
        self.create_driver()


print("going to create driver")
c = DriverManager(False)
c.driver.uc_open("google.com")
# print(c.driver.get_current_url())
print(dir(c.driver))
print(c.driver.current_url)
c.driver.quit()
# print("easy sleep")
# c.sleep(SleepTime.STEP)
# print("deep sleep1")
# c.sleep(SleepTime.BREAK)
# print("deep sleep2")
# c.sleep(SleepTime.DUEL)
# print("wait for closing")
# c.driver.sleep(5)
# c.driver.quit()
