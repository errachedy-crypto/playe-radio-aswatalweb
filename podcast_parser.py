import feedparser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_feed(feed_url):
    """
    Parses a podcast RSS feed and returns the feed's title and a list of episodes.

    Args:
        feed_url (str): The URL of the RSS feed.

    Returns:
        tuple: A tuple containing (feed_title, episodes_list).
               Returns (None, []) if the feed cannot be parsed.
    """
    try:
        logging.info(f"Parsing feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            logging.warning(f"Malformed feed at {feed_url}. Bozo exception: {feed.bozo_exception}")
            # We can still try to process it, feedparser often recovers.

        feed_title = feed.feed.get('title', 'Untitled Podcast')

        episodes = []
        for entry in feed.entries:
            episode = {
                'title': entry.get('title', 'No Title'),
                'link': None, # This will hold the audio URL
                'description': entry.get('summary', 'No description available.'),
                'published': entry.get('published', 'No date available.')
            }

            # Find the audio enclosure link, which is the standard way to specify podcast media.
            if 'enclosures' in entry:
                for enclosure in entry.enclosures:
                    if 'audio' in enclosure.get('type', ''):
                        episode['link'] = enclosure.href
                        break # Take the first audio enclosure found

            # As a fallback, check if the standard 'link' tag points to an audio file.
            if not episode['link'] and entry.get('link', '').endswith(('.mp3', '.m4a', '.wav', '.ogg')):
                 episode['link'] = entry.get('link')

            # Only add the episode if we successfully found a playable link
            if episode['link']:
                episodes.append(episode)
            else:
                logging.warning(f"No audio link found for episode: {episode['title']}")

        logging.info(f"Found title '{feed_title}' and {len(episodes)} episodes in feed.")
        return feed_title, episodes

    except Exception as e:
        logging.error(f"Critical error parsing feed at {feed_url}: {e}")
        return None, []
