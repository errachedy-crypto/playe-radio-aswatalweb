import sys
import logging
import wx
import os
import vlc
from sound_manager import SoundManager

from log_formatter import CensoringFormatter
from main_window import RadioWindow

def setup_logging():
    """Configures the logging system manually to use the custom formatter."""
    log_file = 'radio_app.log'
    
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

    try:
        vlc_instance = vlc.Instance()
        sound_manager = SoundManager(vlc_instance)
    except Exception as e:
        logging.critical(f"Failed to initialize VLC or SoundManager: {e}")
        wx.MessageBox(f"فشل تهيئة مكونات الصوت الأساسية (VLC). لا يمكن تشغيل التطبيق.\n\nخطأ: {e}", "خطأ فادح", wx.OK | wx.ICON_ERROR)
        return

    app = wx.App(False)
    
    window = RadioWindow(vlc_instance=vlc_instance, sound_manager=sound_manager)
    window.Show()
    
    app.MainLoop()

if __name__ == '__main__':
    main()
