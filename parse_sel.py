import re
from bs4 import BeautifulSoup
from seleniumbase import SB
from pathlib import Path

web_page = (Path.cwd() / "pages/answered.mht").as_uri()

with SB(uc=True, headless=True, user_data_dir="./chrome_profile") as sb:
    sb.open(web_page)
    html_content = sb.get_page_source()
    soup = BeautifulSoup(html_content, "html.parser")

    towns = soup.find_all("g", class_="tl")
    for town in towns:
        title = town.find("title")
        if title:
            town_text = title.get_text()
            match = re.search(r"(.*?) \((\d+)\)", town_text)

            if match:
                town = match.group(1)
                miles = match.group(2)
                print(town, miles)

    # towns = sb.find_elements("g.tl")
    # # print(towns)
    # for town in towns:
    #     title = town.get_attribute("title")
    #     if title:
    #         print(title)

    latest_entry_text = sb.get_text("div.d_msg")
    print("Latest Diary Entry:", latest_entry_text)
    print("➥" in latest_entry_text)
