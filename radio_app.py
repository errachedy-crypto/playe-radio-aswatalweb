import sys
import logging
import wx

from main_window import RadioWindow

def main():
    """Main function to run the application."""
    logging.basicConfig(filename='radio_app.log', level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    logging.info("Application starting...")

    app = wx.App(False)
    
    window = RadioWindow()
    window.Show()
    
    app.MainLoop()

if __name__ == '__main__':
    main()