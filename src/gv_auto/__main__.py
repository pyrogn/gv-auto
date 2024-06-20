import logging
import time
import random
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path
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

    # should not be here
    if sb.is_element_present("a.dm_close"):
        sb.uc_click("a.dm_close")
        logger.info("Closed direct message")
    if sb.is_link_text_visible("Прекрасно"):
        sb.click_link("Прекрасно")
        logger.info("Closed hint")
    # might also close hints

    return True


def perform_tasks(sb, env, hero_tracker, hero_actions, strategies):
    n_actions = random.randint(50, 150)
    logger.info(f"{n_actions} actions will be performed.")
    check_counter = 0
    while check_counter < n_actions:
        if check_counter % 6 == 0:
            logger.info(env.all_info)

        if sb.is_link_text_visible("Воскресить"):
            sb.click_link("Воскресить")
            logger.info("Воскресили")

        sb.reconnect(10)
        # right now I don't enable strategies
        # strategies.check_and_execute()
        check_counter += 1
        sb.save_screenshot(str(Path("now.png")))

        url = sb.get_current_url()
        if "superhero" not in url:
            logger.error("Are we banned? Check screenshot or use manual mode.")
            return False
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
        ) as sb:
            logger.info("Driver is launched")

            if not login(sb):
                return

            # choose action
            # bingo + coupon
            # normal strategies

            env = EnvironmentInfo(sb)
            hero_tracker = HeroTracker()
            hero_actions = HeroActions(sb, hero_tracker)
            strategies = Strategies(hero_actions, env)

            if manual:
                sb.reconnect(2)

                logger.info("Живой")
                # sb.uc_click("#inv_block_content > ul > li:nth-child(4) > div > a")

                # sb.uc_open("https://godville.net/news")
                # # sb.uc_click("#bgn_show")
                # # print("click 1")
                # # if sb.is_element_clickable("#bgn_use"):
                # #     print("clickable")
                # #     sb.uc_click("#bgn_use")
                # #     print("click 2")
                # #     text = sb.get_text("#b_inv")  # to find number of matches
                # #     print(text)
                # # print("not clickable")

                # if sb.is_element_clickable("#ad_b"):
                #     sb.scroll_to("#ad_b")
                #     sb.click("#ad_b")
                #     print("clicked")
                #     sb.sleep(1)
                #     print("slept")
                #     # alert = sb.switch_to_alert()
                #     # print(alert.text)
                #     print(sb.accept_alert())

                # sb.uc_click('//*[@id="cntrl1"]/a[contains(text(),"Сделать хорошо")]')
                # sb.click_link("Сделать хорошо")
                # sb.click("#cntrl1 > a.no_link.div_link.enc_link")
                # print(sb.is_element_clickable("#cntrl1 > a.no_link.div_link.enc_link"))
                # sb.uc_click('//*[@id="cntrl1"]/a[contains(text(),"Сделать хорошо")]')

                selector = "#cntrl1 > a.no_link.div_link.enc_link"
                # sb.focus(selector)
                # sb.send_keys(selector, Keys.RETURN)
                # logger.info("clicked on enc link")
                # sb.hover_and_click(selector, selector)
                # sb.reconnect(5)
                # logger.info("reconnected")
                sb.disconnect()
                time.sleep(10000000)
                return

            if not perform_tasks(sb, env, hero_tracker, hero_actions, strategies):
                return

        if sleep:
            random_sleep_time = random.randint(300, 900)
            logger.info(f"Sleeping for {random_sleep_time} seconds")
            time.sleep(random_sleep_time)


if __name__ == "__main__":
    typer.run(main)
