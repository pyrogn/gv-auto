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

    def get_response(self) -> str:
        """Read what's in a diary at and after last influence."""
        responses = []
        for elem in self.driver.find_elements("#diary div.d_msg"):
            if "m_infl" in elem.get_attribute("class"):
                responses.append(elem.text)
                break
            responses.append(elem.text)  # maybe I don't need it, only m_infl
        return "|".join(responses)

    def understand_response(self) -> Responses:
        """Determine if hero is reponded after last influence."""
        # maybe we should add validation that we sent some godvoice
        # we assume top messages are more recent (default UI)
        for elem in self.driver.find_elements("#diary div.d_msg"):
            if "m_infl" in elem.get_attribute("class"):
                break
            if "➥" in elem.text:
                return Responses.RESPONDED
        return Responses.IGNORED
