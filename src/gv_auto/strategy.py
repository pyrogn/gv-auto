import logging
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.logger import setup_logging
from gv_auto.states import HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE

setup_logging()
logger = logging.getLogger(__name__)

BRICK_CITIES = ["Торгбург", "Снаряжуполь", "Някинск"]
MY_GUILD = "Ряды Фурье"


class Strategies:
    def __init__(
        self, hero_actions: HeroActions, env: EnvironmentInfo, hero_tracker: HeroTracker
    ):
        self.hero_actions = hero_actions
        self.env = env
        self.hero_tracker = hero_tracker

    def check_and_execute(self):
        basic_strategies = [self.melt_bricks, self.bingo]
        for strategy in basic_strategies:
            try:
                strategy()
            except Exception as e:
                logger.error(f"Error in {strategy.__name__} strategy: {e}")

        advanced_strategies = [  # noqa: F841
            self.zpg_arena,
            self.digging,
            self.cancel_leaving_guild,
            self.city_travel,
            self.open_activatables,
            self.craft_items,
        ]

    def melt_bricks(self):
        if (self.env.prana > 25) and (
            self.env.state_enum
            not in [HeroStates.FISHING, HeroStates.ADVENTURE, HeroStates.DUEL]
            and self.env.closest_town not in BRICK_CITIES
            and self.env.money > 3000
            and self.hero_tracker.is_melting_available
        ):
            self.hero_actions.influence(INFLUENCE_TYPE.PUNISH)
            logger.info("Melt bricks strategy executed.")

    def bingo(self):
        if self.hero_tracker.is_bingo_available:
            if self.env.inventory_perc >= 40:
                self.hero_actions.play_bingo()
                logger.info("Bingo strategy executed.")
            elif self.hero_tracker.bingo_last_call:
                self.hero_actions.play_bingo(finish=True)
                logger.info("Bingo last call strategy executed.")

    def digging(self):
        if (self.env.prana >= 5) and (
            self.env.state_enum in [HeroStates.WALKING, HeroStates.RETURNING]
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.DIG)
            logger.info("Digging strategy executed.")

    def city_travel(self):
        if (
            (self.env.prana >= 5)
            and (self.env.state_enum == HeroStates.WALKING)
            # different cities have different prices (look up)
            and (self.env.money > (2000 - self.env.inventory * 5))
            and (self.env.closest_town in BRICK_CITIES)
            # add condition with counters
        ):
            # добавить счетчик
            self.hero_actions.godvoice(VOICEGOD_TASK.RETURN)
            logger.info("Returning strategy executed.")

    def zpg_arena(self):
        if (
            (self.env.prana >= 50)
            and (self.env.state_enum != HeroStates.FISHING)
            and (self.env.money < 3000)
            # and zpg is available (parse it)
        ):
            self.hero_actions.go_to_zpg_arena()
            logger.info("ZPG arena strategy executed.")

    def cancel_leaving_guild(self):
        _, quest = self.env.quest
        if (
            ("Стать" in quest)  # verify this, replace with re
            and ("членом" in quest)
            and (MY_GUILD not in quest)
            and ("(отменено)" not in quest)
            and (self.env.prana >= 5)
            and (self.env.state_enum not in [HeroStates.DUEL])
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.CANCEL)
            logger.info("Cancel task strategy executed.")

    def open_activatables(self):
        "If there are certain activatable items, we should open them."

    def craft_items(self):
        """Crafting items to get certain activatables."""
