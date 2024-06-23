import re  # noqa: F401
from bs4 import BeautifulSoup  # noqa: F401
from seleniumbase import SB
from pathlib import Path
from selenium.webdriver.common.by import By


def get_class_name(init_name):
    return "type-" + init_name.replace(" ", "-")


boxes = [
    "black box",
    "charge box",
    "gift box",
    "good box",
    "prize box",
    "treasure box",
]
friends = ["invite", "friend box"]
# smelter - 2000 gold, no fight
# transformer - many fat items
bricks = ["smelter", "transformer"]
all_names = []
for boxes_class in (boxes, friends, bricks):
    all_names.extend(map(get_class_name, boxes_class))
print(all_names)

web_page = (Path.cwd() / "pages/activatable.mhtml").as_uri()

with SB(uc=True, headless2=True) as sb:
    sb.open(web_page)

    inventory_items = sb.find_elements("ul.ul_inv > li")

    for item in inventory_items:
        item_name = item.find_element(By.TAG_NAME, "span").text

        class_attribute = item.get_attribute("class")
        match_good_activatables = any([name in class_attribute for name in all_names])
        if match_good_activatables:
            title_element = item.find_element(By.CSS_SELECTOR, "div > a")
            title = title_element.get_attribute("title") if title_element else None

            parentheses_text = None
            prana_price = None
            div_text = item.find_element(By.CSS_SELECTOR, "div.item_act_link_div").text
            match = re.search(r"\((.*?)\)", title)
            if match:
                parentheses_text = match.group(1)
                price = re.search(r"\d+", parentheses_text)
                if price:
                    prana_price = int(price.group(0))
                else:
                    prana_price = 0

            print(f"Name: {item_name}")
            print(f"Title: {title}")
            print(f"Prana price: {prana_price}")

            elem_click = item.find_element(By.CSS_SELECTOR, "div > a")

            elem_click.click()
            sb.click(elem_click)
