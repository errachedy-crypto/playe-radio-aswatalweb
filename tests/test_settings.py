import unittest
from unittest.mock import patch
import os
import json
import tempfile

import settings

class TestSettings(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.settings_path = os.path.join(self.test_dir.name, "settings.json")
        self.cache_path = os.path.join(self.test_dir.name, "cache.json")

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('settings.get_settings_path')
    def test_load_settings_no_file(self, mock_get_path):
        """Test that default settings are returned when the file doesn't exist."""
        mock_get_path.return_value = self.settings_path
        s = settings.load_settings()
        self.assertEqual(s['volume'], 40)
        self.assertEqual(s['theme'], 'light')

    @patch('settings.get_settings_path')
    def test_load_settings_file_exists(self, mock_get_path):
        """Test that settings are loaded correctly from an existing file."""
        mock_get_path.return_value = self.settings_path
        test_settings = {"volume": 80, "theme": "dark"}
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(test_settings, f)

        s = settings.load_settings()
        self.assertEqual(s['volume'], 80)
        self.assertEqual(s['theme'], 'dark')

    @patch('settings.get_settings_path')
    def test_load_settings_partial_file(self, mock_get_path):
        """Test that default values are applied for missing keys."""
        mock_get_path.return_value = self.settings_path
        test_settings = {"volume": 75}
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(test_settings, f)

        s = settings.load_settings()
        self.assertEqual(s['volume'], 75)
        self.assertEqual(s['theme'], 'light')  # Default value should be present

    @patch('settings.get_settings_path')
    def test_load_settings_invalid_json(self, mock_get_path):
        """Test that default settings are returned for a corrupt/invalid JSON file."""
        mock_get_path.return_value = self.settings_path
        with open(self.settings_path, "w", encoding="utf-8") as f:
            f.write("this is not valid json")

        s = settings.load_settings()
        self.assertEqual(s['volume'], 40)
        self.assertEqual(s['theme'], 'light')

    @patch('settings.get_settings_path')
    def test_save_settings(self, mock_get_path):
        """Test that settings are saved correctly to a file."""
        mock_get_path.return_value = self.settings_path
        test_settings = {"volume": 55, "play_on_startup": True}
        settings.save_settings(test_settings)

        with open(self.settings_path, "r", encoding="utf-8") as f:
            saved = json.load(f)

        self.assertEqual(saved['volume'], 55)
        self.assertEqual(saved['play_on_startup'], True)

    @patch('settings.get_stations_cache_path')
    def test_load_stations_cache_no_file(self, mock_get_path):
        """Test that None is returned when the cache file doesn't exist."""
        mock_get_path.return_value = self.cache_path
        cache = settings.load_stations_cache()
        self.assertIsNone(cache)

    @patch('settings.get_stations_cache_path')
    def test_load_stations_cache_file_exists(self, mock_get_path):
        """Test that the station cache is loaded correctly from an existing file."""
        mock_get_path.return_value = self.cache_path
        test_cache = [{"name": "Category", "stations": []}]
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(test_cache, f)

        cache = settings.load_stations_cache()
        self.assertEqual(cache, test_cache)

    @patch('settings.get_stations_cache_path')
    def test_load_stations_cache_invalid_json(self, mock_get_path):
        """Test that None is returned for a corrupt/invalid cache JSON file."""
        mock_get_path.return_value = self.cache_path
        with open(self.cache_path, "w", encoding="utf-8") as f:
            f.write("this is not valid json")

        cache = settings.load_stations_cache()
        self.assertIsNone(cache)

    @patch('settings.get_stations_cache_path')
    def test_save_stations_cache(self, mock_get_path):
        """Test that the station cache is saved correctly to a file."""
        mock_get_path.return_value = self.cache_path
        test_cache = [{"name": "News", "stations": [{"name": "News FM", "url": "http://news.fm"}]}]
        settings.save_stations_cache(test_cache)

        with open(self.cache_path, "r", encoding="utf-8") as f:
            saved = json.load(f)

        self.assertEqual(saved, test_cache)

if __name__ == '__main__':
    unittest.main()
