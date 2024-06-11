import logging
from gv_auto.states import HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE


class Strategies:
    def __init__(self, hero, env):
        self.hero = hero
        self.env = env

    def check_and_execute(self):
        self.melt_bricks()
        self.digging()

    def melt_bricks(self):
        try:
            if (self.env.prana > 25) and (
                self.env.state_enum not in [HeroStates.FISHING, HeroStates.ADVENTURE]
            ):
                if 1 == 0:
                    self.hero.influence(INFLUENCE_TYPE.PUNISH)
                logging.info("Melt bricks strategy executed.")
        except Exception as e:
            logging.error(f"Error in melt_bricks strategy: {e}")

    def digging(self):
        try:
            if (self.env.prana > 5) and (
                self.env.state_enum in [HeroStates.WALKING, HeroStates.RETURNING]
            ):
                if 1 == 0:
                    self.hero.godvoice(VOICEGOD_TASK.DIG)
                logging.info("Digging strategy executed.")
        except Exception as e:
            logging.error(f"Error in digging strategy: {e}")
