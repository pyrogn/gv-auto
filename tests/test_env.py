from pathlib import Path
from seleniumbase import SB

from gv_auto.auto import EnvironmentInfo


def test_environment_info():
    with SB(uc=True, headless2=True) as sb:
        page_url = (Path.cwd() / "pages/page1.mhtml").as_uri()
        sb.open(page_url)
        env = EnvironmentInfo(sb)
        assert env.money == 1702
