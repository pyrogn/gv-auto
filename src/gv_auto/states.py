from enum import Enum, auto


class HeroStates(Enum):
    SLEEPING = auto()
    WALKING = auto()
    RETURNING = auto()
    FISHING = auto()
    HEALING = auto()
    FIGHTING = auto()
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
    HeroStates.DUEL: ["Босс", "Дуэль", "Битва"],  # to find out
    HeroStates.TRADING: ["Торговля"],
    HeroStates.FISHING: ["Рыбалка"],
    HeroStates.LEISURE: ["Отдых"],
    HeroStates.ADVENTURE: ["Авантюра"],
    HeroStates.PRAYING: ["Молитва"],
    HeroStates.DEATH: ["Смерть"],
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
