import wx

class TimedPopup(wx.Frame):
    def __init__(self, parent, message, duration_ms=2000):
        style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER | wx.STAY_ON_TOP
        super().__init__(parent, style=style)

        self.SetBackgroundColour(wx.BLACK)

        text = wx.StaticText(self, label=message)
        text.SetForegroundColour(wx.WHITE)
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        text.SetFont(font)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 1, wx.EXPAND | wx.ALL, 20)
        self.SetSizerAndFit(sizer)

        # Center on the parent window
        parent_rect = parent.GetScreenRect()
        self_rect = self.GetRect()
        pos_x = parent_rect.x + (parent_rect.width - self_rect.width) // 2
        pos_y = parent_rect.y + (parent_rect.height - self_rect.height) // 2
        self.SetPosition((pos_x, pos_y))

        self.Show()

        # Set a timer to close the popup
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.StartOnce(duration_ms)

    def on_timer(self, event):
        self.Close()
