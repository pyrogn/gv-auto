import logging
import time
from seleniumbase import SB
from pathlib import Path
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions
from gv_auto.strategy import Strategies
from gv_auto.hero import HeroTracker


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

web_page = (Path.cwd() / "pages/in_town.mht").as_uri()
web_page = "https://godville.net/"

if __name__ == "__main__":
    with SB(uc=True, headless=True, user_data_dir="./chrome_profile") as sb:
        logging.info("Driver is launched")
        sb.open(web_page)
        logging.info("Page is loaded")

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
                strategies.check_and_execute()
                check_counter += 1

        except KeyboardInterrupt:
            logging.info("Script terminated by user.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
