import sys
import os
import json
import webbrowser
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, 
                             QSlider, QLabel, QMessageBox, QStatusBar, QDialog, 
                             QDialogButtonBox, QCheckBox, QRadioButton, QButtonGroup, 
                             QProgressDialog)
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import logging
from packaging import version  # إضافة هذا السطر

try:
    import vlc
except ImportError:
    vlc = None

# إعدادات تسجيل الأخطاء
logging.basicConfig(filename='radio_app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
CURRENT_VERSION = "1.5"
UPDATE_URL = "https://raw.githubusercontent.com/errachedy-crypto/playe-radio-aswatalweb/main/version.json"
STATIONS_URL = "https://aswatalweb.com/radio/radio.json"

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)

    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url
        
    def run(self):
        try:
            logging.debug("Checking for updates...")
            response = requests.get(self.update_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            latest_version_str = data.get("latest_version")
            download_url = data.get("download_url")
            if latest_version_str and download_url and version.parse(latest_version_str) > version.parse(self.current_version):
                self.update_available.emit(latest_version_str, download_url)
            logging.debug(f"Update check completed. Latest version: {latest_version_str}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to check for updates: {e}")
        except json.JSONDecodeError:
            logging.error("Failed to decode update JSON.")

class StationLoader(QThread):
    stationsLoaded = pyqtSignal(list)
    errorOccurred = pyqtSignal(str)

    def run(self):
        try:
            logging.debug("Loading stations from URL...")
            response = requests.get(STATIONS_URL, timeout=10)
            response.raise_for_status()
            data = response.text
            categories = json.loads(data).get("categories", [])
            logging.debug(f"Categories loaded: {categories}")
            self.stationsLoaded.emit(categories)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to load stations from network: {e}")
            self.errorOccurred.emit(f"غير قادر على تحميل قائمة الإذاعات:\n{e}")
        except json.JSONDecodeError:
            logging.error("Failed to decode stations JSON.")
            self.errorOccurred.emit("فشل في قراءة بيانات الإذاعات.")

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

        # --- Font Size Setting ---
        self.font_size_checkbox = QCheckBox("استخدام خط كبير")
        self.font_size_checkbox.setChecked(self.settings.get("large_font", False))
        self.layout.addWidget(self.font_size_checkbox)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.save_and_accept)
        self.buttons.rejected.connect(self.reject)

    def save_and_accept(self):
        # Save the state of the widgets back to the settings dictionary
        self.settings["check_for_updates"] = self.update_checkbox.isChecked()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.isChecked()
        self.settings["theme"] = "dark" if self.dark_theme_radio.isChecked() else "light"
        self.settings["large_font"] = self.font_size_checkbox.isChecked()
        self.accept()

class RadioWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initialize_vlc()
        self.settings = self.load_settings()  # Load settings here
        self.apply_theme()  # Apply theme at startup

        self.setWindowTitle(f"الراديو العربي STV v{CURRENT_VERSION}")
        self.setGeometry(100, 100, 400, 500)

        # Initialize QMediaPlayer for regular audio
        self.player = QMediaPlayer()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.setup_ui(main_layout)
        self.setup_menu()
        self.connect_signals()
        
        # Use a timer to defer loading and network tasks
        QTimer.singleShot(100, self.finish_setup)

    def initialize_vlc(self):
        self.vlc_instance = None
        self.vlc_player = None
        self.vlc_available = False
        if vlc:
            try:
                # Attempt to create a VLC instance
                self.vlc_instance = vlc.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
                self.vlc_available = True
                logging.info("VLC player initialized successfully.")
            except Exception as e:
                logging.warning(f"Failed to initialize VLC: {e}. Falling back to QMediaPlayer.")
                self.vlc_available = False
        else:
            logging.warning("python-vlc library not found. Falling back to QMediaPlayer.")

    def finish_setup(self):
        try:
            logging.debug("Starting setup tasks...")
            self.load_stations()  # Ensure stations are loaded here
            self.check_for_updates()
            self.statusBar().showMessage("أهلاً بك في الراديو العربي STV", 2000)
            self.play_last_station_if_enabled()  # Ensure this function is defined
            logging.debug("Setup tasks completed successfully.")
        except Exception as e:
            logging.error(f"Error during setup: {e}")
            QMessageBox.critical(self, "خطأ في التهيئة", f"حدث خطأ أثناء تهيئة التطبيق:\n{e}")

    def load_settings(self):
        # التأكد من تحميل الإعدادات بشكل صحيح
        path = self.get_settings_path()
        defaults = {
            "check_for_updates": True,
            "play_on_startup": False,
            "theme": "light",
            "large_font": False
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

    def play_last_station_if_enabled(self):
        # هذه الدالة ستقوم بتشغيل آخر إذاعة تم الاستماع إليها إذا كانت الإعدادات مفعلة
        if self.settings.get("play_on_startup", False):
            last_station_name = self.settings.get("last_station_name")
            if not last_station_name:
                return

            root = self.tree_widget.invisibleRootItem()
            for i in range(root.childCount()):
                category = root.child(i)
                for j in range(category.childCount()):
                    station = category.child(j)
                    if station.text(0).strip() == last_station_name:
                        self.tree_widget.setCurrentItem(station)
                        self.play_station(station)  # Ensure play_station is called correctly
                        return

    def play_station(self, item=None, column=None):
        if not item:
            item = self.tree_widget.currentItem()

        if not item or not item.data(0, Qt.UserRole):
            return

        station_name = item.text(0).strip()
        url_string = item.data(0, Qt.UserRole)

        self.settings["last_station_name"] = station_name
        self.save_settings()

        self.stop_station() # Stop any playing stream first

        if self.vlc_available:
            logging.info(f"Playing with VLC: {url_string}")
            media = self.vlc_instance.media_new(url_string)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
        else:
            logging.info(f"Playing with QMediaPlayer: {url_string}")
            # Use QMediaPlayer for all audio files (mp3, m3u8, etc.)
            media = QMediaContent(QUrl(url_string))
            self.player.setMedia(media)
            self.player.play()

    def stop_station(self):
        if self.vlc_available and self.vlc_player.is_playing():
            self.vlc_player.stop()
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()

    def adjust_volume(self):
        volume = self.volume_slider.value()
        self.player.setVolume(volume)
        if self.vlc_available:
            self.vlc_player.audio_set_volume(volume)

    def setup_ui(self, main_layout):
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        main_layout.addWidget(self.tree_widget)

        button_layout = QHBoxLayout()
        self.play_button = QPushButton("تشغيل")
        self.stop_button = QPushButton("إيقاف")
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
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

    def load_stations(self):
        self.progress_dialog = QProgressDialog("جاري التحميل ... يرجى الانتظار.", None, 0, 0, self)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        self.station_loader = StationLoader()
        self.station_loader.stationsLoaded.connect(self.on_stations_loaded)
        self.station_loader.errorOccurred.connect(self.on_stations_load_error)
        self.station_loader.start()

    def on_stations_loaded(self, categories):
        self.progress_dialog.close()
        self.populate_stations(categories)

    def on_stations_load_error(self, error_message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "خطأ في تحميل الإذاعات", error_message)

    def populate_stations(self, categories):
        for category in categories:
            parent = QTreeWidgetItem(self.tree_widget)
            parent.setText(0, category["name"])
            parent.setFlags(parent.flags() & ~Qt.ItemIsSelectable)
            for station in category.get("stations", []):
                child = QTreeWidgetItem(parent)
                child.setText(0, station["name"])
                child.setData(0, Qt.UserRole, station["url"])

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
        <b>الراديو العربي STV</b><br>
        الإصدار: {CURRENT_VERSION}<br>
        المطور: errachedy<br><br>
        تطبيق بسيط للاستماع إلى الإذاعات العربية.
        """
        QMessageBox.about(self, "حول البرنامج", about_text)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            self.settings = dialog.settings
            self.save_settings()
            self.apply_theme()

    def connect_signals(self):
        self.play_button.clicked.connect(self.play_station)
        self.stop_button.clicked.connect(self.stop_station)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        self.tree_widget.itemActivated.connect(self.play_station)

    def check_for_updates(self):
        if self.settings.get("check_for_updates", True):
            self.update_checker = UpdateChecker(CURRENT_VERSION, UPDATE_URL)
            self.update_checker.update_available.connect(self.show_update_dialog)
            self.update_checker.start()

    def show_update_dialog(self, new_version, download_url):
        message = (f"يتوفر تحديث جديد!\n\n"
                   f"الإصدار الحالي: {CURRENT_VERSION}\n"
                   f"الإصدار الجديد: {new_version}\n\n"
                   "هل تريد الذهاب إلى صفحة التنزيل الآن؟")
        reply = QMessageBox.information(self, "تحديث متوفر", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(download_url)

    def handle_player_error(self, error):
        error_string = self.player.errorString()
        if error_string:
            logging.error(f"Player error: {error_string}")
            QMessageBox.critical(self, "خطأ في التشغيل", f"حدث خطأ أثناء محاولة تشغيل الإذاعة:\n{error_string}")
        self.stop_station()

    def save_settings(self):
        try:
            with open(self.get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def get_settings_path(self):
        return os.path.join(os.path.expanduser("~"), "stv_radio_settings.json")

    def apply_theme(self):
        font = self.font()
        if self.settings.get("large_font", False):
            font.setPointSize(14)
        else:
            font.setPointSize(10)
        self.setFont(font)

        dark_stylesheet = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTreeWidget {
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RadioWindow()
    window.show()
    sys.exit(app.exec_())
