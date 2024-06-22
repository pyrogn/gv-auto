from seleniumbase import SB
import time

config = [
    {"headless": True, "uc": True},
    {"headless": True, "uc": False},
    {"headless2": True, "uc": True},
    {"headless2": True, "uc": False},
    {"uc": True},
    {"uc": False},
]

for idx, param in enumerate(config):
    screenshot_filename = f"screenshots/checker_{idx}_headless_{param.get('headless', param.get('headless2', False))}_uc_{param['uc']}.png"
    with SB(user_data_dir="./chrome_profile", **param) as sb:
        sb.get("https://nowsecure.nl/#relax")
        time.sleep(6)
        sb.save_screenshot(screenshot_filename)
