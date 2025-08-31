import wx

class SplashScreen(wx.SplashScreen):
    def __init__(self, version):
        # Create a bitmap dynamically
        width, height = 400, 200
        bitmap = wx.Bitmap(width, height)

        # Draw on the bitmap
        dc = wx.MemoryDC(bitmap)
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()

        # Draw title
        font_title = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font_title)
        dc.SetTextForeground(wx.Colour("#4A90E2")) # Using a color from the "Modern Mode" theme
        dc.DrawText("Amwaj Radio", 100, 60)

        # Draw version
        font_version = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(font_version)
        dc.SetTextForeground(wx.BLACK)
        dc.DrawText(f"Version {version}", 160, 110)

        del dc # End drawing

        super().__init__(bitmap,
                         wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                         3000, None, -1, style=wx.SIMPLE_BORDER | wx.STAY_ON_TOP)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        # Prevent the user from closing the splash screen
        event.Veto()
