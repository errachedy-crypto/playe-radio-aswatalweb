import json
import os
import feedparser
import logging
import requests
import configparser

LOCAL_FEEDS_FILE = os.path.join(os.path.expanduser("~"), "stv_radio_custom_feeds.json")
REMOTE_FEEDS_CACHE_FILE = os.path.join(os.path.expanduser("~"), "stv_radio_remote_feeds_cache.json")
REMOTE_FEEDS_URL = "https://aswatalweb.com/radio/Feeds-radio/DefaultListRSS.Ini"

class RSSManager:
    def __init__(self):
        self._local_categories = self._load_local_categories()

    def get_merged_categories(self):
        """
        Fetches remote categories, loads local categories, and merges them.
        The returned structure includes a 'source' key for each category.
        """
        remote_categories = self._fetch_remote_categories()
        for cat in remote_categories:
            cat['source'] = 'remote'

        merged_categories = [dict(c) for c in remote_categories]
        remote_cat_names = {c['name'] for c in merged_categories}

        for local_cat in self._local_categories:
            local_cat_with_source = dict(local_cat)
            local_cat_with_source['source'] = 'local'

            if local_cat['name'] not in remote_cat_names:
                merged_categories.append(local_cat_with_source)
            else:
                for remote_cat in merged_categories:
                    if remote_cat['name'] == local_cat['name']:
                        for feed_url in local_cat['feeds']:
                            if feed_url not in remote_cat['feeds']:
                                remote_cat['feeds'].append(feed_url)
                        break
        return merged_categories

    def _load_local_categories(self):
        """Loads the user's custom feeds and categories from a local JSON file."""
        if not os.path.exists(LOCAL_FEEDS_FILE):
            return []
        try:
            with open(LOCAL_FEEDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except (IOError, json.JSONDecodeError):
            return []

    def _save_local_categories(self):
        """Saves the user's custom feeds and categories."""
        try:
            with open(LOCAL_FEEDS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._local_categories, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def _fetch_remote_categories(self):
        """Fetches remote categories from the web, with a local cache fallback."""
        try:
            logging.info("Attempting to fetch remote feeds from network...")
            response = requests.get(REMOTE_FEEDS_URL, timeout=20)
            response.raise_for_status()
            ini_content = response.content.decode('utf-8-sig')

            config = configparser.ConfigParser(interpolation=None)
            config.read_string(ini_content)

            categories = {}
            for section in config.sections():
                group = config.get(section, 'Group', fallback='متفرقات').strip()
                url = config.get(section, 'Url', fallback=None)
                if url:
                    if group not in categories:
                        categories[group] = []
                    categories[group].append(url)

            parsed_data = [{"name": name, "feeds": feeds} for name, feeds in categories.items()]

            with open(REMOTE_FEEDS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=4)

            return parsed_data

        except requests.exceptions.RequestException as e:
            logging.warning(f"Could not fetch remote feeds list: {e}. Attempting to load from cache.")
            try:
                with open(REMOTE_FEEDS_CACHE_FILE, "r", encoding="utf-8") as f:
                    logging.info("Successfully loaded remote feeds from cache.")
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                logging.error("Failed to load remote feeds from cache.")
                return []
        except configparser.Error as e:
            logging.error(f"Could not parse remote feeds list: {e}")
            return []

    def add_category(self, category_name):
        """Adds a new category to the local list."""
        for category in self._local_categories:
            if category['name'] == category_name:
                return False
        self._local_categories.append({"name": category_name, "feeds": []})
        self._save_local_categories()
        return True

    def remove_category(self, category_name):
        """Removes a category from the local list."""
        category_to_remove = None
        for category in self._local_categories:
            if category['name'] == category_name:
                category_to_remove = category
                break
        if category_to_remove:
            self._local_categories.remove(category_to_remove)
            self._save_local_categories()
            return True
        return False

    def add_feed_to_category(self, feed_url, category_name):
        """Adds a feed to a category in the local list."""
        target_category = None
        for category in self._local_categories:
            if category['name'] == category_name:
                target_category = category
                break
        if not target_category:
            self.add_category(category_name)
            for category in self._local_categories:
                if category['name'] == category_name:
                    target_category = category
                    break
        if target_category:
            if feed_url not in target_category['feeds']:
                target_category['feeds'].append(feed_url)
                self._save_local_categories()
                return True
        return False

    def remove_feed_from_category(self, feed_url, category_name):
        """Removes a feed from a category in the local list."""
        for category in self._local_categories:
            if category['name'] == category_name:
                if feed_url in category['feeds']:
                    category['feeds'].remove(feed_url)
                    self._save_local_categories()
                    return True
        return False

    def fetch_feed_articles(self, feed_url):
        """Fetches and parses articles from a given feed URL."""
        try:
            parsed_feed = feedparser.parse(feed_url)
            if parsed_feed.bozo:
                print(f"Warning: Feed '{feed_url}' may be malformed. Error: {parsed_feed.bozo_exception}")

            articles = []
            for entry in parsed_feed.entries:
                articles.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "No Date"),
                    "summary": entry.get("summary", "No Summary"),
                })
            return articles
        except Exception as e:
            print(f"Error fetching feed '{feed_url}': {e}")
            return None
