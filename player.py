import logging
try:
    import vlc
except (ImportError, FileNotFoundError):
    vlc = None

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class Player:
    def __init__(self):
        self.vlc_instance = None
        self.vlc_player = None
        self.vlc_available = False
        self.q_player = QMediaPlayer()

        self._initialize_vlc()

    def _initialize_vlc(self):
        if vlc:
            try:
                self.vlc_instance = vlc.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
                self.vlc_available = True
                logging.info("VLC player initialized successfully.")
            except Exception as e:
                logging.warning(f"Failed to initialize VLC: {e}. Falling back to QMediaPlayer.")
                self.vlc_available = False
        else:
            logging.warning("python-vlc library not found. Falling back to QMediaPlayer.")

    def play(self, url_string):
        self.stop()

        if self.vlc_available:
            logging.info(f"Playing with VLC: {url_string}")
            media = self.vlc_instance.media_new(url_string)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
        else:
            logging.info(f"Playing with QMediaPlayer: {url_string}")
            media = QMediaContent(QUrl(url_string))
            self.q_player.setMedia(media)
            self.q_player.play()

    def stop(self):
        if self.vlc_available and self.vlc_player.is_playing():
            self.vlc_player.stop()
        if self.q_player.state() == QMediaPlayer.PlayingState:
            self.q_player.stop()

    def is_playing(self):
        vlc_playing = self.vlc_available and self.vlc_player.is_playing()
        qt_playing = self.q_player.state() == QMediaPlayer.PlayingState
        return vlc_playing or qt_playing

    def set_volume(self, volume):
        self.q_player.setVolume(volume)
        if self.vlc_available:
            self.vlc_player.audio_set_volume(volume)
            
    def get_volume(self):
        if self.vlc_available:
            return self.vlc_player.audio_get_volume()
        return self.q_player.volume()

    def toggle_mute(self):
        if self.vlc_available:
            self.vlc_player.audio_toggle_mute()
        else:
            current_mute_status = self.q_player.isMuted()
            self.q_player.setMuted(not current_mute_status)

    def connect_error_handler(self, handler):
        self.q_player.error.connect(handler)