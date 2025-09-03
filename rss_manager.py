import json
import os
import feedparser

FEEDS_FILE = os.path.join(os.path.expanduser("~"), "stv_radio_rss_feeds.json")

class RSSManager:
    def __init__(self):
        self._categories = self._load_or_create_feeds()

    def _load_or_create_feeds(self):
        """Loads categorized feeds from file, or creates a default list if the file doesn't exist."""
        if not os.path.exists(FEEDS_FILE):
            print("Feeds file not found. Creating a default list with categories.")
            default_structure = [
                {
                    "name": "أخبار",
                    "feeds": [
                        "https://www.aljazeera.net/aljazeerarss/rss.xml",
                        "https://feeds.bbci.co.uk/arabic/rss.xml",
                        "https://www.skynewsarabia.com/rss/all.xml",
                        "https://www.alarabiya.net/.mrss/ar.xml",
                    ]
                },
                {
                    "name": "تقنية",
                    "feeds": [
                        "https://www.tech-wd.com/feed/",
                        "https://www.unlimit-tech.com/feed/",
                    ]
                },
                {
                    "name": "رياضة",
                    "feeds": [
                        "https://www.kooora.com/rss/"
                    ]
                }
            ]
            self._save_structure(default_structure)
            return default_structure

        try:
            with open(FEEDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return []

    def _save_structure(self, structure):
        """Saves the entire category structure to the JSON file."""
        try:
            with open(FEEDS_FILE, "w", encoding="utf-8") as f:
                json.dump(structure, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def get_categories(self):
        """Returns the list of category objects."""
        return self._categories

    def add_category(self, category_name):
        """Adds a new, empty category."""
        for category in self._categories:
            if category['name'] == category_name:
                return False # Category already exists
        self._categories.append({"name": category_name, "feeds": []})
        self._save_structure(self._categories)
        return True

    def remove_category(self, category_name):
        """Removes a category and all its feeds."""
        category_to_remove = None
        for category in self._categories:
            if category['name'] == category_name:
                category_to_remove = category
                break
        if category_to_remove:
            self._categories.remove(category_to_remove)
            self._save_structure(self._categories)
            return True
        return False

    def add_feed_to_category(self, feed_url, category_name):
        """Adds a new feed URL to a specific category."""
        for category in self._categories:
            if category['name'] == category_name:
                if feed_url not in category['feeds']:
                    category['feeds'].append(feed_url)
                    self._save_structure(self._categories)
                    return True
        return False # Category not found or feed already exists

    def remove_feed_from_category(self, feed_url, category_name):
        """Removes a feed URL from a specific category."""
        for category in self._categories:
            if category['name'] == category_name:
                if feed_url in category['feeds']:
                    category['feeds'].remove(feed_url)
                    self._save_structure(self._categories)
                    return True
        return False # Category or feed not found

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
