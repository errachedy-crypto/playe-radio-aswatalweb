import logging
try:
    import vlc
except (ImportError, FileNotFoundError):
    vlc = None

class Player:
    def __init__(self, vlc_instance):
        if not vlc:
            raise ImportError("python-vlc library not found.")
        if not isinstance(vlc_instance, vlc.Instance):
            raise TypeError("A valid vlc.Instance must be provided.")

        self.vlc_instance = vlc_instance
        self.vlc_player = self.vlc_instance.media_player_new()
        self.current_url = None
        self.is_rec = False

    def play(self, url_string):
        self.current_url = url_string
        logging.info(f"Playing with VLC: {url_string}")
        media = self.vlc_instance.media_new(url_string)
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def stop(self):
        if self.vlc_player.is_playing():
            self.vlc_player.stop()
            self.current_url = None

    def is_playing(self):
        return self.vlc_player.is_playing()

    def set_volume(self, volume):
        self.vlc_player.audio_set_volume(volume)

    def get_volume(self):
        return self.vlc_player.audio_get_volume()

    def toggle_mute(self):
        self.vlc_player.audio_toggle_mute()

    def start_recording(self, output_path):
        if not self.current_url:
            logging.error("Cannot record: no stream is currently playing.")
            return False

        sout_options = f'#transcode{{acodec=mp3,ab=128}}:std{{access=file,mux=ts,dst="{output_path}"}}'

        media = self.vlc_instance.media_new(self.current_url, f'sout={sout_options}', 'sout-keep')

        self.vlc_player.set_media(media)
        self.vlc_player.play()
        self.is_rec = True
        logging.info(f"Started recording to {output_path}")
        return True

    def stop_recording(self):
        self.stop()
        self.is_rec = False
        logging.info("Stopped recording.")

    def is_recording(self):
        return self.is_rec

    def connect_error_handler(self, handler):
        event_manager = self.vlc_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError, handler)