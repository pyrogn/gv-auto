import logging
import re
import time  # noqa: F401
from gv_auto.environment import EnvironmentInfo, TimeManager
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.logger import LogError, setup_logging
from gv_auto.game_info import FeatureLock, HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE

setup_logging()
logger = logging.getLogger(__name__)

BRICK_TOWNS = {
    "Торгбург": 2400,  # 2000-2700
    "Снаряжуполь": 1500,  # 1000-1700
    "Някинск": 1500,  # 1000-1700
}
MY_GUILD = "Ряды Фурье"
MAX_GOLD_ZPG_ARENA = 2300
MIN_PERC_INV_BINGO = 40
MIN_PRANA_DIGGING = 55
MIN_PRANA_CITY_TRAVEL = 30


class Strategies:
    def __init__(
        self, hero_actions: HeroActions, env: EnvironmentInfo, hero_tracker: HeroTracker
    ):
        self.hero_actions = hero_actions
        self.env = env
        self.hero_tracker = hero_tracker
        self.feature_lock = FeatureLock(self.env.level)

    def check_and_execute(self) -> None:
        """Strategies to add to a list and execute."""
        strategies = [
            self.melt_bricks,
            self.bingo,
            self.city_travel,
            self.digging,
            self.open_activatables,
        ]

        if self.feature_lock.is_guild_available:
            strategies.append(self.cancel_leaving_guild)  # test it
        if self.feature_lock.is_zpg_arena_available:
            strategies.append(self.zpg_arena)

        if self.env.state_enum is not HeroStates.DUEL:
            for strategy in strategies:
                try:
                    strategy()
                except Exception:
                    logger.exception(f"Error in {strategy.__name__} strategy")
                    LogError(self.env.driver).log_error()

        to_be_included = [  # noqa: F841
            self.craft_items,  # test it
        ]

    def melt_bricks(self):
        if (
            (self.env.prana >= 25)
            and self.env.state_enum
            not in [
                HeroStates.FISHING,
                HeroStates.ADVENTURE,
                HeroStates.DUEL,
                HeroStates.UNKNOWN,
            ]
            and self.env.closest_town not in BRICK_TOWNS
            and self.env.money > 3000
            and self.hero_tracker.is_melting_available
        ):
            self.hero_actions.influence(INFLUENCE_TYPE.PUNISH)
            logger.info("Melt bricks strategy executed.")

    def bingo(self):
        if (
            self.env.state_enum not in [HeroStates.DUEL]
            and self.hero_tracker.is_bingo_available
        ):
            if TimeManager.bingo_last_call():
                self.hero_actions.play_bingo(finish=True)
                logger.info("Bingo last call strategy executed.")
            elif self.env.inventory_perc >= MIN_PERC_INV_BINGO:
                self.hero_actions.play_bingo()
                logger.info("Bingo strategy executed.")

    def digging(self):
        if (
            self.env.state_enum in [HeroStates.WALKING, HeroStates.RETURNING]
            and self.hero_tracker.is_godvoice_available
            and (self.env.prana >= MIN_PRANA_DIGGING)
            and (self.env.inventory_perc < 100)
            and self.env.health_perc < 30  # Don't want to fight with bosses
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.DIG)
            logger.info("Digging strategy executed.")

    def city_travel(self):
        closest_town = self.env.closest_town  # fix this (duel)
        if (
            (self.env.state_enum is HeroStates.WALKING)
            and self.hero_tracker.is_godvoice_available
            and (self.env.prana >= MIN_PRANA_CITY_TRAVEL)
            and (closest_town in BRICK_TOWNS)
            and (
                self.env.money + self.env.inventory[0] * 50
                > BRICK_TOWNS.get(closest_town)
            )
            and self.hero_tracker.can_return
            # and "(мини)" not in self.env.quest[1]
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.RETURN)
            logger.info("Returning strategy executed.")

    def zpg_arena(self):
        inv_cur, inv_full = self.env.inventory
        available_inv_slots = inv_full - inv_cur
        _, quest = self.env.quest  # fix this (duel)
        if (
            (
                self.env.state_enum
                not in [HeroStates.FISHING, HeroStates.DUEL, HeroStates.UNKNOWN]
            )
            and (self.env.prana >= 50)
            and (self.env.money < MAX_GOLD_ZPG_ARENA)
            and self.env.is_arena_available(zpg=True)
            and (available_inv_slots >= 3)
            and (("(гильд)" not in quest) and ("(мини)" not in quest))
            and self.env.closest_town not in BRICK_TOWNS
        ):
            self.hero_actions.go_to_zpg_arena()
            logger.info("ZPG arena strategy executed.")

    def cancel_leaving_guild(self):
        _, quest = self.env.quest  # fix this
        regex = r"стать \d+-м членом гильдии «[^»]+»"
        if (
            (self.env.state_enum not in [HeroStates.DUEL, HeroStates.UNKNOWN])
            and re.search(regex, quest)
            and (MY_GUILD not in quest)
            and ("(отменено)" not in quest)
            and (self.env.prana >= 5)
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.CANCEL)
            logger.info("Cancel task strategy executed.")

    def open_activatables(self):
        "If there are certain activatable items, we should open them."
        if self.env.state_enum not in [HeroStates.DUEL, HeroStates.UNKNOWN]:
            self.hero_actions.open_activatables()

    def craft_items(self):
        """Crafting items to get certain activatables."""
        # if enough prana
        # and crafting available (link text 'ящик')
        # but I don't see much point in this strategy since it may craft an activatable
        # that can be opened with 50% prana. And we've got 10 attempts max (usually less).
