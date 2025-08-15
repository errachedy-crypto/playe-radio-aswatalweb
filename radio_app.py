# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QSlider,
                             QLabel, QListWidgetItem, QMessageBox, QLineEdit,
                             QStatusBar)
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData
import urllib.request
from packaging import version
import webbrowser
# --- Configuration ---
CURRENT_VERSION = "1.4"
# URL to a simple JSON file on your GitHub repo containing the latest version info
# Example content for version.json: {"latest_version": "1.1", "download_url": "https://github.com/user/repo/releases/latest"}
UPDATE_URL = "https://raw.githubusercontent.com/errachedy-crypto/playe-radio-aswatalweb/main/version.json"


# Station data provided by the user
STATIONS = [
    ["إذاعة القرآن الكريم من نابلِس", "http://www.quran-radio.org:8002/;stream.mp3"],
    ["إذاعة القرآن الكريم من القاهرة", "http://n0e.radiojar.com/8s5u5tpdtwzuv?rj-ttl=5&rj-tok=AAABeel-l8gApvlPoJcG2WWz8A"],
    ["إذاعة القرآن الكريم من تونس", "http://5.135.194.225:8000/live"],
    ["إذاعة الحرم المكي", "http://r7.tarat.com:8004/;"],
    ["إذاعة دُبَيْ للقرآن الكريم", "http://uk5.internet-radio.com:8079/stream"],
    ["إذاعة قناة المجد", "http://r1.tarat.com:8196/"],
    ["تلاوات خاشعة", "http://live.mp3quran.net:9992/"],
    ["إذاعة القُراء", "http://live.mp3quran.net:8006/"],
    ["إذاعة القرآن الكريم من أستراليا", "http://listen.qkradio.com.au:8382/listen.mp3"],
    ["إذاعة طيبة للقرآن الكريم من السودان", "http://live.mp3quran.net:9960/"],
    ["إذاعة القرآن الكريم من فَلَسطين", "http://streamer.mada.ps:8029/quranfm"],
    ["إذاعة سورة البقرة", "http://live.mp3quran.net:9722/"]
]


class RadioWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"عالم المعرفة راديو v{CURRENT_VERSION}")
        self.setGeometry(100, 100, 400, 500)

        # --- Create Media Player ---
        self.player = QMediaPlayer()
        self.player.metaDataChanged.connect(self.update_now_playing)

        # --- Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Search Bar ---
        search_label = QLabel("ابحث عن إذاعة:")
        main_layout.addWidget(search_label)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("اكتب هنا للبحث...")
        main_layout.addWidget(self.search_bar)
        search_label.setBuddy(self.search_bar)

        # --- Station List ---
        station_label = QLabel("قائمة الإذاعات:")
        main_layout.addWidget(station_label)
        self.station_list = QListWidget()
        self.station_list.setAccessibleName("قائمة محطات الراديو")
        for name, url in STATIONS:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, url)
            self.station_list.addItem(item)
        main_layout.addWidget(self.station_list)
        station_label.setBuddy(self.station_list)

        # --- Control Buttons ---
        button_layout = QHBoxLayout()
        self.play_button = QPushButton("تشغيل")
        self.stop_button = QPushButton("إيقاف")
        self.add_fav_button = QPushButton("إضافة للمفضلة")
        self.rem_fav_button = QPushButton("إزالة من المفضلة")
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.add_fav_button)
        button_layout.addWidget(self.rem_fav_button)
        main_layout.addLayout(button_layout)

        # --- Volume Control ---
        volume_layout = QHBoxLayout()
        volume_label = QLabel("مستوى الصوت:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # --- Now Playing Display ---
        self.now_playing_label = QLabel("التشغيل الحالي: -")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.now_playing_label)

        # --- Status Bar ---
        self.setStatusBar(QStatusBar(self))

        # --- Connect Signals to Slots ---
        self.play_button.clicked.connect(self.play_station)
        self.stop_button.clicked.connect(self.stop_station)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.search_bar.textChanged.connect(self.filter_stations)
        self.add_fav_button.clicked.connect(self.add_favorite)
        self.rem_fav_button.clicked.connect(self.remove_favorite)

        # --- Load Favorites and Set Initial State ---
        self.player.setVolume(self.volume_slider.value())
        self.load_favorites()

        # --- Show Welcome Message ---
        self.statusBar().showMessage("أهلاً بك في راديو عالم المعرفة", 2000) # Show for 2s

        # --- Check for Updates ---
        self.update_checker = UpdateChecker(CURRENT_VERSION, UPDATE_URL)
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.start()

    def show_update_dialog(self, new_version, download_url):
        """
        Displays a message box to the user about the new update.
        """
        title = "تحديث متوفر"
        message = (f"يتوفر تحديث جديد!\n\n"
                   f"الإصدار الحالي: {CURRENT_VERSION}\n"
                   f"الإصدار الجديد: {new_version}\n\n"
                   "هل تريد الذهاب إلى صفحة التنزيل الآن؟")

        reply = QMessageBox.information(self, title, message,
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)

        if reply == QMessageBox.Yes:
            webbrowser.open(download_url)

    def play_station(self):
        current_item = self.station_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد إذاعة أولاً.")
            return
        url_string = current_item.data(Qt.UserRole)
        content = QMediaContent(QUrl(url_string))
        self.player.setMedia(content)
        self.player.play()

    def stop_station(self):
        self.player.stop()

    def update_now_playing(self):
        if self.player.isMetaDataAvailable():
            title = self.player.metaData(QMediaMetaData.Title)
            if title:
                self.now_playing_label.setText(f"التشغيل الحالي: {title}")
            else:
                self.now_playing_label.setText("التشغيل الحالي: -")

    def filter_stations(self):
        search_text = self.search_bar.text().lower()
        for i in range(self.station_list.count()):
            item = self.station_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)

    def add_favorite(self):
        current_item = self.station_list.currentItem()
        if current_item and not current_item.text().startswith("★ "):
            current_item.setText("★ " + current_item.text())
            self.save_favorites()

    def remove_favorite(self):
        current_item = self.station_list.currentItem()
        if current_item and current_item.text().startswith("★ "):
            current_item.setText(current_item.text()[2:])
            self.save_favorites()

    def get_favorites_path(self):
        return os.path.join(os.path.expanduser("~"), "alam_al_maarifa_radio_fav.json")

    def save_favorites(self):
        favorites = []
        for i in range(self.station_list.count()):
            item = self.station_list.item(i)
            if item.text().startswith("★ "):
                favorites.append(item.text()[2:])
        try:
            with open(self.get_favorites_path(), "w", encoding="utf-8") as f:
                json.dump(favorites, f, ensure_ascii=False, indent=4)
        except IOError:
            pass # Ignore save errors for now

    def load_favorites(self):
        path = self.get_favorites_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                favorites = json.load(f)
            for fav_name in favorites:
                for i in range(self.station_list.count()):
                    item = self.station_list.item(i)
                    if item.text() == fav_name:
                        item.setText("★ " + fav_name)
                        break
        except (IOError, json.JSONDecodeError):
            pass # Ignore load errors


class UpdateChecker(QThread):
    """
    A worker thread that checks for updates in the background.
    """
    # Signal to emit when an update is found.
    # It will carry the new version string and the download URL string.
    update_available = pyqtSignal(str, str)

    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url

    def run(self):
        """
        Fetches, parses, and compares version information.
        """
        try:
            with urllib.request.urlopen(self.update_url, timeout=5) as response:
                data = response.read().decode('utf-8')
                version_info = json.loads(data)

                latest_version_str = version_info.get("latest_version")
                download_url = version_info.get("download_url")

                if not latest_version_str or not download_url:
                    return

                # Compare versions using the packaging library
                if version.parse(latest_version_str) > version.parse(self.current_version):
                    self.update_available.emit(latest_version_str, download_url)

        except Exception as e:
            # Silently fail if there's a network error or parsing error.
            # In a real app, this might be logged.
            print(f"Update check failed: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RadioWindow()
    window.show()
    sys.exit(app.exec_())
