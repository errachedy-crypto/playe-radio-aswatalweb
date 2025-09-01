import sys
import os
import logging
import wx
import vlc

from log_formatter import CensoringFormatter
from main_window import RadioWindow
from sound_manager import SoundManager
from screen_reader_bridge import ScreenReaderBridge
from splash_screen import SplashScreen
from constants import CURRENT_VERSION

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

    # Show splash screen
    splash = SplashScreen()
    splash.Show()
    wx.Yield() # Ensure splash screen is painted

    # Initialize components
    try:
        vlc_instance = vlc.Instance()
        sound_manager = SoundManager()
        screen_reader = ScreenReaderBridge()
        # Use sound manager for startup sound, not TTS
        sound_manager.play("startup")
    except Exception as e:
        logging.critical(f"Failed to initialize components: {e}")
        wx.MessageBox(f"فشل تهيئة المكونات الأساسية. لا يمكن تشغيل التطبيق.\n\nخطأ: {e}", "خطأ فادح", wx.OK | wx.ICON_ERROR)
        return

    # Wait for splash screen to finish
    wx.Sleep(3)
    splash.Destroy()

    # Create and show the main window
    window = RadioWindow(vlc_instance=vlc_instance, sound_manager=sound_manager, screen_reader=screen_reader)
    window.Show()
    
    app.MainLoop()

if __name__ == '__main__':
    main()
