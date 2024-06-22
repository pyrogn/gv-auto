from enum import Enum, auto
from pathlib import Path


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


class Responses(Enum):
    IGNORED = auto()
    RESPONDED = auto()


class UnderstandResponse:
    def __init__(self, driver) -> None:
        self.driver = driver

    def understand_response(self) -> Responses:
        # maybe we should add validation that we sent some godvoice
        responses = []
        # we assume top messages are more recent (default UI)
        for elem in self.driver.find_elements("#diary div.d_msg"):
            if "m_infl" in elem.get_attribute("class"):
                break
        for response in responses:
            if "➥" in response:
                return Responses.RESPONDED
        return Responses.IGNORED


# maybe:
# we should add tracking of states (bricks, quests, prana, state)
# and we'll call it success
# but it's no use for now, just for easier tracking and reading logs
