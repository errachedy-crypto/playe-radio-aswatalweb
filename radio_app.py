import sys
import logging
import os
from PyQt5.QtWidgets import QApplication

from log_filter import URLFilter
from main_window import RadioWindow

def main():
    """Main function to run the application."""
    log_file = 'radio_app.log'
    
    # Clean up old log file on every startup
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except OSError as e:
            # If deletion fails, print error to stderr, as logging is not yet configured.
            print(f"Error removing log file {log_file}: {e}", file=sys.stderr)

    logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Add the custom filter to the root logger to censor URLs
    logging.getLogger().addFilter(URLFilter())

    logging.info("Application starting...")

    app = QApplication(sys.argv)
    
    window = RadioWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()