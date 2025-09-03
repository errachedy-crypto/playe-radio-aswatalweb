import wx

class SuggestStationDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="اقتراح إذاعة")

        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create the form fields
        self.create_form()

        # Create the buttons
        self.create_buttons()

        self.panel.SetSizerAndFit(self.main_sizer)
        self.Fit()

    def create_form(self):
        form_sizer = wx.FlexGridSizer(5, 2, 10, 10)

        fields = [
            ("اسم الإذاعة:", "station_name"),
            ("رابط البث:", "stream_url"),
            ("البلد:", "country"),
            ("البريد الإلكتروني:", "email"),
            ("الموقع الإلكتروني (إن وجد):", "website")
        ]

        self.text_controls = {}
        for label_text, name in fields:
            label = wx.StaticText(self.panel, label=label_text)
            text_ctrl = wx.TextCtrl(self.panel)
            self.text_controls[name] = text_ctrl

            form_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            form_sizer.Add(text_ctrl, 1, wx.EXPAND)

        self.main_sizer.Add(form_sizer, 1, wx.EXPAND | wx.ALL, 10)

    def create_buttons(self):
        button_sizer = wx.StdDialogButtonSizer()

        submit_button = wx.Button(self.panel, wx.ID_OK, "إرسال")
        submit_button.SetDefault()
        button_sizer.AddButton(submit_button)

        cancel_button = wx.Button(self.panel, wx.ID_CANCEL, "إلغاء")
        button_sizer.AddButton(cancel_button)

        button_sizer.Realize()

        self.main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

    def get_values(self):
        """Returns the values from the form fields."""
        return {name: ctrl.GetValue() for name, ctrl in self.text_controls.items()}
