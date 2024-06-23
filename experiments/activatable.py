import re  # noqa: F401
from bs4 import BeautifulSoup  # noqa: F401
from seleniumbase import SB
from pathlib import Path
from selenium.webdriver.common.by import By

web_page = (Path.cwd() / "pages/activatable.mhtml").as_uri()

with SB(uc=True, headless2=True) as sb:
    sb.open(web_page)

    # Use the appropriate CSS selector to narrow down the search scope
    inventory_items = sb.find_elements("#inventory > div.block_content ul.ul_inv > li")

    for item in inventory_items:
        item_text = item.find_element(By.TAG_NAME, "span").text
        print(item_text)
        class_attribute = item.get_attribute("class")
        print("type-boss-box" in class_attribute)  # find what types exist

        # if "чёрный-чёрный ящик" in item_text:
        #     # print(item)
        #     # print(item_text)
        #     elem_click = item.find_element(By.CSS_SELECTOR, "div > a")
        # print(elem_click)

        # click somehow
        # elem_click.click()
        # sb.click(elem_click)
        # break
