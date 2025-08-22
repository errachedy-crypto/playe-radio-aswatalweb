from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QCheckBox, QRadioButton, QButtonGroup, 
                             QDialogButtonBox, QLabel)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.settings = settings.copy()
        self.layout = QVBoxLayout(self)
        
        self.update_checkbox = QCheckBox("التحقق من وجود تحديثات عند بدء التشغيل")
        self.update_checkbox.setChecked(self.settings.get("check_for_updates", True))
        self.layout.addWidget(self.update_checkbox)

        self.play_on_startup_checkbox = QCheckBox("تشغيل آخر إذاعة تم الاستماع إليها عند بدء التشغيل")
        self.play_on_startup_checkbox.setChecked(self.settings.get("play_on_startup", False))
        self.layout.addWidget(self.play_on_startup_checkbox)

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

        self.font_size_checkbox = QCheckBox("استخدام خط كبير")
        self.font_size_checkbox.setChecked(self.settings.get("large_font", False))
        self.layout.addWidget(self.font_size_checkbox)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.save_and_accept)
        self.buttons.rejected.connect(self.reject)

    def save_and_accept(self):
        self.settings["check_for_updates"] = self.update_checkbox.isChecked()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.isChecked()
        self.settings["theme"] = "dark" if self.dark_theme_radio.isChecked() else "light"
        self.settings["large_font"] = self.font_size_checkbox.isChecked()
        self.accept()

    def get_settings(self):
        return self.settings