import logging
import time
import random
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.strategy import Strategies
import typer
from selenium.webdriver.common.keys import Keys  # noqa: F401


def login(sb, config):
    sb.uc_open("https://godville.net/")
    logging.info("Page is loaded")

    url = sb.get_current_url()
    if "superhero" not in url:
        sb.type("#username", config["LOGIN"])
        sb.type("#password", config["PASSWORD"])
        sb.uc_click('input[value="Войти!"]')
        logging.info("Trying to log in")
    url = sb.get_current_url()
    if "superhero" not in url:
        logging.error("Login is unsuccessful")
        return False
    logging.info("Logged in")

    if sb.is_element_present("a.dm_close"):
        sb.uc_click("a.dm_close")
        logging.info("Closed direct message")
    # might also close hints

    return True


def perform_tasks(sb, env, hero_tracker, hero_actions, strategies):
    n_actions = random.randint(50, 150)
    logging.info(f"{n_actions} actions will be performed.")
    check_counter = 0
    while check_counter < n_actions:
        if check_counter % 6 == 0:
            logging.info(env.all_info)

        time.sleep(10)
        strategies.check_and_execute()
        check_counter += 1
        sb.save_screenshot(str(Path("now.png")))

        url = sb.get_current_url()
        if "superhero" not in url:
            logging.error("Are we banned? Check screenshot or use manual mode.")
            return False
    return True


def main(
    headless: bool = typer.Option(True, help="Run browser in headless mode."),
    manual: bool = typer.Option(False, help="Run in simple mode just to open a URL."),
    sleep: bool = typer.Option(
        True, help="Should script disconnect and sleep for some time."
    ),
):
    config = dotenv_values()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    headless = False if manual else headless

    while True:
        with SB(uc=True, headless2=headless, user_data_dir="./chrome_profile") as sb:
            logging.info("Driver is launched")

            if not login(sb, config):
                return

            env = EnvironmentInfo(sb)
            hero_tracker = HeroTracker()
            hero_actions = HeroActions(sb, hero_tracker)
            strategies = Strategies(hero_actions, env)

            if manual:
                sb.sleep(2)

                # sb.uc_click('//*[@id="cntrl1"]/a[contains(text(),"Сделать хорошо")]')
                # sb.click_link("Сделать хорошо")
                # sb.click("#cntrl1 > a.no_link.div_link.enc_link")
                # print(sb.is_element_clickable("#cntrl1 > a.no_link.div_link.enc_link"))
                # sb.uc_click('//*[@id="cntrl1"]/a[contains(text(),"Сделать хорошо")]')

                # selector = "#cntrl1 > a.no_link.div_link.enc_link"
                # sb.focus(selector)
                # sb.send_keys(selector, Keys.RETURN)
                # logging.info("clicked on enc link")
                # sb.reconnect(5)
                # logging.info("reconnected")
                sb.sleep(10000000)
                return

            if not perform_tasks(sb, env, hero_tracker, hero_actions, strategies):
                return

        if sleep:
            random_sleep_time = random.randint(300, 900)
            logging.info(f"Sleeping for {random_sleep_time} seconds")
            time.sleep(random_sleep_time)


if __name__ == "__main__":
    typer.run(main)
