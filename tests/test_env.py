from seleniumbase import SB

from gv_auto.environment import EnvironmentInfo
from tests.utils import get_uri_for_html


def test_environment_info():
    with SB(uc=True, headless2=True) as sb:
        page_url = get_uri_for_html("pages/page1.mhtml")
        sb.open(page_url)
        env = EnvironmentInfo(sb)
        assert env.money == 1702
        # add more and more
