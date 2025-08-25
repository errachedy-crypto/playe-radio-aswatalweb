import logging
try:
    import vlc
except (ImportError, FileNotFoundError):
    vlc = None

class Player:
    def __init__(self):
        self.vlc_instance = None
        self.vlc_player = None
        self.vlc_available = False

        self._initialize_vlc()

    def _initialize_vlc(self):
        if vlc:
            try:
                self.vlc_instance = vlc.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
                self.vlc_available = True
                logging.info("VLC player initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize VLC: {e}.")
                self.vlc_available = False
        else:
            logging.error("python-vlc library not found.")

    def play(self, url_string):
        self.stop()

        if self.vlc_available:
            logging.info(f"Playing with VLC: {url_string}")
            media = self.vlc_instance.media_new(url_string)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
        else:
            logging.error("VLC not available, cannot play.")

    def stop(self):
        if self.vlc_available and self.vlc_player.is_playing():
            self.vlc_player.stop()

    def is_playing(self):
        if not self.vlc_available:
            return False
        return self.vlc_player.is_playing()

    def set_volume(self, volume):
        if self.vlc_available:
            self.vlc_player.audio_set_volume(volume)
            
    def get_volume(self):
        if self.vlc_available:
            return self.vlc_player.audio_get_volume()
        return 0

    def toggle_mute(self):
        if self.vlc_available:
            self.vlc_player.audio_toggle_mute()

    def connect_error_handler(self, handler):
        if self.vlc_available:
            event_manager = self.vlc_player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, handler)