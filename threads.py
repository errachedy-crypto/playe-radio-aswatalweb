import requests
import json
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from packaging import version

from constants import STATIONS_URL
from settings import load_stations_cache, save_stations_cache


class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)

    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url

    def run(self):
        try:
            logging.debug("Checking for updates...")
            response = requests.get(self.update_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            latest_version_str = data.get("latest_version")
            download_url = data.get("download_url")
            if latest_version_str and download_url and version.parse(latest_version_str) > version.parse(self.current_version):
                self.update_available.emit(latest_version_str, download_url)
            logging.debug(f"Update check completed. Latest version: {latest_version_str}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to check for updates: {e}")
        except (json.JSONDecodeError, AttributeError):
            logging.error("Failed to decode update JSON.")


class StationLoader(QThread):
    stationsLoaded = pyqtSignal(list)
    errorOccurred = pyqtSignal(str, bool)

    def run(self):
        try:
            logging.debug("Attempting to load stations from network...")
            response = requests.get(STATIONS_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            categories = data.get("categories", [])

            if not categories:
                raise ValueError("No categories found in the station list.")

            logging.info(f"Successfully loaded {len(categories)} categories from network.")
            save_stations_cache(categories)
            self.stationsLoaded.emit(categories)

        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            logging.warning(f"Could not load stations from network: {e}. Attempting to load from cache.")

            cached_categories = load_stations_cache()
            if cached_categories:
                logging.info("Successfully loaded stations from cache.")
                self.stationsLoaded.emit(cached_categories)
                self.errorOccurred.emit("فشل تحديث قائمة الإذاعات. يتم عرض نسخة محفوظة.", False)
            else:
                logging.error("Failed to load stations from network and no cache available.")
                self.errorOccurred.emit("فشل تحميل قائمة الإذاعات من الإنترنت ولا توجد نسخة محفوظة. يرجى التحقق من اتصالك بالإنترنت.", True)
