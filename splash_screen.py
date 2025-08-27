import wx
from main_window import RadioWindow

class SplashScreen(wx.Frame):
    def __init__(self, vlc_instance, sound_manager):
        # Frameless, borderless, always-on-top window
        super().__init__(None, style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.BORDER_NONE)

        self.vlc_instance = vlc_instance
        self.sound_manager = sound_manager

        self.SetBackgroundColour(wx.Colour(30, 30, 30)) # Dark grey background
        self.Center()

        # Splash screen content
        splash_text = wx.StaticText(self, label="...جاري التشغيل")
        splash_text.SetForegroundColour(wx.Colour(255, 255, 255))
        font = wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        splash_text.SetFont(font)

        # Center the text
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splash_text, 0, wx.ALIGN_CENTER | wx.ALL, 60)
        self.SetSizerAndFit(sizer)

        # Play startup sound
        # We use CallLater to ensure the frame is shown before the sound plays
        wx.CallLater(100, self.sound_manager.play, "startup")

        # Set a timer to close the splash screen and open the main window
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.StartOnce(5000) # 5 seconds as requested

    def on_timer(self, event):
        # Create and show the main window, passing the shared instances
        # This assumes RadioWindow is refactored to accept sound_manager
        main_win = RadioWindow(self.vlc_instance, self.sound_manager)
        main_win.Show()

        # Close the splash screen
        self.Close()
