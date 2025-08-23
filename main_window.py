import logging
import webbrowser
import os

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QPushButton, QSlider, 
                             QLabel, QMessageBox, QStatusBar, QProgressDialog, 
                             QLineEdit, QShortcut)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

from constants import CURRENT_VERSION, UPDATE_URL
from settings import load_settings, save_settings
from threads import UpdateChecker, StationLoader
from player import Player
from settings_dialog import SettingsDialog
from help_dialog import HelpDialog

class RadioWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.player = Player()

        self.setWindowTitle(f"Amwaj v{CURRENT_VERSION}")
        self.setGeometry(100, 100, 400, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.setup_ui()
        self.setup_menu()
        self.connect_signals()
        
        self.volume_slider.setValue(self.settings.get("volume", 40))
        self.adjust_volume()

        self.apply_theme()

        QTimer.singleShot(100, self.finish_setup)
        self.setup_shortcuts()

    def finish_setup(self):
        try:
            logging.debug("Starting setup tasks...")
            self.load_stations()
            if self.settings.get("check_for_updates", True):
                self.check_for_updates()
            self.statusBar().showMessage("أهلاً بك في الراديو العربي STV", 2000)
            if self.settings.get("play_on_startup", False):
                self.play_last_station()
            logging.debug("Setup tasks completed successfully.")
        except Exception as e:
            logging.error(f"Error during setup: {e}")
            QMessageBox.critical(self, "خطأ في التهيئة", f"حدث خطأ أثناء تهيئة التطبيق:\\n{e}")

    def setup_ui(self):
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.main_layout.addWidget(self.tree_widget)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("ابحث عن إذاعة...")
        self.main_layout.addWidget(self.search_box)

        button_layout = QHBoxLayout()
        self.play_stop_button = QPushButton("تشغيل")
        button_layout.addWidget(self.play_stop_button)
        self.main_layout.addLayout(button_layout)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("مستوى الصوت:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        self.main_layout.addLayout(volume_layout)

        settings_button = QPushButton("الإعدادات")
        settings_button.clicked.connect(self.open_settings_dialog)
        self.main_layout.addWidget(settings_button)

        self.now_playing_label = QLabel("التشغيل الحالي: -")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.now_playing_label)

        self.setStatusBar(QStatusBar(self))

    def connect_signals(self):
        self.play_stop_button.clicked.connect(self.toggle_play_stop)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        self.tree_widget.itemDoubleClicked.connect(self.play_station)
        self.search_box.textChanged.connect(self.filter_stations)
        self.player.connect_error_handler(self.handle_player_error)

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

        help_menu = menu_bar.addMenu("&المساعدة")
        help_action = help_menu.addAction("عرض دليل المساعدة")
        help_action.triggered.connect(self.show_help_dialog)

    def setup_shortcuts(self):
        shortcut_f3 = QShortcut(QKeySequence(Qt.Key_F3), self)
        shortcut_f3.activated.connect(self.search_box.setFocus)
        shortcut_f7 = QShortcut(QKeySequence(Qt.Key_F7), self)
        shortcut_f7.activated.connect(self.lower_volume)
        shortcut_f8 = QShortcut(QKeySequence(Qt.Key_F8), self)
        shortcut_f8.activated.connect(self.raise_volume)
        shortcut_f9 = QShortcut(QKeySequence(Qt.Key_F9), self)
        shortcut_f9.activated.connect(self.toggle_mute)
        shortcut_f5 = QShortcut(QKeySequence(Qt.Key_F5), self)
        shortcut_f5.activated.connect(self.restart_station)
        shortcut_f2 = QShortcut(QKeySequence(Qt.Key_F2), self)
        shortcut_f2.activated.connect(self.toggle_play_stop)

    def play_station(self, item=None, column=None):
        if not item:
            item = self.tree_widget.currentItem()
        if not item or not item.data(0, Qt.UserRole):
            return

        station_name = item.text(0).strip()
        url_string = item.data(0, Qt.UserRole)

        self.settings["last_station_name"] = station_name
        self.player.play(url_string)
        self.now_playing_label.setText(f"التشغيل الحالي: {station_name}")
        self.play_stop_button.setText('إيقاف')

    def stop_station(self):
        self.player.stop()
        self.now_playing_label.setText("التشغيل الحالي: -")
        self.play_stop_button.setText('تشغيل')

    def toggle_play_stop(self):
        if self.player.is_playing():
            self.stop_station()
        else:
            current_item = self.tree_widget.currentItem()
            if current_item and current_item.data(0, Qt.UserRole):
                self.play_station(current_item)
            else:
                self.play_last_station()

    def adjust_volume(self):
        volume = self.volume_slider.value()
        self.player.set_volume(volume)
        self.settings["volume"] = volume

    def lower_volume(self):
        self.volume_slider.setValue(max(self.volume_slider.value() - 10, 0))

    def raise_volume(self):
        self.volume_slider.setValue(min(self.volume_slider.value() + 10, 100))

    def toggle_mute(self):
        self.player.toggle_mute()

    def restart_station(self):
        self.play_station()

    def play_last_station(self):
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
                    self.play_station(station)
                    return

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
        self.play_last_station_if_enabled()

    def on_stations_load_error(self, error_message, is_critical):
        self.progress_dialog.close()
        if is_critical:
            QMessageBox.critical(self, "خطأ فادح", error_message)
        else:
            self.statusBar().showMessage(error_message, 10000)

    def populate_stations(self, categories):
        self.tree_widget.clear()
        for category in categories:
            parent = QTreeWidgetItem(self.tree_widget)
            parent.setText(0, category["name"])
            parent.setFlags(parent.flags() & ~Qt.ItemIsSelectable)
            for station in category.get("stations", []):
                child = QTreeWidgetItem(parent)
                child.setText(0, station["name"])
                child.setData(0, Qt.UserRole, station["url"])
        self.tree_widget.expandAll()

    def play_last_station_if_enabled(self):
        if self.settings.get("play_on_startup", False):
            self.play_last_station()

    def filter_stations(self):
        search_text = self.search_box.text().lower()
        root = self.tree_widget.invisibleRootItem()

        for i in range(root.childCount()):
            category = root.child(i)
            category_has_matches = False
            for j in range(category.childCount()):
                station = category.child(j)
                station_matches = search_text in station.text(0).lower()
                station.setHidden(not station_matches)
                if station_matches:
                    category_has_matches = True
            
            category.setHidden(not category_has_matches)
            category.setExpanded(category_has_matches)

    def check_for_updates(self):
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

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            new_settings = dialog.get_settings()
            theme_changed = self.settings.get("theme") != new_settings.get("theme")
            font_changed = self.settings.get("large_font") != new_settings.get("large_font")

            self.settings = new_settings
            save_settings(self.settings)
            self.apply_theme()
            
            if theme_changed or font_changed:
                QMessageBox.information(self, "الإعدادات", "بعض الإعدادات تتطلب إعادة تشغيل التطبيق لتصبح سارية المفعول.")

    def show_about_dialog(self):
        about_text = f"""
        <b>Amwaj</b><br>
        الإصدار: {CURRENT_VERSION}<br>
        المطور: errachedy<br><br>
        الميزات الجديدة: استماع إلى الإذاعات العربية.
        """
        QMessageBox.about(self, "حول البرنامج", about_text)

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

    def handle_player_error(self, error):
        error_string = self.player.q_player.errorString()
        if error_string:
            logging.error(f"Player error: {error_string}")
            QMessageBox.critical(self, "خطأ في التشغيل", f"حدث خطأ أثناء محاولة تشغيل الإذاعة:\\n{error_string}")
        self.stop_station()

    def show_help_dialog(self):
        try:
            help_file_path = 'HELP.md'
            if not os.path.exists(help_file_path):
                QMessageBox.warning(self, "خطأ", "ملف المساعدة 'HELP.md' غير موجود.")
                return

            with open(help_file_path, "r", encoding="utf-8") as f:
                help_content = f.read()
            
            self.help_dialog = HelpDialog(help_content, self)
            self.help_dialog.show()
        except Exception as e:
            logging.error(f"Could not show help dialog: {e}")
            QMessageBox.critical(self, "خطأ", f"لا يمكن عرض ملف المساعدة: {e}")

    def closeEvent(self, event):
        save_settings(self.settings)
        super().closeEvent(event)