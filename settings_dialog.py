import wx
from constants import THEMES

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
        
        self.theme_choices = list(THEMES.keys())
        self.theme_choice = wx.Choice(self.panel, choices=self.theme_choices)
        current_theme = self.settings.get("theme", "Light Mode")
        if current_theme in self.theme_choices:
            self.theme_choice.SetStringSelection(current_theme)
        self.vbox.Add(self.theme_choice, flag=wx.LEFT | wx.EXPAND, border=10)

        self.font_size_checkbox = wx.CheckBox(self.panel, label="استخدام خط كبير")
        self.font_size_checkbox.SetValue(self.settings.get("large_font", False))
        self.vbox.Add(self.font_size_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.sound_effects_checkbox = wx.CheckBox(self.panel, label="تفعيل المؤثرات الصوتية")
        self.sound_effects_checkbox.SetValue(self.settings.get("sound_effects_enabled", True))
        self.vbox.Add(self.sound_effects_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.screen_reader_checkbox = wx.CheckBox(self.panel, label="تفعيل إعلانات قارئ الشاشة")
        self.screen_reader_checkbox.SetValue(self.settings.get("screen_reader_enabled", True))
        self.vbox.Add(self.screen_reader_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self.panel, id=wx.ID_OK, label="موافق")
        cancel_button = wx.Button(self.panel, id=wx.ID_CANCEL, label="إلغاء")
        button_sizer.Add(ok_button)
        button_sizer.Add(cancel_button, flag=wx.LEFT, border=5)
        self.vbox.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(self.vbox)

        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self, event):
        self.settings["check_for_updates"] = self.update_checkbox.GetValue()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.GetValue()
        self.settings["theme"] = self.theme_choice.GetStringSelection()
        self.settings["large_font"] = self.font_size_checkbox.GetValue()
        self.settings["sound_effects_enabled"] = self.sound_effects_checkbox.GetValue()
        self.settings["screen_reader_enabled"] = self.screen_reader_checkbox.GetValue()
        self.EndModal(wx.ID_OK)

    def get_settings(self):
        return self.settings