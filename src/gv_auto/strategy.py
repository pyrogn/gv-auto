import logging
from gv_auto.environment import EnvironmentInfo
from gv_auto.hero import HeroActions, HeroTracker
from gv_auto.logger import setup_logging
from gv_auto.game_info import HeroStates, VOICEGOD_TASK, INFLUENCE_TYPE
import traceback

setup_logging()
logger = logging.getLogger(__name__)

BRICK_TOWNS = {
    "Торгбург": 2400,  # 2000-2700
    "Снаряжуполь": 1500,  # 1000-1700
    "Някинск": 1500,  # 1000-1700
}
MY_GUILD = "Ряды Фурье"
MAX_GOLD_ZPG_ARENA = 2300
MIN_PERC_INV_BINGO = 50
MIN_PRANA_DIGGING = 55
MIN_PRANA_CITY_TRAVEL = 30


class Strategies:
    def __init__(
        self, hero_actions: HeroActions, env: EnvironmentInfo, hero_tracker: HeroTracker
    ):
        self.hero_actions = hero_actions
        self.env = env
        self.hero_tracker = hero_tracker

    def check_and_execute(self) -> None:
        basic_strategies = [
            self.melt_bricks,
            self.bingo,
            self.zpg_arena,
            self.digging,
            self.city_travel,  # test it
            self.open_activatables,  # test it
        ]
        for strategy in basic_strategies:
            try:
                strategy()
            except Exception as e:
                logger.error(
                    f"Error in {strategy.__name__} strategy: {e}\n{traceback.format_exc()}"
                )

        advanced_strategies = [  # noqa: F841
            self.cancel_leaving_guild,
            self.craft_items,
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
        if self.hero_tracker.is_bingo_available and self.env.state_enum not in [
            HeroStates.DUEL
        ]:
            if self.env.inventory_perc >= MIN_PERC_INV_BINGO:
                self.hero_actions.play_bingo()
                logger.info("Bingo strategy executed.")
            elif self.hero_tracker.bingo_last_call:
                self.hero_actions.play_bingo(finish=True)
                logger.info("Bingo last call strategy executed.")

    def digging(self):
        if (
            self.hero_tracker.is_godvoice_available
            and (self.env.prana >= MIN_PRANA_DIGGING)
            and (self.env.inventory_perc < 100)
            and self.env.state_enum
            in [HeroStates.WALKING, HeroStates.RETURNING, HeroStates.UNKNOWN]
            and self.env.health_perc < 30  # Don't want to fight with bosses
        ):
            self.hero_actions.godvoice(VOICEGOD_TASK.DIG)
            logger.info("Digging strategy executed.")

    def city_travel(self):
        closest_town = self.env.closest_town
        if (
            self.hero_tracker.is_godvoice_available
            and (self.env.prana >= MIN_PRANA_CITY_TRAVEL)
            and (self.env.state_enum is HeroStates.WALKING)
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
        if (
            (self.env.prana >= 50)
            and (
                self.env.state_enum
                not in [HeroStates.FISHING, HeroStates.DUEL, HeroStates.UNKNOWN]
            )
            and (self.env.money < MAX_GOLD_ZPG_ARENA)
            and self.env.is_arena_available(zpg=True)
            and (available_inv_slots >= 3)
            and not (
                self.env.closest_town in BRICK_TOWNS
                and self.env.state_enum is HeroStates.RETURNING
            )
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
            and (self.env.state_enum not in [HeroStates.DUEL, HeroStates.UNKNOWN])
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
