import sys
import os
import logging
import wx

from log_formatter import CensoringFormatter
from splash_screen import SplashScreen
from sound_manager import SoundManager

try:
    import vlc
except (ImportError, FileNotFoundError):
    vlc = None

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

    # Create a single VLC instance to be shared across the application
    vlc_instance = None
    if vlc:
        try:
            vlc_instance = vlc.Instance("--no-video --quiet")
            logging.info("Main VLC instance created successfully.")
        except Exception as e:
            logging.error(f"Failed to create main VLC instance: {e}")
    
    # Create a single SoundManager instance
    sound_manager = SoundManager(vlc_instance)

    # Show the splash screen, which will then create the main window
    splash = SplashScreen(vlc_instance, sound_manager)
    splash.Show()
    
    app.MainLoop()

if __name__ == '__main__':
    main()
