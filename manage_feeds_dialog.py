import wx
from rss_manager import RSSManager

class ManageFeedsDialog(wx.Dialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="إدارة خلاصات RSS")

        self.rss_manager = RSSManager()
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # List of feeds
        feeds_label = wx.StaticText(self.panel, label="الخلاصات الحالية:")
        self.vbox.Add(feeds_label, flag=wx.LEFT | wx.TOP, border=10)

        self.feeds_listbox = wx.ListBox(self.panel, style=wx.LB_SINGLE)
        self.vbox.Add(self.feeds_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self._populate_feeds_list()

        # Add new feed section
        add_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.new_feed_text = wx.TextCtrl(self.panel)
        add_hbox.Add(self.new_feed_text, proportion=1, flag=wx.EXPAND)

        add_button = wx.Button(self.panel, label="إضافة")
        add_hbox.Add(add_button, flag=wx.LEFT, border=5)
        self.vbox.Add(add_hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Remove feed button
        remove_button = wx.Button(self.panel, label="إزالة المحدد")
        self.vbox.Add(remove_button, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)

        # Dialog buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self.panel, id=wx.ID_OK, label="موافق")
        button_sizer.Add(ok_button)
        self.vbox.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        self.panel.SetSizer(self.vbox)
        self.SetSize((400, 350))

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_add, add_button)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_button)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def _populate_feeds_list(self):
        """Clears and repopulates the listbox with current feeds."""
        self.feeds_listbox.Clear()
        feeds = self.rss_manager.get_feeds()
        if feeds:
            self.feeds_listbox.InsertItems(feeds, 0)

    def on_add(self, event):
        """Handles adding a new feed."""
        feed_url = self.new_feed_text.GetValue().strip()
        if feed_url:
            if self.rss_manager.add_feed(feed_url):
                self._populate_feeds_list()
                self.new_feed_text.Clear()
            else:
                wx.MessageBox("هذه الخلاصة موجودة بالفعل.", "خطأ", wx.ICON_ERROR)
        else:
            wx.MessageBox("الرجاء إدخال رابط الخلاصة.", "خطأ", wx.ICON_ERROR)

    def on_remove(self, event):
        """Handles removing a selected feed."""
        selected_index = self.feeds_listbox.GetSelection()
        if selected_index != wx.NOT_FOUND:
            feed_url = self.feeds_listbox.GetString(selected_index)
            if self.rss_manager.remove_feed(feed_url):
                self._populate_feeds_list()
            else:
                wx.MessageBox("لم يتم العثور على الخلاصة المحددة.", "خطأ", wx.ICON_ERROR)
        else:
            wx.MessageBox("الرجاء تحديد خلاصة لإزالتها.", "تنبيه", wx.ICON_INFORMATION)

    def on_ok(self, event):
        """Closes the dialog."""
        self.EndModal(wx.ID_OK)
