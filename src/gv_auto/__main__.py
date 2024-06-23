import logging
import time
import random
from dotenv import dotenv_values
from pathlib import Path  # noqa: F401
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.logger import setup_logging
from gv_auto.states import HeroStates
from gv_auto.strategy import Strategies
import typer

from gv_auto.driver import DriverManager, SleepTime  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)

config = dotenv_values()


def login(driver):
    driver.uc_open("https://godville.net/")
    logger.info("Page is loaded")

    url = driver.current_url
    if "superhero" not in url:
        driver.type("#username", config["LOGIN"])
        driver.type("#password", config["PASSWORD"])
        driver.uc_click('input[value="Войти!"]')
        logger.info("Trying to log in")
    url = driver.current_url
    if "superhero" not in url:
        logger.error("Login is unsuccessful")
        return False
    logger.info("Logged in")

    return True


def routine(sb) -> bool:
    if sb.is_link_text_visible("Воскресить"):
        sb.click_link("Воскресить")
        logger.info("Воскресили")
    if sb.is_element_present("a.dm_close"):
        sb.uc_click("a.dm_close")
        logger.info("Closed direct message")
    if sb.is_link_text_visible("Прекрасно"):
        sb.click_link("Прекрасно")
        logger.info("Closed hint")

    url = sb.get_current_url()
    if "superhero" not in url:
        logger.error("Are we banned? Check screenshot or use manual mode.")
        return False
    return True
    # sb.save_screenshot(str(Path("now.png")))


def perform_tasks(
    driver_manager: DriverManager, env: EnvironmentInfo, strategies: Strategies
) -> bool:
    n_actions = random.randint(50, 250)
    logger.info(f"{n_actions} actions will be performed.")
    check_counter = 0
    while check_counter < n_actions:
        if check_counter % 6 == 0:
            logger.info(env.all_info)

        if not routine(driver_manager.driver):
            return False

        if env.state_enum is HeroStates.DUEL:
            driver_manager.sleep(SleepTime.DUEL)
        elif env.state_enum is HeroStates.UNKNOWN:
            logger.error("Got an unknown state, where am I?")
        else:
            strategies.check_and_execute()
            driver_manager.sleep(SleepTime.STEP)
        check_counter += 1
    return True


def main(
    headless: bool = typer.Option(True, help="Run browser in headless mode."),
    manual: bool = typer.Option(False, help="Run in simple mode just to open a URL."),
    sleep: bool = typer.Option(
        True, help="Should script disconnect and sleep for some time."
    ),
):
    headless = False if manual else headless

    while True:
        try:
            driver_manager = DriverManager(headless)
            logger.info("Driver is launched")

            if not login(driver_manager.driver):
                return

            env = EnvironmentInfo(driver_manager)
            hero_tracker = HeroTracker(env)
            hero_actions = HeroActions(driver_manager, hero_tracker, env)
            strategies = Strategies(hero_actions, env, hero_tracker)

            if manual:
                driver = driver_manager.driver
                driver.reconnect(2)
                # breakpoint()
                # hero_actions._make_influence(INFLUENCE_TYPE.PUNISH)
                # print("influence")
                # sb.click("#cntrl2 > div.arena_link_wrap > a")
                # if sb.is_link_text_visible("Отправить на арену"):
                #     print("going to click")
                #     selector = "#cntrl2 > div.arena_link_wrap > a"
                #     sb.find_element(selector, timeout=1).click()
                #     print("clicked")
                #     sb.sleep(1)
                #     print("clept")
                #     # alert = sb.switch_to_alert(2)
                #     # print(alert.text)
                #     print(sb.dismiss_alert())
                #     print("alert dismissed")

                driver.disconnect()
                time.sleep(10000000)
                return

            if not perform_tasks(driver_manager, env, strategies):
                return

            if sleep:
                driver_manager.sleep(SleepTime.BREAK)
        finally:
            driver_manager.quit_driver()


if __name__ == "__main__":
    typer.run(main)
