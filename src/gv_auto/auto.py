import re
import random
import logging
from seleniumbase import SB
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

web_page = (Path.cwd() / "pages/in_town.mht").as_uri()
web_page = "https://godville.net/"


class HeroActions:
    def __init__(self, driver) -> None:
        self.driver = driver

    def influence(self, infl_type):
        try:
            if infl_type == "good":
                self.driver.click_link("Сделать хорошо")
                # alternative
                # self.driver.click("#cntrl1 > a.no_link.div_link.enc_link")
            elif infl_type == "bad":
                self.driver.click_link("Сделать плохо")
                # self.driver.click("#cntrl1 > a.no_link.div_link.pun_link")
            logging.info(f"Influence action '{infl_type}' executed successfully.")
        except Exception as e:
            logging.error(f"Error in influence method: {e}")

    def godvoice(self, text):
        try:
            self.driver.type("#godvoice", text)
            self.driver.uc_click("#voice_submit")
            logging.info(f"Godvoice command '{text}' executed successfully.")
        except Exception as e:
            logging.error(f"Error in godvoice method: {e}")


class EnvironmentInfo:
    def __init__(self, driver):
        self.driver = driver

    @property
    def state(self):
        try:
            state = self.driver.get_text("#news > div.block_h > h2")
            short_state = state.split(" ")[0]
            return short_state
        except Exception as e:
            logging.error(f"Error retrieving state: {e}")
            return "Unknown"

    @property
    def money(self):
        try:
            money_str = self.driver.get_text("#hk_gold_we > div.l_val")
            money = int(re.search(r"\d+", money_str).group())
            return money
        except Exception as e:
            logging.error(f"Error retrieving money: {e}")
            return 0

    @property
    def prana(self):
        try:
            prana = int(
                self.driver.get_text("#cntrl > div.pbar.line > div.gp_val")[:-1]
            )
            return prana
        except Exception as e:
            logging.error(f"Error retrieving prana: {e}")
            return 0

    @property
    def bricks(self):
        try:
            bricks = int(
                float(self.driver.get_text("#hk_bricks_cnt > div.l_val")[:-1]) * 10
            )
            return bricks
        except Exception as e:
            logging.error(f"Error retrieving bricks: {e}")
            return 0

    @property
    def health(self):
        try:
            health_str = self.driver.get_text("#hk_health > div.l_val")
            cur_health, all_health = map(int, re.findall(r"\d+", health_str))
            return int(cur_health / all_health * 100)
        except Exception as e:
            logging.error(f"Error retrieving health: {e}")
            return 0

    @property
    def position(self):
        try:
            where = self.driver.get_text("#hk_distance > div.l_capt")
            is_in_town = True if where == "Город" else False
            miles = self.driver.get_text("#hk_distance > div.l_val")
            if not is_in_town:
                miles = int(re.search(r"\d+", miles).group())
                area = "В пути"
            else:
                area = self.driver.get_attribute("g.tl.sl title", "textContent")
                miles = int(re.search(r"\d+", area).group())
                area = area.split(" ")[0]
            return miles, area
        except Exception as e:
            logging.error(f"Error retrieving position: {e}")
            return 0, "Unknown"

    @property
    def inventory(self):
        try:
            inv_str = self.driver.get_text("#hk_inventory_num > div.l_val")
            cur_inv, all_inv = map(int, re.findall(r"\d+", inv_str))
            return int(cur_inv / all_inv * 100)
        except Exception as e:
            logging.error(f"Error retrieving inventory: {e}")
            return 0

    @property
    def all_info(self):
        try:
            return f"{self.state}|money:{self.money}|prana:{self.prana}|inv:{self.inventory}|bricks:{self.bricks}|hp:{self.health}|where:{','.join(map(str, self.position))}"
        except Exception as e:
            logging.error(f"Error retrieving all information: {e}")
            return "Error retrieving all information"


class HeroResponses:
    "Track, wait and listen to reponses"


class Strategies:
    def __init__(self, hero: HeroActions, env: EnvironmentInfo):
        self.hero = hero
        self.env = env

    def melt_bricks(self):
        try:
            if (self.hero.prana > 25) and (self.env.state != "Рыбалка"):
                self.hero.influence("bad")
                logging.info("Melt bricks strategy executed.")
        except Exception as e:
            logging.error(f"Error in melt_bricks strategy: {e}")

    def digging(self):
        try:
            if (self.hero.prana > 5) and (self.env.state in ["Дорога", "Возврат"]):
                self.hero.godvoice("Копай клад!")
                logging.info("Digging strategy executed.")
        except Exception as e:
            logging.error(f"Error in digging strategy: {e}")

    def open_activatables(self):
        pass


if __name__ == "__main__":
    with SB(uc=True, headless=True, user_data_dir="./chrome_profile") as sb:
        logging.info("Driver is launched")
        sb.open(web_page)
        logging.info("Page is loaded")
        env = EnvironmentInfo(sb)

        try:
            while True:
                logging.info(env.all_info)
                sb.sleep(60 + random.randint(-20, 20))
        except KeyboardInterrupt:
            logging.info("Script terminated by user.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
