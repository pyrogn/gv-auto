from enum import Enum, auto
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


class HeroStates(Enum):
    SLEEPING = auto()
    WALKING = auto()
    RETURNING = auto()
    FISHING = auto()
    HEALING = auto()
    FIGHTING = auto()
    TRADING = auto()
    LEISURE = auto()
    ADVENTURE = auto()
    PRAYING = auto()


activity_map = {
    HeroStates.SLEEPING: ["Сон"],
    HeroStates.WALKING: ["Дорога"],
    HeroStates.RETURNING: ["Возврат"],
    HeroStates.HEALING: ["Лечение"],
    HeroStates.FIGHTING: ["Бой"],
    HeroStates.TRADING: ["Торговля"],
    HeroStates.FISHING: ["Рыбалка"],
    HeroStates.LEISURE: ["Отдых"],
    HeroStates.ADVENTURE: ["Авантюра"],
    HeroStates.PRAYING: ["Молитва"],
}
str_state2enum_state = {}
for k, v in activity_map.items():
    for say in v:
        str_state2enum_state[say] = k


class VOICEGOD_TASK(Enum):
    FIGHT = auto()
    HEAL = auto()
    RETURN = auto()
    DIG = auto()
    CANCEL = auto()


class INFLUENCE_TYPE(Enum):
    ENCOURAGE = auto()
    PUNISH = auto()


voicegods_map = {
    VOICEGOD_TASK.FIGHT: ["Бей"],
    VOICEGOD_TASK.HEAL: ["Лечись"],
    VOICEGOD_TASK.RETURN: ["Домой"],
    VOICEGOD_TASK.DIG: ["Копай клад"],
    VOICEGOD_TASK.CANCEL: ["Отмени задание"],
}


class HeroTracker:
    def __init__(self):
        self.return_counter = 0


class HeroActions:
    def __init__(self, driver, hero_state: HeroTracker) -> None:
        self.driver = driver
        self.hs = hero_state

    def influence(self, infl_type: INFLUENCE_TYPE):
        try:
            if infl_type == INFLUENCE_TYPE.ENCOURAGE:
                self.driver.click_link("Сделать хорошо")
            elif infl_type == INFLUENCE_TYPE.PUNISH:
                self.driver.click_link("Сделать плохо")
            logging.info(f"Influence action '{infl_type}' executed successfully.")
        except Exception as e:
            logging.error(f"Error in influence method: {e}")

    def godvoice(self, say: VOICEGOD_TASK):
        try:
            text = random.choice(voicegods_map[say])
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
    def state_enum(self):
        return str_state2enum_state[self.state]

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
                area = re.search(r"(.+?)\s*\(", area).group(0)
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

    def __init__(self, driver):
        self.driver = driver

    @property
    def is_responded(self):
        latest_entry_text = sb.get_text("div.d_msg")
        if "➥" in latest_entry_text:
            return True
        return False


class Strategies:
    def __init__(self, hero: HeroActions, env: EnvironmentInfo):
        self.hero = hero
        self.env = env

    def melt_bricks(self):
        try:
            if (
                (self.hero.prana > 25)
                and (
                    self.env.state_enum
                    not in [HeroStates.FISHING, HeroStates.ADVENTURE]
                )
                and (self.hero.money >= 3000)
            ):
                self.hero.influence(INFLUENCE_TYPE.PUNISH)
                logging.info("Melt bricks strategy executed.")
        except Exception as e:
            logging.error(f"Error in melt_bricks strategy: {e}")

    def digging(self):
        try:
            if (self.hero.prana > 5) and (
                self.env.state in [HeroStates.WALKING, HeroStates.RETURNING]
            ):
                self.hero.godvoice(VOICEGOD_TASK.DIG)
                logging.info("Digging strategy executed.")
        except Exception as e:
            logging.error(f"Error in digging strategy: {e}")

    def open_activatables(self):
        # learn to parse them
        pass

    def return_host(self):
        pass
        # also count times during quest


if __name__ == "__main__":
    with SB(uc=True, headless=True, user_data_dir="./chrome_profile") as sb:
        logging.info("Driver is launched")
        sb.open(web_page)
        logging.info("Page is loaded")
        env = EnvironmentInfo(sb)

        hs = HeroTracker()
        hero_actions = HeroActions(sb, hs)

        try:
            while True:
                logging.info(env.all_info)
                sb.sleep(60 + random.randint(-20, 20))
        except KeyboardInterrupt:
            logging.info("Script terminated by user.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
