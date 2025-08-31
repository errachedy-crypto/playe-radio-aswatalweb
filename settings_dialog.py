import wx
from constants import THEMES

class SettingsDialog(wx.Dialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent, title="الإعدادات")
        self.settings = settings.copy()
        
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Update Checkbox
        self.update_checkbox = wx.CheckBox(self.panel, label="التحقق من وجود تحديثات عند بدء التشغيل")
        self.update_checkbox.SetValue(self.settings.get("check_for_updates", True))
        self.vbox.Add(self.update_checkbox, flag=wx.ALL, border=10)

        # Play on Startup Checkbox
        self.play_on_startup_checkbox = wx.CheckBox(self.panel, label="تشغيل آخر إذاعة تم الاستماع إليها عند بدء التشغيل")
        self.play_on_startup_checkbox.SetValue(self.settings.get("play_on_startup", False))
        self.vbox.Add(self.play_on_startup_checkbox, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Font Size Checkbox
        self.font_size_checkbox = wx.CheckBox(self.panel, label="استخدام خط كبير لتسهيل القراءة")
        self.font_size_checkbox.SetValue(self.settings.get("large_font", False))
        self.vbox.Add(self.font_size_checkbox, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Sound Effects Checkbox (for next step)
        self.sound_effects_checkbox = wx.CheckBox(self.panel, label="تفعيل المؤثرات الصوتية للتطبيق")
        self.sound_effects_checkbox.SetValue(self.settings.get("sound_effects_enabled", True))
        self.vbox.Add(self.sound_effects_checkbox, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Theme Chooser
        theme_sizer = wx.BoxSizer(wx.HORIZONTAL)
        theme_label = wx.StaticText(self.panel, label="مظهر التطبيق:")
        theme_sizer.Add(theme_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.theme_choices = list(THEMES.keys())
        self.theme_choice = wx.Choice(self.panel, choices=self.theme_choices)
        current_theme = self.settings.get("theme", "Light Mode 1")
        try:
            self.theme_choice.SetSelection(self.theme_choices.index(current_theme))
        except ValueError:
            self.theme_choice.SetSelection(0) # Default to first theme
        theme_sizer.Add(self.theme_choice, 1, wx.EXPAND)
        self.vbox.Add(theme_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)


        # OK/Cancel Buttons
        self.buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.vbox.Add(self.buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(self.vbox)
        self.Fit()
        self.CenterOnParent()

        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self, event):
        self.settings["check_for_updates"] = self.update_checkbox.GetValue()
        self.settings["play_on_startup"] = self.play_on_startup_checkbox.GetValue()
        self.settings["large_font"] = self.font_size_checkbox.GetValue()
        self.settings["sound_effects_enabled"] = self.sound_effects_checkbox.GetValue()
        selected_theme_index = self.theme_choice.GetSelection()
        self.settings["theme"] = self.theme_choices[selected_theme_index]
        self.EndModal(wx.ID_OK)

    def get_settings(self):
        return self.settings