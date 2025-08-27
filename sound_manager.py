import logging

try:
    import vlc
except (ImportError, FileNotFoundError):
    vlc = None

class SoundManager:
    def __init__(self, vlc_instance):
        self.vlc_instance = vlc_instance
        self.sfx_player = None
        self.enabled = False

        if self.vlc_instance:
            try:
                self.sfx_player = self.vlc_instance.media_player_new()
                self.enabled = True
                logging.info("SoundManager initialized successfully with shared VLC instance.")
            except Exception as e:
                self.sfx_player = None
                self.enabled = False
                logging.error(f"SoundManager: Failed to create media player from shared instance: {e}")
        else:
            logging.warning("SoundManager: No valid VLC instance provided. Sound effects will be disabled.")

        self.sounds = {
            "startup": "https://aswatalweb.com/radio/media/demarage.wav",
            "update_success": "https://aswatalweb.com/radio/media/misajour_du_play_station.wav",
            "navigate": "https://aswatalweb.com/radio/media/When_moving_between_the_stations_in_the_list.wav",
            "play_station": "https://aswatalweb.com/radio/media/When_starting_a%20station.wav",
            "stop_station": "https://aswatalweb.com/radio/media/When_turning_off_a_station.wav"
        }

    def set_enabled(self, enabled):
        """Enable or disable sound effects."""
        self.enabled = enabled
        logging.info(f"Sound effects have been {'enabled' if enabled else 'disabled'}.")

    def play(self, sound_name):
        """Play a sound effect by its name."""
        if not self.enabled or not self.sfx_player:
            return

        if sound_name in self.sounds:
            url = self.sounds[sound_name]
            try:
                media = self.vlc_instance.media_new(url)
                self.sfx_player.set_media(media)
                self.sfx_player.play()
                logging.debug(f"Playing sound effect: '{sound_name}' from {url}")
            except Exception as e:
                logging.error(f"Failed to play sound effect '{sound_name}': {e}")
        else:
            logging.warning(f"Sound effect not found: '{sound_name}'")
