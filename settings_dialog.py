import wx

class SettingsDialog(wx.Dialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent, title="الإعدادات")
        self.settings = settings.copy()
        
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.update_checkbox = wx.CheckBox(self.panel, label="التحقق من وجود تحديثات عند بدء التشغيل")
        self.update_checkbox.SetValue(self.settings.get("check_for_updates", True))
        self.vbox.Add(self.update_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.play_on_startup_checkbox = wx.CheckBox(self.panel, label="تشغيل آخر إذاعة تم الاستماع إليها عند بدء التشغيل")
        self.play_on_startup_checkbox.SetValue(self.settings.get("play_on_startup", False))
        self.vbox.Add(self.play_on_startup_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        theme_label = wx.StaticText(self.panel, label="سمة التطبيق:")
        self.vbox.Add(theme_label, flag=wx.LEFT | wx.TOP, border=10)
        
        self.theme_radio_box = wx.RadioBox(self.panel, choices=["فاتح", "داكن"], style=wx.RA_SPECIFY_ROWS)
        self.theme_radio_box.SetSelection(1 if self.settings.get("theme", "light") == "dark" else 0)
        self.vbox.Add(self.theme_radio_box, flag=wx.LEFT, border=10)

        self.font_size_checkbox = wx.CheckBox(self.panel, label="استخدام خط كبير")
        self.font_size_checkbox.SetValue(self.settings.get("large_font", False))
        self.vbox.Add(self.font_size_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.sound_effects_checkbox = wx.CheckBox(self.panel, label="تفعيل المؤثرات الصوتية")
        self.sound_effects_checkbox.SetValue(self.settings.get("sound_effects_enabled", True))
        self.vbox.Add(self.sound_effects_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.vbox.Add(self.buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(self.vbox)

        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self, event):
        self.settings["check_for_updates"] = self.update_checkbox.GetValue()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.GetValue()
        self.settings["theme"] = "dark" if self.theme_radio_box.GetSelection() == 1 else "light"
        self.settings["large_font"] = self.font_size_checkbox.GetValue()
        self.settings["sound_effects_enabled"] = self.sound_effects_checkbox.GetValue()
        self.EndModal(wx.ID_OK)

    def get_settings(self):
        return self.settings