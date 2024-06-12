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
        self._return_counter = 0

    @property
    def return_counter(self):
        return self._return_counter

    @return_counter.setter
    def _(self, val):
        self._return_counter = val

    def register_quest(self):
        pass
        # if quest is new, then we reset return_counter to 0
