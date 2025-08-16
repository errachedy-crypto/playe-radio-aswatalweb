# -*- coding: utf-8 -*-

import sys
import os
import json
import webbrowser
from packaging import version
import urllib.request
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QSlider,
                             QLabel, QListWidgetItem, QMessageBox, QLineEdit,
                             QStatusBar, QDialog, QDialogButtonBox, QCheckBox,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData

# --- Configuration ---
CURRENT_VERSION = "2.0"
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

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)
    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url
    def run(self):
        try:
            with urllib.request.urlopen(self.update_url, timeout=5) as response:
                data = response.read().decode('utf-8')
                version_info = json.loads(data)
                latest_version_str = version_info.get("latest_version")
                download_url = version_info.get("download_url")
                if latest_version_str and download_url and version.parse(latest_version_str) > version.parse(self.current_version):
                    self.update_available.emit(latest_version_str, download_url)
        except Exception:
            pass

class FavoritesLoader(QThread):
    favoritesLoaded = pyqtSignal(list)
    def __init__(self, path):
        super().__init__()
        self.path = path
    def run(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                favorites = json.load(f)
                self.favoritesLoaded.emit(favorites)
        except (IOError, json.JSONDecodeError):
            pass

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.settings = settings
        self.layout = QVBoxLayout(self)

        # --- Update Check Setting ---
        self.update_checkbox = QCheckBox("التحقق من وجود تحديثات عند بدء التشغيل")
        self.update_checkbox.setChecked(self.settings.get("check_for_updates", True))
        self.layout.addWidget(self.update_checkbox)

        # --- Play on Startup Setting ---
        self.play_on_startup_checkbox = QCheckBox("تشغيل آخر إذاعة تم الاستماع إليها عند بدء التشغيل")
        self.play_on_startup_checkbox.setChecked(self.settings.get("play_on_startup", False))
        self.layout.addWidget(self.play_on_startup_checkbox)

        # --- Theme Setting ---
        theme_label = QLabel("سمة التطبيق:")
        self.layout.addWidget(theme_label)
        self.light_theme_radio = QRadioButton("فاتح")
        self.dark_theme_radio = QRadioButton("داكن")
        self.theme_button_group = QButtonGroup()
        self.theme_button_group.addButton(self.light_theme_radio)
        self.theme_button_group.addButton(self.dark_theme_radio)
        if self.settings.get("theme", "light") == "dark":
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        self.layout.addLayout(theme_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.save_and_accept)
        self.buttons.rejected.connect(self.reject)

    def save_and_accept(self):
        # Save the state of the widgets back to the settings dictionary
        self.settings["check_for_updates"] = self.update_checkbox.isChecked()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.isChecked()
        self.settings["theme"] = "dark" if self.dark_theme_radio.isChecked() else "light"
        self.accept()

class RadioWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = self.load_settings()
        self.apply_theme() # Apply theme at startup

        self.setWindowTitle(f"عالم المعرفة راديو v{CURRENT_VERSION}")
        self.setGeometry(100, 100, 400, 500)
        self.player = QMediaPlayer()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.setup_ui(main_layout)
        self.setup_menu()
        self.connect_signals()
        self.player.setVolume(self.volume_slider.value())

        # Use a timer to defer loading and network tasks
        QTimer.singleShot(100, self.finish_setup)

    def finish_setup(self):
        """
        Run startup tasks that might block, after the main window is shown.
        """
        self.load_favorites_in_background()
        self.check_for_updates()
        self.statusBar().showMessage("أهلاً بك في راديو عالم المعرفة", 2000)
        self.play_last_station_if_enabled()

    def setup_ui(self, main_layout):
        search_label = QLabel("ابحث عن إذاعة:")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("اكتب هنا للبحث...")
        main_layout.addWidget(search_label)
        main_layout.addWidget(self.search_bar)

        station_label = QLabel("قائمة الإذاعات:")
        main_layout.addWidget(station_label)
        self.station_list = QListWidget()
        for name, url in STATIONS:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, url)
            self.station_list.addItem(item)
        main_layout.addWidget(self.station_list)

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

        volume_layout = QHBoxLayout()
        volume_label = QLabel("مستوى الصوت:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        self.now_playing_label = QLabel("التشغيل الحالي: -")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.now_playing_label)
        self.setStatusBar(QStatusBar(self))

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&ملف")

        settings_action = file_menu.addAction("الإعدادات...")
        settings_action.triggered.connect(self.open_settings_dialog)

        about_action = file_menu.addAction("حول البرنامج...")
        about_action.triggered.connect(self.show_about_dialog)

        file_menu.addSeparator()
        exit_action = file_menu.addAction("خروج")
        exit_action.triggered.connect(self.close)

    def show_about_dialog(self):
        about_text = f"""
        <b>عالم المعرفة راديو</b><br>
        الإصدار: {CURRENT_VERSION}<br>
        المطور: errachedy<br><br>
        تطبيق بسيط للاستماع إلى إذاعات القرآن الكريم.
        """
        QMessageBox.about(self, "حول البرنامج", about_text)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            self.settings = dialog.settings
            self.save_settings()
            self.apply_theme() # Apply theme immediately after settings change

    def connect_signals(self):
        self.player.metaDataChanged.connect(self.update_now_playing)
        self.player.error.connect(self.handle_player_error)
        self.play_button.clicked.connect(self.play_station)
        self.stop_button.clicked.connect(self.stop_station)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.search_bar.textChanged.connect(self.filter_stations)
        self.add_fav_button.clicked.connect(self.add_favorite)
        self.rem_fav_button.clicked.connect(self.remove_favorite)
        self.station_list.itemActivated.connect(self.play_station)

    def check_for_updates(self):
        if self.settings.get("check_for_updates", True):
            self.update_checker = UpdateChecker(CURRENT_VERSION, UPDATE_URL)
            self.update_checker.update_available.connect(self.show_update_dialog)
            self.update_checker.start()

    def show_update_dialog(self, new_version, download_url):
        message = (f"يتوفر تحديث جديد!\\n\\n"
                   f"الإصدار الحالي: {CURRENT_VERSION}\\n"
                   f"الإصدار الجديد: {new_version}\\n\\n"
                   "هل تريد الذهاب إلى صفحة التنزيل الآن؟")
        reply = QMessageBox.information(self, "تحديث متوفر", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(download_url)

    def handle_player_error(self, error):
        error_string = self.player.errorString()
        if error_string:
            QMessageBox.critical(self, "خطأ في التشغيل", f"حدث خطأ أثناء محاولة تشغيل الإذاعة:\n{error_string}")
        # Stop the player and reset the label
        self.stop_station()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            self.toggle_play_stop()
        else:
            super().keyPressEvent(event)

    def toggle_play_stop(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.stop_station()
        else:
            self.play_station()

    def play_station(self, item=None):
        if isinstance(item, QListWidgetItem):
             current_item = item
        else:
             current_item = self.station_list.currentItem()

        if not current_item:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد إذاعة أولاً.")
            return

        # Save the last played station
        station_name = current_item.text().lstrip("★ ")
        self.settings["last_station_name"] = station_name
        self.save_settings()

        url_string = current_item.data(Qt.UserRole)
        self.player.setMedia(QMediaContent(QUrl(url_string)))
        self.player.play()

    def stop_station(self):
        self.player.stop()

    def update_now_playing(self):
        if self.player.isMetaDataAvailable():
            title = self.player.metaData(QMediaMetaData.Title)
            self.now_playing_label.setText(f"التشغيل الحالي: {title or '-'}")

    def filter_stations(self):
        search_text = self.search_bar.text().lower()
        for i in range(self.station_list.count()):
            item = self.station_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def add_favorite(self):
        item = self.station_list.currentItem()
        if item and not item.text().startswith("★ "):
            item.setText("★ " + item.text())
            self.save_favorites()

    def remove_favorite(self):
        item = self.station_list.currentItem()
        if item and item.text().startswith("★ "):
            item.setText(item.text()[2:])
            self.save_favorites()

    def get_favorites_path(self):
        return os.path.join(os.path.expanduser("~"), "alam_al_maarifa_radio_fav.json")

    def get_settings_path(self):
        return os.path.join(os.path.expanduser("~"), "radio_app_settings.json")

    def save_settings(self):
        try:
            with open(self.get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def play_last_station_if_enabled(self):
        if self.settings.get("play_on_startup", False):
            last_station_name = self.settings.get("last_station_name")
            if not last_station_name:
                return

            for i in range(self.station_list.count()):
                item = self.station_list.item(i)
                if item.text().lstrip("★ ") == last_station_name:
                    self.station_list.setCurrentItem(item)
                    self.play_station()
                    break

    def load_settings(self):
        path = self.get_settings_path()
        defaults = {
            "check_for_updates": True,
            "play_on_startup": False,
            "theme": "light"
        }
        if not os.path.exists(path):
            return defaults
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            for key, value in defaults.items():
                settings.setdefault(key, value)
            return settings
        except (IOError, json.JSONDecodeError):
            return defaults

    def apply_theme(self):
        dark_stylesheet = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #777;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 3px;
            }
            QMenuBar, QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #555;
            }
        """
        if self.settings.get("theme", "light") == "dark":
            self.setStyleSheet(dark_stylesheet)
        else:
            self.setStyleSheet("")

    def save_favorites(self):
        favorites = [self.station_list.item(i).text()[2:] for i in range(self.station_list.count()) if self.station_list.item(i).text().startswith("★ ")]
        try:
            with open(self.get_favorites_path(), "w", encoding="utf-8") as f:
                json.dump(favorites, f, ensure_ascii=False, indent=4)
        except IOError: pass

    def load_favorites_in_background(self):
        self.favorites_loader = FavoritesLoader(self.get_favorites_path())
        self.favorites_loader.favoritesLoaded.connect(self.apply_loaded_favorites)
        self.favorites_loader.start()

    def apply_loaded_favorites(self, favorites):
        for fav_name in favorites:
            for i in range(self.station_list.count()):
                item = self.station_list.item(i)
                if item.text() == fav_name:
                    item.setText("★ " + fav_name)
                    break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RadioWindow()
    window.show()
    sys.exit(app.exec_())
