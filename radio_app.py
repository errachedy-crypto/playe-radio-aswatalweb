import sys
import logging
from PyQt5.QtWidgets import QApplication

from main_window import RadioWindow

def main():
    """Main function to run the application."""
    logging.basicConfig(filename='radio_app.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Application starting...")

    app = QApplication(sys.argv)

    window = RadioWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
