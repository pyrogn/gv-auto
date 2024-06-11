import random
import logging
from gv_auto.states import INFLUENCE_TYPE, VOICEGOD_TASK, voicegods_map


class HeroActions:
    def __init__(self, driver, hero_tracker) -> None:
        self.driver = driver
        self.hero_tracker = hero_tracker

    def influence(self, infl_type: INFLUENCE_TYPE):
        try:
            if infl_type == INFLUENCE_TYPE.ENCOURAGE:
                self.driver.click_link("Сделать хорошо")
            elif infl_type == INFLUENCE_TYPE.PUNISH:
                self.driver.click_link("Сделать плохо")
            logging.info(f"Influence action '{infl_type}' executed successfully.")
        except Exception as e:
            logging.error(f"Error in influence method: {e}")

    def godvoice(self, task: VOICEGOD_TASK):
        try:
            text = random.choice(voicegods_map[task])
            self.driver.type("#godvoice", text)
            self.driver.uc_click("#voice_submit")
            logging.info(f"Godvoice command '{text}' executed successfully.")
        except Exception as e:
            logging.error(f"Error in godvoice method: {e}")


class HeroTracker:
    def __init__(self):
        self.return_counter = 0
