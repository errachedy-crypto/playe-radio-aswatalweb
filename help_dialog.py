import wx

class HelpDialog(wx.Dialog):
    def __init__(self, help_content, parent=None):
        super().__init__(parent, title="دليل المساعدة", size=(600, 400))
        
        # Use a read-only TextCtrl for better accessibility
        self.text_ctrl = wx.TextCtrl(self, value=help_content, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)

        # Improve font for readability
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text_ctrl.SetFont(font)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Add a close button
        ok_button = wx.Button(self, wx.ID_OK, "إغلاق")
        sizer.Add(ok_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(sizer)