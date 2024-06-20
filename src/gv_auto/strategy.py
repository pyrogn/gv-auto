import logging
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions
from gv_auto.logger import setup_logging
from gv_auto.states import HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE

setup_logging()
logger = logging.getLogger(__name__)

BRICK_CITIES = ["Торгбург", "Снаряжуполь", "Някинск"]


class Strategies:
    def __init__(self, hero: HeroActions, env: EnvironmentInfo):
        self.hero = hero
        self.env = env

    def check_and_execute(self):
        # basic strategies:
        self.melt_bricks()
        self.bingo()
        # self.zpg_arena()

        # advanced strategies:
        # self.digging()
        # self.cancel_leaving_guild()
        # self.city_travel

    def melt_bricks(self):
        try:
            if (self.env.prana > 25) and (
                self.env.state_enum not in [HeroStates.FISHING, HeroStates.ADVENTURE]
                and self.env.closest_town not in BRICK_CITIES
                and self.env.money > 3100
            ):
                self.hero.influence(INFLUENCE_TYPE.PUNISH)
                logger.info("Melt bricks strategy executed.")
        except Exception as e:
            logger.error(f"Error in melt_bricks strategy: {e}")

    def bingo(self):
        # think about giving away expensive items
        try:
            if self.env.inventory >= 50:
                self.hero.play_bingo()
                logger.info("Bingo strategy executed.")
        except Exception as e:
            logger.error(f"Error in bingo strategy: {e}")

    def digging(self):
        try:
            if (self.env.prana >= 5) and (
                self.env.state_enum in [HeroStates.WALKING, HeroStates.RETURNING]
            ):
                self.hero.godvoice(VOICEGOD_TASK.DIG)
                logger.info("Digging strategy executed.")
        except Exception as e:
            logger.error(f"Error in digging strategy: {e}")

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
                self.hero.godvoice(VOICEGOD_TASK.RETURN)
                logger.info("Returning strategy executed.")
        except Exception as e:
            logger.error(f"Error in returning strategy: {e}")

    def zpg_arena(self):
        try:
            if (
                (self.env.prana >= 50)
                and (self.env.state_enum != HeroStates.FISHING)
                and (self.env.money < 3000)
                # and zpg is available (to add)
            ):
                # добавить счетчик и таймер
                if 1 == 0:
                    self.hero.godvoice(VOICEGOD_TASK.RETURN)
                logger.info("Returning strategy executed.")
        except Exception as e:
            logger.error(f"Error in returning strategy: {e}")

    def cancel_leaving_guild(self):
        try:
            _, quest = self.env.quest
            if (
                ("Стать" in quest)  # verify this, replace with re
                and ("членом" in quest)
                and ("Ряды Фурье" not in quest)
                and (self.env.prana >= 5)
                and (self.env.state_enum not in [HeroStates.DUEL])
            ):
                self.hero.godvoice(VOICEGOD_TASK.CANCEL)
                logger.info("Cancel task strategy executed.")
        except Exception as e:
            logger.error(f"Error in cancel task strategy: {e}")

    def open_activatables(self):
        "If there are certain activatable items, we should open them."

    def craft_items(self):
        """Crafting items to get certain activatables."""
