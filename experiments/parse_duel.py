from pathlib import Path
from seleniumbase import SB


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


# html_parse = get_uri_for_html("pages/no_response_true.mhtml")
# html_parse = get_uri_for_html("pages/response.mhtml")
# html_parse = get_uri_for_html("pages/no_response.mhtml")
html_duel = get_uri_for_html("pages/duel1.mhtml")
html_normal = get_uri_for_html("pages/test_resp1.mhtml")

with SB(uc=True, headless2=True) as sb:
    for html_url in (html_duel, html_normal):
        sb.uc_open(html_url)
        # breakpoint()
        print(sb.is_element_present("#diary"))
        print(sb.is_element_present("#m_fight_log"))
        # #m_fight_log > div.block_h > h2
