from datetime import datetime
import logging
from pathlib import Path


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Log to console
            logging.FileHandler("bot.log"),  # Log to file
        ],
    )


class LogError:
    def __init__(self, driver) -> None:
        self.driver = driver

    def log_error(self):
        error_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = Path("error_logs") / error_id
        folder_path.mkdir(parents=True, exist_ok=True)

        screenshot_path = folder_path / "screenshot.png"
        self.driver.save_screenshot(str(screenshot_path))

        page_source_path = folder_path / "page_source.html"
        self.driver.save_page_source(str(page_source_path))
