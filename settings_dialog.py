import wx
from constants import THEMES

class SettingsDialog(wx.Dialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent, title="الإعدادات")
        self.settings = settings.copy()
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.update_checkbox = wx.CheckBox(panel, label="التحقق من وجود تحديثات عند بدء التشغيل")
        self.update_checkbox.SetValue(self.settings.get("check_for_updates", True))
        vbox.Add(self.update_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.play_on_startup_checkbox = wx.CheckBox(panel, label="تشغيل آخر إذاعة تم الاستماع إليها عند بدء التشغيل")
        self.play_on_startup_checkbox.SetValue(self.settings.get("play_on_startup", False))
        vbox.Add(self.play_on_startup_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        theme_label = wx.StaticText(panel, label="سمة التطبيق:")
        vbox.Add(theme_label, flag=wx.LEFT | wx.TOP, border=10)
        
        self.theme_names = list(THEMES.keys())
        self.theme_choice = wx.Choice(panel, choices=self.theme_names)
        current_theme = self.settings.get("theme", "Light Mode 1")
        if current_theme in self.theme_names:
            self.theme_choice.SetStringSelection(current_theme)
        else:
            self.theme_choice.SetSelection(0)
        vbox.Add(self.theme_choice, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=10)


        self.font_size_checkbox = wx.CheckBox(panel, label="استخدام خط كبير")
        self.font_size_checkbox.SetValue(self.settings.get("large_font", False))
        vbox.Add(self.font_size_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        self.sound_effects_checkbox = wx.CheckBox(panel, label="تفعيل المؤثرات الصوتية")
        self.sound_effects_checkbox.SetValue(self.settings.get("sound_effects_enabled", True))
        vbox.Add(self.sound_effects_checkbox, flag=wx.LEFT | wx.TOP, border=10)

        # Manual buttons
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(panel, label="موافق")
        cancel_button = wx.Button(panel, label="إلغاء")
        hbox.Add(ok_button)
        hbox.Add(cancel_button, flag=wx.LEFT, border=5)

        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

        # Set sizer for the dialog itself
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        # Bind events manually
        ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_ok(self, event):
        self.settings["check_for_updates"] = self.update_checkbox.GetValue()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.GetValue()
        self.settings["theme"] = self.theme_choice.GetStringSelection()
        self.settings["large_font"] = self.font_size_checkbox.GetValue()
        self.settings["sound_effects_enabled"] = self.sound_effects_checkbox.GetValue()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def get_settings(self):
        return self.settings