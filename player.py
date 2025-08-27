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
        self.is_recording_flag = False
        self.current_url = None

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
        self.current_url = url_string

        if self.vlc_available:
            logging.info(f"Playing with VLC: {self.current_url}")
            media = self.vlc_instance.media_new(self.current_url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
        else:
            logging.error("VLC not available, cannot play.")

    def start_recording(self, filename):
        if not self.vlc_available or not self.current_url:
            logging.error("Cannot start recording: player not ready or no station selected.")
            return False

        self.stop()
        self.is_recording_flag = True

        # Note: The muxer (e.g., mp3, wav, ts) can be important.
        # Using 'ts' for transport stream is often a safe bet for various stream types.
        sout_string = f'#duplicate{{dst=display,dst=std{{access=file,mux=ts,dst="{filename}"}}}}'

        media = self.vlc_instance.media_new(self.current_url, f':sout={sout_string}')

        self.vlc_player.set_media(media)
        self.vlc_player.play()
        logging.info(f"Started recording stream from {self.current_url} to {filename}")
        return True

    def stop_recording(self):
        self.stop()

    def stop(self):
        if self.vlc_available and self.vlc_player.is_playing():
            self.vlc_player.stop()
        self.is_recording_flag = False
        # Don't clear current_url, so we can resume playback easily

    def is_playing(self):
        if not self.vlc_available:
            return False
        return self.vlc_player.is_playing()

    def is_recording(self):
        return self.is_recording_flag

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