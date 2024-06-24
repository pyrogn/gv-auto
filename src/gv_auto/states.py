from enum import Enum, auto


class HeroStates(Enum):
    SLEEPING = auto()
    WALKING = auto()
    RETURNING = auto()
    FISHING = auto()
    HEALING = auto()
    FIGHTING = auto()
    AFTER_ARENA = auto()
    DUEL = auto()
    TRADING = auto()
    LEISURE = auto()
    ADVENTURE = auto()
    PRAYING = auto()
    DEATH = auto()
    UNKNOWN = auto()


class VOICEGOD_TASK(Enum):
    FIGHT = auto()
    HEAL = auto()
    RETURN = auto()
    DIG = auto()
    CANCEL = auto()


class INFLUENCE_TYPE(Enum):
    ENCOURAGE = auto()
    PUNISH = auto()


activity_map = {
    HeroStates.SLEEPING: ["Сон"],
    HeroStates.WALKING: ["Дорога"],
    HeroStates.RETURNING: ["Возврат"],
    HeroStates.HEALING: ["Лечение"],
    HeroStates.FIGHTING: ["Бой"],
    HeroStates.DUEL: ["Босс", "Дуэль", "Битва"],
    HeroStates.TRADING: ["Торговля"],
    HeroStates.FISHING: ["Рыбалка"],
    HeroStates.LEISURE: ["Отдых"],
    HeroStates.ADVENTURE: ["Авантюра"],
    HeroStates.PRAYING: ["Молитва"],
    HeroStates.DEATH: ["Смерть"],
    HeroStates.AFTER_ARENA: ["Бытие"],
}

voicegods_map = {
    VOICEGOD_TASK.FIGHT: ["Бей"],
    VOICEGOD_TASK.HEAL: ["Лечись"],
    VOICEGOD_TASK.RETURN: ["Домой"],
    VOICEGOD_TASK.DIG: ["Копай клад!"],
    VOICEGOD_TASK.CANCEL: ["Отмени задание"],
}

str_state2enum_state = {}
for k, v in activity_map.items():
    for say in v:
        str_state2enum_state[say] = k


def get_class_name(init_name):
    return "type-" + init_name.replace(" ", "-")


boxes = [
    "black box",
    "charge box",
    "gift box",
    "good box",
    "prize box",
    "treasure box",
]
# friend box costs 50% prana
friends = ["invite", "friend box"]
# smelter - 2000 gold, no fight
# transformer - many fat items
bricks = ["smelter", "transformer"]
all_boxes = [*boxes, *friends]
# all_boxes.extend(bricks) # need special conditions for them
BRICK_FRIEND_ACTIVATABLES = list(map(get_class_name, all_boxes))
