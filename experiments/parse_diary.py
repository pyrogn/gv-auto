from pathlib import Path
from seleniumbase import SB


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


# html_parse = get_uri_for_html("pages/no_response_true.mhtml")
# html_parse = get_uri_for_html("pages/response.mhtml")
# html_parse = get_uri_for_html("pages/no_response.mhtml")
html_parse = get_uri_for_html("pages/test_resp1.mhtml")

with SB(uc=True, headless2=True) as sb:
    sb.uc_open(html_parse)
    # breakpoint()
    for elem in sb.find_elements("#diary div.d_msg"):
        if "m_infl" in elem.get_attribute("class"):
            break
        print(elem.text)
        print("➥" in elem.text)
    # list(map(lambda x: x.text, sb.find_elements('#diary div.d_msg')))
    # list(map(lambda x: x.text, sb.find_elements('#diary div.d_msg.m_infl')))
