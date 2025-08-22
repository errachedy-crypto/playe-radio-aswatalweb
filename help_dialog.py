from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, help_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("دليل المساعدة")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setMarkdown(help_content)
        
        self.layout.addWidget(self.text_browser)
        self.setLayout(self.layout)