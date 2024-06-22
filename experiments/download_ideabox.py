import random
from seleniumbase import SB

links = [
    "diary",
    "e_news",
    "duels",
    "dungeons",
    "sail",
    "quests",
    "monsters",
    "artifacts",
    "equipment",
    "news",
]
urls = ["https://godville.net/ideabox/show/" + i for i in links]

with SB(
    uc=True,
    headless2=False,
    user_data_dir="./chrome_profile",
    # these options might speed up loading
    sjw=True,
    pls="none",
    ad_block_on=True,
) as sb:
    for url in urls:
        sb.uc_open(url)
        sb.reconnect(random.randint(2, 5))
        html_save = sb.get_page_source()
        category = url.split("/")[-1]
        with open(f"pages/ideabox/{category}.html", "w") as f:
            f.write(html_save)
