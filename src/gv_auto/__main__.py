import logging
import time
import random
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path  # noqa: F401
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.logger import setup_logging
from gv_auto.strategy import Strategies
import typer
from selenium.webdriver.common.keys import Keys  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)

config = dotenv_values()


def login(sb):
    sb.uc_open("https://godville.net/")
    logger.info("Page is loaded")

    url = sb.get_current_url()
    if "superhero" not in url:
        sb.type("#username", config["LOGIN"])
        sb.type("#password", config["PASSWORD"])
        sb.uc_click('input[value="Войти!"]')
        logger.info("Trying to log in")
    url = sb.get_current_url()
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


def perform_tasks(sb, env, strategies) -> bool:
    n_actions = random.randint(50, 250)
    logger.info(f"{n_actions} actions will be performed.")
    check_counter = 0
    while check_counter < n_actions:
        if check_counter % 6 == 0:
            logger.info(env.all_info)

        if not routine(sb):
            return False
        strategies.check_and_execute()
        sb.reconnect(random.randint(8, 15))
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
        with SB(
            uc=True,
            headless2=headless,
            user_data_dir="./chrome_profile",
            # these options might speed up loading
            sjw=True,
            pls="none",
            ad_block_on=True,
        ) as sb:
            logger.info("Driver is launched")

            if not login(sb):
                return

            env = EnvironmentInfo(sb)
            hero_tracker = HeroTracker()
            hero_actions = HeroActions(sb, hero_tracker)
            strategies = Strategies(hero_actions, env, hero_tracker)

            if manual:
                sb.reconnect(2)
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

                sb.disconnect()
                time.sleep(10000000)
                return

            if not perform_tasks(sb, env, strategies):
                return

        if sleep:
            random_sleep_time = random.randint(300, 900)
            logger.info(f"Sleeping for {random_sleep_time} seconds")
            time.sleep(random_sleep_time)


if __name__ == "__main__":
    typer.run(main)
