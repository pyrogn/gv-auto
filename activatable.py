import re  # noqa: F401
from bs4 import BeautifulSoup  # noqa: F401
from seleniumbase import SB
from pathlib import Path

web_page = (Path.cwd() / "pages/activatable.mhtml").as_uri()

with SB(uc=True, headless2=True, user_data_dir="./chrome_profile") as sb:
    sb.open(web_page)

    elements = sb.find_elements("li")

    for element in elements:
        if "чёрный-чёрный ящик" in element.text:
            print(element)
            print(element.text)
            elem_click = element.find_element("div > a")
            print(elem_click)
            # sb.click(elem_click)
            break
