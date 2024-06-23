"""Compare headless and usual versions."""

from seleniumbase import SB


for headless in (True, False):
    with SB(
        uc=True,
        headless2=headless,
        user_data_dir="./chrome_profile",
    ) as sb:
        print(f"Headless: {headless}")
        print(f"UserAgent: {sb.get_user_agent()}")
        print(sb.get_chrome_version())
        print(sb.get_chromium_version())
        print(sb.get_chromedriver_version())
        print(sb.get_chromium_driver_version())
        print(sb.get_locale_code())
        print()
