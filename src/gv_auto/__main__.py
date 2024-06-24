import logging
import time
import random
import traceback
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path  # noqa: F401
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker, StateManager
from gv_auto.logger import LogError, setup_logging
from gv_auto.game_info import HeroStates
from gv_auto.strategy import Strategies
import typer
from selenium.webdriver.common.keys import Keys  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)
LOG_PERIOD = 60

config = dotenv_values()


class BadURLException(Exception):
    """Bad URL."""


def validate_url_main_page(sb) -> None:
    url = sb.get_current_url()
    if "superhero" not in url:
        logger.error("Login is unsuccessful")
        LogError(sb).log_error()
        raise BadURLException


def login(sb) -> None:
    sb.uc_open("https://godville.net/")
    logger.info("Page is loaded")

    url = sb.get_current_url()
    if "superhero" not in url:
        sb.type("#username", config["LOGIN"])
        sb.type("#password", config["PASSWORD"])
        sb.uc_click('input[value="Войти!"]')
        logger.info("Trying to log in")

    validate_url_main_page(sb)

    logger.info("Logged in")


def routine(sb) -> None:
    if sb.is_link_text_visible("Воскресить"):
        sb.click_link("Воскресить")
        logger.info("Воскресили")
    if sb.is_element_present("a.dm_close"):
        sb.click("a.dm_close")
        logger.info("Closed direct message")
    if sb.is_element_visible("#hint_controls > span"):
        sb.click("#hint_controls > span")
        logger.info("Closed hint")

    validate_url_main_page(sb)
    # sb.save_screenshot(str(Path("now.png")))


def get_random_time_minutes(min, max) -> int:
    return random.randint(int(min * 60), int(max * 60))


def perform_tasks(sb, env: EnvironmentInfo, strategies: Strategies) -> int | None:
    run_duration = get_random_time_minutes(20, 80)
    logger.info(f"Tasks will be performed for {run_duration // 60} minutes.")

    start_time = time.time()
    next_log_time = start_time + LOG_PERIOD

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time >= run_duration:
            return None

        if current_time >= next_log_time:
            logger.info(env.all_info)
            next_log_time += LOG_PERIOD

        routine(sb)

        strategies.check_and_execute()

        match env.state_enum:
            case (HeroStates.ADVENTURE, HeroStates.HEALING, HeroStates.PRAYING):
                sb.reconnect(random.randint(20, 50))
            case HeroStates.DUEL:
                return get_random_time_minutes(5, 8)
            case HeroStates.LEISURE:
                return get_random_time_minutes(10, 20)
            case HeroStates.FISHING:
                return get_random_time_minutes(8, 15)
            case HeroStates.UNKNOWN:
                logger.error("Got an unknown state, where am I?")
                LogError(sb).log_error()
            case _:
                sb.reconnect(random.randint(5, 12))


def main(
    headless: bool = typer.Option(True, help="Run browser in headless mode."),
    manual: bool = typer.Option(False, help="Run in simple mode just to open a URL."),
    sleep: bool = typer.Option(
        True, help="Should script disconnect and sleep for some time."
    ),
):
    headless = False if manual else headless

    while True:
        with SB(
            uc=True,
            headless2=headless,
            user_data_dir="./chrome_profile",
            # these options speed up loading
            sjw=True,
            pls="none",
            ad_block_on=True,
        ) as sb:
            try:
                logger.info("Driver is launched")

                login(sb)

                env = EnvironmentInfo(sb)
                state_manager = StateManager()
                hero_tracker = HeroTracker(env, state_manager)
                hero_actions = HeroActions(sb, hero_tracker, env)
                strategies = Strategies(hero_actions, env, hero_tracker)

                if manual:
                    sb.reconnect(2)
                    # breakpoint()

                    sb.disconnect()
                    time.sleep(10000000)
                    return

                timeout = perform_tasks(sb, env, strategies) or get_random_time_minutes(
                    5, 15
                )
                if not sleep:  # to prevent constant reconnect during some states
                    logger.info(
                        f"Because sleep is off, we pause for {timeout/60:.1f} minutes"
                    )
                    sb.reconnect(timeout)

            except Exception as e:
                logger.error(f"Exception occurred: {e}")
                logger.error(traceback.format_exc())
                LogError(sb).log_error()
                break
                # then analyze, fix error and start again.
                # Better to analyze problem, then trying to be stuck in loop with error.

        if sleep:
            if timeout >= 60:
                logger.info(f"Sleeping for {timeout/60:.1f} minutes")
            time.sleep(timeout)


if __name__ == "__main__":
    typer.run(main)
