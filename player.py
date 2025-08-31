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
        self.current_url = None
        self.is_rec = False

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
            self.current_url = url_string
            logging.info(f"Playing with VLC: {url_string}")
            media = self.vlc_instance.media_new(url_string)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
        else:
            logging.error("VLC not available, cannot play.")

    def stop(self):
        if self.vlc_available and self.vlc_player.is_playing():
            self.vlc_player.stop()
            self.current_url = None

    def is_playing(self):
        if not self.vlc_available:
            return False
        return self.vlc_player.is_playing()

    def start_recording(self, output_path):
        if not self.current_url or not self.vlc_available:
            logging.error("Cannot record: no stream is currently playing or VLC not available.")
            return False

        sout_options = f'#transcode{{acodec=mp3,ab=128}}:std{{access=file,mux=ts,dst="{output_path}"}}'
        media = self.vlc_instance.media_new(self.current_url, f'sout={sout_options}', 'sout-keep')

        # Create a new player instance for recording to not interfere with the main player
        recorder_player = self.vlc_instance.media_player_new()
        recorder_player.set_media(media)
        recorder_player.play()

        self.is_rec = True
        self.recorder_player = recorder_player # Store the recorder player instance
        logging.info(f"Started recording to {output_path}")
        return True

    def stop_recording(self):
        if hasattr(self, 'recorder_player') and self.recorder_player.is_playing():
            self.recorder_player.stop()
        self.is_rec = False
        logging.info("Stopped recording.")

    def is_recording(self):
        return self.is_rec

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