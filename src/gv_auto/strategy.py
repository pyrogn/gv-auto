import logging
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions
from gv_auto.states import HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE

BRICK_CITIES = ["Торгбург", "Снаряжуполь", "Някинск"]


class Strategies:
    def __init__(self, hero: HeroActions, env: EnvironmentInfo):
        self.hero = hero
        self.env = env

    def check_and_execute(self):
        self.melt_bricks()
        self.digging()

    def melt_bricks(self):
        try:
            if (self.env.prana > 25) and (
                self.env.state_enum not in [HeroStates.FISHING, HeroStates.ADVENTURE]
                and self.env.closest_town not in BRICK_CITIES
            ):
                if 1 == 1:
                    self.hero.influence(INFLUENCE_TYPE.PUNISH)
                logging.info("Melt bricks strategy executed.")
        except Exception as e:
            logging.error(f"Error in melt_bricks strategy: {e}")

    def digging(self):
        try:
            if (self.env.prana >= 5) and (
                self.env.state_enum in [HeroStates.WALKING, HeroStates.RETURNING]
            ):
                if 1 == 0:
                    self.hero.godvoice(VOICEGOD_TASK.DIG)
                logging.info("Digging strategy executed.")
        except Exception as e:
            logging.error(f"Error in digging strategy: {e}")

    def city_travel(self):
        try:
            if (
                (self.env.prana >= 5)
                and (self.env.state_enum == HeroStates.WALKING)
                and (self.env.money > (2000 - self.env.inventory * 5))
                and (self.env.closest_town in BRICK_CITIES)
                # and quest is not mini
            ):
                # добавить счетчик
                if 1 == 0:
                    self.hero.godvoice(VOICEGOD_TASK.RETURN)
                logging.info("Returning strategy executed.")
        except Exception as e:
            logging.error(f"Error in returning strategy: {e}")

    def zpg_arena(self):
        try:
            if (
                (self.env.prana >= 50)
                and (self.env.state_enum != HeroStates.FISHING)
                and (self.env.money < 3000)
            ):
                # добавить счетчик
                if 1 == 0:
                    self.hero.godvoice(VOICEGOD_TASK.RETURN)
                logging.info("Returning strategy executed.")
        except Exception as e:
            logging.error(f"Error in returning strategy: {e}")
