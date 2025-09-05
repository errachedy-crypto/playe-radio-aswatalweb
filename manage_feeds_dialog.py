import wx
from rss_manager import RSSManager

class ManageFeedsDialog(wx.Dialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="إدارة خلاصات RSS", size=(500, 450))

        self.rss_manager = RSSManager()
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Tree control for categories and feeds
        self.tree = wx.TreeCtrl(self.panel, style=wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        self.main_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 10)
        self.populate_tree()

        # --- Add Feed Section ---
        add_feed_box = wx.StaticBox(self.panel, label="إضافة خلاصة جديدة إلى القسم المحدد")
        add_feed_sizer = wx.StaticBoxSizer(add_feed_box, wx.HORIZONTAL)
        self.new_feed_text = wx.TextCtrl(self.panel)
        add_feed_sizer.Add(self.new_feed_text, 1, wx.EXPAND | wx.ALL, 5)
        add_feed_button = wx.Button(self.panel, label="إضافة خلاصة")
        add_feed_sizer.Add(add_feed_button, 0, wx.ALL, 5)
        self.main_sizer.Add(add_feed_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # --- Add Category and Remove Buttons ---
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_category_button = wx.Button(self.panel, label="إضافة قسم محلي جديد")
        button_sizer.Add(add_category_button, 1, wx.EXPAND | wx.ALL, 5)
        remove_button = wx.Button(self.panel, label="إزالة العنصر المحلي المحدد")
        button_sizer.Add(remove_button, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # --- OK Button ---
        ok_button = wx.Button(self.panel, id=wx.ID_OK, label="إغلاق")
        self.main_sizer.Add(ok_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.panel.SetSizer(self.main_sizer)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_add_feed, add_feed_button)
        self.Bind(wx.EVT_BUTTON, self.on_add_category, add_category_button)
        self.Bind(wx.EVT_BUTTON, self.on_remove, remove_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK), id=wx.ID_OK)

    def populate_tree(self):
        self.tree.DeleteAllItems()
        root = self.tree.AddRoot("All Feeds")
        categories = self.rss_manager.get_merged_categories()

        for cat_data in categories:
            display_name = cat_data["name"]
            if cat_data["source"] == "local":
                display_name += " (محلي)"

            category_node = self.tree.AppendItem(root, display_name)
            self.tree.SetItemData(category_node, {"type": "category", "source": cat_data["source"], "real_name": cat_data["name"]})

            for feed_url in cat_data["feeds"]:
                feed_node = self.tree.AppendItem(category_node, feed_url)
                # For now, we assume all feeds within a category share its source.
                self.tree.SetItemData(feed_node, {"type": "feed", "source": cat_data["source"], "category": cat_data["name"]})

        self.tree.ExpandAll()

    def on_add_category(self, event):
        with wx.TextEntryDialog(self, "أدخل اسم القسم الجديد:", "إضافة قسم محلي") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                category_name = dlg.GetValue().strip()
                if category_name:
                    if self.rss_manager.add_category(category_name):
                        self.populate_tree()
                    else:
                        wx.MessageBox(f"القسم '{category_name}' موجود بالفعل في قائمتك المحلية.", "خطأ", wx.ICON_ERROR)

    def on_add_feed(self, event):
        feed_url = self.new_feed_text.GetValue().strip()
        if not feed_url:
            wx.MessageBox("الرجاء إدخال رابط الخلاصة.", "خطأ", wx.ICON_ERROR)
            return

        selected_item = self.tree.GetSelection()
        if not selected_item.IsOk() or selected_item == self.tree.GetRootItem():
            wx.MessageBox("الرجاء تحديد قسم أولاً لإضافة الخلاصة إليه.", "خطأ", wx.ICON_ERROR)
            return

        item_data = self.tree.GetItemData(selected_item)
        if item_data["type"] == "feed":
            category_node = self.tree.GetItemParent(selected_item)
        else:
            category_node = selected_item

        category_name = self.tree.GetItemData(category_node)["real_name"]

        if self.rss_manager.add_feed_to_category(feed_url, category_name):
            self.populate_tree()
            self.new_feed_text.Clear()
        else:
            wx.MessageBox(f"فشلت إضافة الخلاصة. قد تكون موجودة بالفعل.", "خطأ", wx.ICON_ERROR)

    def on_remove(self, event):
        selected_item = self.tree.GetSelection()
        if not selected_item.IsOk() or selected_item == self.tree.GetRootItem():
            wx.MessageBox("الرجاء تحديد عنصر لإزالته.", "تنبيه", wx.ICON_INFORMATION)
            return

        item_data = self.tree.GetItemData(selected_item)

        if item_data["source"] == "remote":
            wx.MessageBox("لا يمكن حذف العناصر القادمة من الإنترنت. يمكنك فقط حذف الأقسام أو الخلاصات المحلية التي أضفتها بنفسك.", "معلومة", wx.ICON_INFORMATION)
            return

        item_text = self.tree.GetItemText(selected_item)
        category_name = self.tree.GetItemData(selected_item)["real_name"] if item_data["type"] == "category" else item_data["category"]

        if item_data["type"] == "category":
            with wx.MessageDialog(self, f"هل أنت متأكد من أنك تريد حذف قسم '{category_name}' المحلي وجميع خلاصاته؟", "تأكيد الحذف", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) as dlg:
                if dlg.ShowModal() == wx.ID_YES:
                    self.rss_manager.remove_category(category_name)
                    self.populate_tree()

        elif item_data["type"] == "feed":
            feed_url = item_text
            self.rss_manager.remove_feed_from_category(feed_url, category_name)
            self.populate_tree()
