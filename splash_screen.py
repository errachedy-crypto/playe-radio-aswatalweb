import wx
from wx.adv import SplashScreen

class SplashScreen(SplashScreen):
    def __init__(self):
        # Create a bitmap dynamically
        width, height = 400, 100
        bitmap = wx.Bitmap(width, height)

        # Draw on the bitmap
        dc = wx.MemoryDC(bitmap)
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()

        # Draw title
        font_title = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font_title)
        dc.SetTextForeground(wx.Colour("#4A90E2"))

        text = "جاري التحميل ..."
        text_width, text_height = dc.GetTextExtent(text)
        dc.DrawText(text, (width - text_width) // 2, (height - text_height) // 2)

        del dc # End drawing

        super().__init__(bitmap,
                         wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                         3000, None, -1, style=wx.SIMPLE_BORDER | wx.STAY_ON_TOP)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        # Prevent the user from closing the splash screen
        event.Veto()
