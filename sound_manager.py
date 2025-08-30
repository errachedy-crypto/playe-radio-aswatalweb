import vlc
import os
import logging

class SoundManager:
    def __init__(self, vlc_instance):
        """Initializes the sound manager with a shared VLC instance."""
        if vlc_instance is None:
            raise ValueError("A valid VLC instance must be provided.")
        self.vlc_instance = vlc_instance
        # Use a separate player for sound effects to not interfere with main playback
        self.sfx_player = self.vlc_instance.media_player_new()
        self.enabled = True

        # Sound URIs - using web-hosted sounds to avoid local file issues
        self.sounds = {
            "navigate": "https://www.soundjay.com/button/sounds/button-16.mp3",
            "play_station": "https://www.soundjay.com/button/sounds/button-7.mp3",
            "stop_station": "https://www.soundjay.com/button/sounds/button-10.mp3",
            "update_success": "https://www.soundjay.com/communication/sounds/demonstrative-1.mp3"
        }

    def set_enabled(self, enabled):
        """Enable or disable sound effects."""
        self.enabled = enabled

    def play(self, sound_name):
        """Play a sound effect by its name."""
        if not self.enabled:
            return

        sound_uri = self.sounds.get(sound_name)
        if sound_uri:
            try:
                media = self.vlc_instance.media_new(sound_uri)
                self.sfx_player.set_media(media)
                self.sfx_player.play()
            except Exception as e:
                logging.error(f"Failed to play sound '{sound_name}' from {sound_uri}: {e}")
        else:
            logging.warning(f"Sound '{sound_name}' not found in sound list.")
