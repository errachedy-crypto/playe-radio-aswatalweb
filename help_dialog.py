import wx
import wx.html

class HelpDialog(wx.Dialog):
    def __init__(self, help_content, parent=None):
        super().__init__(parent, title="دليل المساعدة", size=(600, 400))
        
        self.html_window = wx.html.HtmlWindow(self)
        self.html_window.SetPage(help_content)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html_window, 1, wx.EXPAND)
        self.SetSizer(sizer)