import re  # noqa: F401
from bs4 import BeautifulSoup  # noqa: F401
from seleniumbase import SB
from pathlib import Path

web_page = (Path.cwd() / "pages/bingo_unavailable.mhtml").as_uri()

with SB(uc=True, headless2=True, user_data_dir="./chrome_profile") as sb:
    sb.open(web_page)

    text = sb.get_text("#l_clicks")
    print(text)
    print(int(re.search(r"Осталось нажатий: (\d+)\.", text).group(1)))
    # html_content = sb.get_page_source()
    # soup = BeautifulSoup(html_content, "html.parser")
