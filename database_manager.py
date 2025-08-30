import sqlite3
import logging
import os

DB_FILE = "podcasts.db"

def initialize_database():
    """Create the database and the podcasts table if they don't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS podcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rss_url TEXT NOT NULL UNIQUE,
                image_url TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database error during initialization: {e}")

def add_podcast(name, rss_url, image_url=None):
    """Add a new podcast feed to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO podcasts (name, rss_url, image_url) VALUES (?, ?, ?)",
                       (name, rss_url, image_url))
        conn.commit()
        conn.close()
        logging.info(f"Added podcast '{name}' with URL: {rss_url}")
        return True
    except sqlite3.IntegrityError:
        logging.warning(f"Podcast with URL {rss_url} already exists.")
        return False
    except sqlite3.Error as e:
        logging.error(f"Failed to add podcast: {e}")
        return False

def delete_podcast(podcast_id):
    """Delete a podcast from the database by its ID."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM podcasts WHERE id = ?", (podcast_id,))
        conn.commit()
        conn.close()
        logging.info(f"Deleted podcast with ID: {podcast_id}")
        return True
    except sqlite3.Error as e:
        logging.error(f"Failed to delete podcast: {e}")
        return False

def get_all_podcasts():
    """Retrieve all podcasts from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM podcasts ORDER BY name")
        podcasts = cursor.fetchall()
        conn.close()
        return [dict(row) for row in podcasts]
    except sqlite3.Error as e:
        logging.error(f"Failed to fetch podcasts: {e}")
        return []
