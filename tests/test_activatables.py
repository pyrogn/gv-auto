from pathlib import Path
from seleniumbase import SB
from unittest.mock import patch

from gv_auto.environment import EnvironmentInfo


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


def test_parsing():
    with patch("gv_auto.environment.USEFUL_AND_FUN_ACTIVATABLES", ["type-smelter"]):
        with SB(uc=True, headless2=True) as sb:
            uri = get_uri_for_html("pages/smelter.mhtml")
            sb.open(uri)
            env = EnvironmentInfo(sb)

            print(env.activatables)
