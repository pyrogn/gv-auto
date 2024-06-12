import logging
from dotenv import dotenv_values
from seleniumbase import SB
from pathlib import Path

config = dotenv_values()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

web_page = (Path.cwd() / "pages/login_page.mht").as_uri()
web_page = "https://godville.net/"

if __name__ == "__main__":
    with SB(uc=True, headless=False, user_data_dir="./chrome_profile3") as sb:
        logging.info("Driver is launched")
        sb.open(web_page)
        logging.info("Page is loaded")
        link = sb.get_current_url()
        if "superhero" not in link:
            sb.type("#username", config["LOGIN"])
            sb.type("#password", config["PASSWORD"])
            sb.uc_click('input[value="Войти!"]')
            print("trying to log in")
        link = sb.get_current_url()
        assert "superhero" in link, "login is unsuccessful"
        if sb.is_element_present("a.dm_close"):
            sb.uc_click("a.dm_close")
            print("close direct message")
