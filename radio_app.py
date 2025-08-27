import sys
import os
import logging
import wx

from log_formatter import CensoringFormatter
from main_window import RadioWindow

def setup_logging():
    """Configures the logging system manually to use the custom formatter."""
    log_file = 'radio_app.log'
    
    # Clean up old log file on every startup
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except OSError as e:
            print(f"Error removing log file {log_file}: {e}", file=sys.stderr)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = CensoringFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

def main():
    """Main function to run the application."""
    setup_logging()
    
    logging.info("Application starting...")

    app = wx.App(False)
    
    window = RadioWindow()
    window.Show()
    
    app.MainLoop()

if __name__ == '__main__':
    main()
