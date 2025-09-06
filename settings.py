import os
import json

def get_settings_path():
    """Returns the path to the settings file."""
    return os.path.join(os.path.expanduser("~"), "stv_radio_settings.json")

def load_settings():
    """Loads settings from the settings file."""
    path = get_settings_path()
    defaults = {
        "check_for_updates": True,
        "play_on_startup": False,
        "theme": "light",
        "large_font": False,
        "volume": 40,
        "last_station_name": None,
        "enable_rss_reader": False,
    }
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        for key, value in defaults.items():
            settings.setdefault(key, value)
        return settings
    except (IOError, json.JSONDecodeError):
        return defaults

def save_settings(settings):
    """Saves settings to the settings file."""
    try:
        with open(get_settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except IOError:
        pass

def get_stations_cache_path():
    """Returns the path to the station cache file."""
    return os.path.join(os.path.expanduser("~"), "stv_radio_stations_cache.json")

def load_stations_cache():
    """Loads the station list from the cache file."""
    path = get_stations_cache_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None

def save_stations_cache(categories):
    """Saves the station list (categories) to the cache file."""
    try:
        with open(get_stations_cache_path(), "w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)
    except IOError:
        pass