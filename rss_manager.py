import json
import os
import feedparser

FEEDS_FILE = os.path.join(os.path.expanduser("~"), "stv_radio_rss_feeds.json")

class RSSManager:
    def __init__(self):
        self._feeds = self._load_or_create_feeds()

    def _load_or_create_feeds(self):
        """Loads feeds from file, or creates a default list if the file doesn't exist."""
        if not os.path.exists(FEEDS_FILE):
            print("Feeds file not found. Creating a default list.")
            default_feeds = [
                "https://www.aljazeera.net/aljazeerarss/rss.xml",
                "https://feeds.bbci.co.uk/arabic/rss.xml",
                "https://www.skynewsarabia.com/rss/all.xml",
                "https://www.alarabiya.net/.mrss/ar.xml"
            ]
            try:
                with open(FEEDS_FILE, "w", encoding="utf-8") as f:
                    json.dump(default_feeds, f, ensure_ascii=False, indent=4)
            except IOError:
                pass
            return default_feeds

        try:
            with open(FEEDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return []

    def _save_feeds(self):
        """Saves the current list of RSS feeds to the JSON file."""
        try:
            with open(FEEDS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._feeds, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def get_feeds(self):
        """Returns the list of saved feed URLs."""
        return self._feeds

    def add_feed(self, feed_url):
        """Adds a new feed URL to the list if it's not already there."""
        if feed_url not in self._feeds:
            self._feeds.append(feed_url)
            self._save_feeds()
            return True
        return False

    def remove_feed(self, feed_url):
        """Removes a feed URL from the list."""
        if feed_url in self._feeds:
            self._feeds.remove(feed_url)
            self._save_feeds()
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
