import logging
import time
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.strategy import Strategies
import typer


def main(headless: bool = typer.Option(True, help="Run browser in headless mode.")):
    config = dotenv_values()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    web_page = (Path.cwd() / "pages/walking.mht").as_uri()
    web_page = "https://godville.net/"

    with SB(uc=True, headless=headless, user_data_dir="./chrome_profile") as sb:
        logging.info("Driver is launched")
        sb.open(web_page)
        logging.info("Page is loaded")
        link = sb.get_current_url()
        if "superhero" not in link:
            sb.type("#username", config["LOGIN"])
            sb.type("#password", config["PASSWORD"])
            sb.uc_click('input[value="Войти!"]')
            logging.info("Trying to log in")
        link = sb.get_current_url()
        if "superhero" not in link:
            logging.error("Login is unsuccessful")
        else:
            logging.info("Logged in")

        # there is also a hint distraction
        if sb.is_element_present("a.dm_close"):
            sb.uc_click("a.dm_close")
            logging.info("Close direct message")

        env = EnvironmentInfo(sb)
        hero_tracker = HeroTracker()
        hero_actions = HeroActions(sb, hero_tracker)
        strategies = Strategies(hero_actions, env)

        try:
            check_counter = 0
            while True:
                if check_counter % 6 == 0:
                    logging.info(env.all_info)
                    check_counter = 0

                time.sleep(10)
                # strategies.check_and_execute()
                check_counter += 1

        except KeyboardInterrupt:
            logging.info("Script terminated by user.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    typer.run(main)
