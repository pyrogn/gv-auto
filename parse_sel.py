from seleniumbase import SB
from pathlib import Path

web_page = (Path.cwd() / "pages/answered.mht").as_uri()

with SB(uc=True, headless=True, user_data_dir="./chrome_profile") as sb:
    sb.open(web_page)

    # Find the diary entries
    # diary_entries = sb.find_elements(
    #     "#diary > div.block_content > div > div.d_content > div.d_line"
    # )

    # # Print all found elements (for debugging purposes)
    # print(diary_entries)

    # Extract the text from the latest (first) diary entry
    # if diary_entries:
    latest_entry_text = sb.get_text("div.d_msg")
    print("Latest Diary Entry:", latest_entry_text)
    print("➥" in latest_entry_text)
    # else:
    #     print("No diary entries found")
