# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPushButton, QSlider, 
                             QLabel, QListWidgetItem, QMessageBox, QLineEdit,
                             QStatusBar)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

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

        self.setWindowTitle("عالم المعرفة راديو v1.0")
        self.setGeometry(100, 100, 400, 500)

        # --- Create Media Player ---
        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_player_error)

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
        self.play_button.setAccessibleName("تشغيل الراديو")
        self.stop_button = QPushButton("إيقاف")
        self.stop_button.setAccessibleName("إيقاف الراديو")
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        # --- Volume Control ---
        volume_layout = QHBoxLayout()
        volume_label = QLabel("مستوى الصوت:")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setAccessibleName("شريط تمرير مستوى الصوت")
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # --- Connect Signals to Slots ---
        self.play_button.clicked.connect(self.play_station)
        self.stop_button.clicked.connect(self.stop_station)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.search_bar.textChanged.connect(self.filter_stations)

        # --- Set Initial Volume ---
        self.set_volume(self.volume_slider.value())

        # --- Status Bar ---
        self.setStatusBar(QStatusBar(self))

        # --- Show Welcome Message ---
        self.statusBar().showMessage("أهلاً بك في راديو عالم المعرفة", 2000)

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

    def set_volume(self, value):
        self.player.setVolume(value)

    def handle_player_error(self):
        error_string = self.player.errorString()
        if error_string:
            QMessageBox.critical(self, "خطأ في التشغيل", f"حدث خطأ: {error_string}")

    def filter_stations(self):
        """
        Filters the station list based on the text in the search bar.
        """
        search_text = self.search_bar.text().lower()
        for i in range(self.station_list.count()):
            item = self.station_list.item(i)
            item_text = item.text().lower()
            if search_text in item_text:
                item.setHidden(False)
            else:
                item.setHidden(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RadioWindow()
    window.show()
    sys.exit(app.exec_())