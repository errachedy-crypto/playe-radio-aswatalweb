import wx

class HelpDialog(wx.Dialog):
    def __init__(self, help_content, parent=None):
        super().__init__(parent, title="دليل المساعدة", size=(600, 400))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        text_ctrl.SetValue(help_content)
        vbox.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        close_button = wx.Button(panel, label="إغلاق")
        vbox.Add(close_button, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 10)

        panel.SetSizer(vbox)
        
        self.Bind(wx.EVT_BUTTON, self.on_close, close_button)
        self.Centre()

    def on_close(self, event):
        self.Close()