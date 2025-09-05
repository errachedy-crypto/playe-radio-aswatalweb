import logging
import webbrowser
import os
import sys
from datetime import datetime
import wx

from constants import CURRENT_VERSION, UPDATE_URL, THEMES
from settings import load_settings, save_settings
from threads import UpdateChecker, StationLoader, ArticleLoader
from player import Player
from settings_dialog import SettingsDialog
from help_dialog import HelpDialog
from sound_manager import SoundManager
from popup_window import TimedPopup
from rss_manager import RSSManager

try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except (ImportError, OSError):
    PYCAW_AVAILABLE = False


class RadioWindow(wx.Frame):
    def __init__(self, vlc_instance, sound_manager):
        super().__init__(None, title=f"Amwaj v{CURRENT_VERSION}", size=(700, 700))

        self.vlc_instance = vlc_instance
        self.sound_manager = sound_manager
        self.rss_manager = RSSManager()
        self.articles = []

        self.settings = load_settings()
        self.player = Player(self.vlc_instance)
        self.categories = []

        self.sleep_timer = wx.Timer(self)

        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create the notebook
        self.notebook = wx.Notebook(self.panel)
        self.main_sizer.Add(self.notebook, 1, wx.EXPAND)

        # Create panels for the tabs
        self.radio_panel = wx.Panel(self.notebook)
        self.news_panel = wx.Panel(self.notebook)

        self.notebook.AddPage(self.radio_panel, "الراديو")
        self.notebook.AddPage(self.news_panel, "الأخبار")

        self.setup_radio_ui() # Refactored UI setup
        self.setup_news_ui() # Placeholder for news UI

        self.setup_menu()
        self.connect_signals()

        self.set_initial_volume()
        self.apply_theme()
        self.apply_sound_settings()

        wx.CallAfter(self.finish_setup)
        self.setup_shortcuts()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.panel.SetSizer(self.main_sizer)


    def set_initial_volume(self):
        initial_volume = self.settings.get("volume", 50)
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = interface.QueryInterface(IAudioEndpointVolume)
                system_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
                initial_volume = system_volume
            except Exception as e:
                logging.warning(f"Could not set initial volume from system: {e}")
        self._set_volume(initial_volume, announce=False)


    def finish_setup(self):
        try:
            logging.debug("Starting setup tasks...")
            self.load_stations()
            self.populate_feeds_tree()
            if self.settings.get("check_for_updates", True):
                self.check_for_updates()
            self.GetStatusBar().SetStatusText("أهلاً بك في الراديو العربي STV")
            if self.settings.get("play_on_startup", False):
                self.play_last_station()
            logging.debug("Setup tasks completed successfully.")
        except Exception as e:
            logging.error(f"Error during setup: {e}")
            wx.MessageBox(f"حدث خطأ أثناء تهيئة التطبيق:\n{e}", "خطأ في التهيئة", wx.OK | wx.ICON_ERROR)

    def setup_radio_ui(self):
        radio_sizer = wx.BoxSizer(wx.VERTICAL)

        # Tree Widget
        self.tree_widget = wx.TreeCtrl(self.radio_panel, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        radio_sizer.Add(self.tree_widget, 1, wx.EXPAND | wx.ALL, 5)

        # Search Box
        self.search_box = wx.TextCtrl(self.radio_panel, style=wx.TE_PROCESS_ENTER)
        self.search_box.SetHint("ابحث عن إذاعة...")
        radio_sizer.Add(self.search_box, 0, wx.EXPAND | wx.ALL, 5)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.play_stop_button = wx.Button(self.radio_panel, label="تشغيل")
        button_sizer.Add(self.play_stop_button, 1, wx.EXPAND | wx.ALL, 5)
        self.record_button = wx.Button(self.radio_panel, label="تسجيل")
        button_sizer.Add(self.record_button, 1, wx.EXPAND | wx.ALL, 5)
        radio_sizer.Add(button_sizer, 0, wx.EXPAND)

        # Volume
        volume_sizer = wx.BoxSizer(wx.HORIZONTAL)
        volume_label = wx.StaticText(self.radio_panel, label="مستوى الصوت:")
        self.volume_slider = wx.Slider(self.radio_panel, value=50, minValue=0, maxValue=100)
        volume_sizer.Add(volume_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        volume_sizer.Add(self.volume_slider, 1, wx.EXPAND | wx.ALL, 5)
        radio_sizer.Add(volume_sizer, 0, wx.EXPAND)

        # Timer
        timer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timer_label = wx.StaticText(self.radio_panel, label="مؤقت النوم:")
        self.timer_options = ["إيقاف", "15 دقيقة", "30 دقيقة", "60 دقيقة", "90 دقيقة"]
        self.sleep_timer_choice = wx.Choice(self.radio_panel, choices=self.timer_options)
        self.sleep_timer_choice.SetSelection(0)
        timer_sizer.Add(timer_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        timer_sizer.Add(self.sleep_timer_choice, 1, wx.EXPAND | wx.ALL, 5)
        radio_sizer.Add(timer_sizer, 0, wx.EXPAND)

        # Settings button
        settings_button = wx.Button(self.radio_panel, label="الإعدادات")
        radio_sizer.Add(settings_button, 0, wx.EXPAND | wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.open_settings_dialog, settings_button)

        # Now Playing
        self.now_playing_label = wx.StaticText(self.radio_panel, label="التشغيل الحالي: -", style=wx.ALIGN_CENTER)
        radio_sizer.Add(self.now_playing_label, 0, wx.EXPAND | wx.ALL, 5)

        self.CreateStatusBar()
        self.radio_panel.SetSizer(radio_sizer)

    def setup_news_ui(self):
        news_sizer = wx.BoxSizer(wx.VERTICAL)
        splitter = wx.SplitterWindow(self.news_panel, style=wx.SP_LIVE_UPDATE)
        news_sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 5)
        left_panel = wx.Panel(splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.feeds_tree = wx.TreeCtrl(left_panel, style=wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        left_sizer.Add(self.feeds_tree, 1, wx.EXPAND | wx.ALL, 5)
        refresh_button = wx.Button(left_panel, label="تحديث الخلاصات")
        left_sizer.Add(refresh_button, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        right_panel = wx.Panel(splitter)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.articles_list = wx.ListCtrl(right_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.articles_list.InsertColumn(0, "العنوان", width=350)
        self.articles_list.InsertColumn(1, "تاريخ النشر", width=150)
        right_sizer.Add(self.articles_list, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        splitter.SplitVertically(left_panel, right_panel, 200)
        self.news_panel.SetSizer(news_sizer)
        self.Bind(wx.EVT_BUTTON, self.on_refresh_feeds, refresh_button)


    def connect_signals(self):
        self.Bind(wx.EVT_BUTTON, self.toggle_play_stop, self.play_stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_toggle_record, self.record_button)
        self.Bind(wx.EVT_SLIDER, self.adjust_volume, self.volume_slider)
        self.Bind(wx.EVT_CHOICE, self.on_sleep_timer_selected, self.sleep_timer_choice)
        self.Bind(wx.EVT_TIMER, self.on_sleep_timer_end, self.sleep_timer)
        self.tree_widget.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.play_station_event)
        self.tree_widget.Bind(wx.EVT_CHAR_HOOK, self.on_tree_char_hook)
        self.tree_widget.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection_changed)
        self.search_box.Bind(wx.EVT_TEXT, self.filter_stations)
        self.player.connect_error_handler(self.handle_player_error)
        self.feeds_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_feed_selected)
        self.articles_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_article_activated)

    def on_sleep_timer_selected(self, event):
        selection = self.sleep_timer_choice.GetSelection()
        self.sleep_timer.Stop()
        self.GetStatusBar().SetStatusText("")
        if selection == 0: return
        try:
            minutes = int(self.timer_options[selection].split()[0])
        except (ValueError, IndexError):
            return
        self.sleep_timer.StartOnce(minutes * 60 * 1000)
        self.GetStatusBar().SetStatusText(f"سيتم إيقاف الراديو بعد {minutes} دقيقة.")

    def on_sleep_timer_end(self, event):
        self.GetStatusBar().SetStatusText("تم إيقاف الراديو بواسطة مؤقت النوم.")
        self.stop_station()
        self.sleep_timer_choice.SetSelection(0)

    def on_toggle_record(self, event):
        if self.player.is_recording():
            self.player.stop_recording()
            self.record_button.SetLabel("تسجيل")
            self.play_stop_button.Enable(True)
            self.GetStatusBar().SetStatusText("تم إيقاف التسجيل.")
        else:
            if not self.player.is_playing() or not self.player.current_url:
                wx.MessageBox("يجب تشغيل إذاعة أولاً لبدء التسجيل.", "خطأ", wx.OK | wx.ICON_ERROR)
                return

            station_name = "recording"
            item = self.tree_widget.GetSelection()
            if item.IsOk():
                station_name = self.tree_widget.GetItemText(item)
                station_name = "".join(x for x in station_name if x.isalnum() or x in " _-").strip()

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"{station_name}_{timestamp}.ts"

            with wx.FileDialog(self, "حفظ التسجيل", wildcard="Transport Stream (*.ts)|*.ts", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, defaultFile=default_filename) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                pathname = fileDialog.GetPath()
                if self.player.start_recording(pathname):
                    self.record_button.SetLabel("إيقاف التسجيل")
                    self.play_stop_button.Enable(False)
                    self.GetStatusBar().SetStatusText(f"جاري التسجيل في: {pathname}")
                else:
                    wx.MessageBox("فشل بدء التسجيل.", "خطأ", wx.OK | wx.ICON_ERROR)

    def setup_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        
        self.id_settings = wx.NewIdRef()
        self.id_about = wx.NewIdRef()
        self.id_exit = wx.NewIdRef()
        self.id_help = wx.NewIdRef()

        settings_item = file_menu.Append(self.id_settings, "الإعدادات...", "Open settings")
        self.Bind(wx.EVT_MENU, self.open_settings_dialog, settings_item)
        
        about_item = file_menu.Append(self.id_about, "حول البرنامج...", "About the application")
        self.Bind(wx.EVT_MENU, self.show_about_dialog, about_item)

        file_menu.AppendSeparator()
        exit_item = file_menu.Append(self.id_exit, "خروج", "Exit the application")
        self.Bind(wx.EVT_MENU, self.on_close, exit_item)
        
        menu_bar.Append(file_menu, "&ملف")

        help_menu = wx.Menu()
        help_item = help_menu.Append(self.id_help, "عرض دليل المساعدة", "Show help")
        self.Bind(wx.EVT_MENU, self.show_help_dialog, help_item)
        menu_bar.Append(help_menu, "&المساعدة")

        self.SetMenuBar(menu_bar)

    def setup_shortcuts(self):
        self.id_play_stop = wx.NewIdRef()
        self.id_focus_search = wx.NewIdRef()
        self.id_restart = wx.NewIdRef()
        self.id_vol_down = wx.NewIdRef()
        self.id_vol_up = wx.NewIdRef()
        self.id_mute = wx.NewIdRef()

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_F2, self.id_play_stop),
            (wx.ACCEL_NORMAL, wx.WXK_F3, self.id_focus_search),
            (wx.ACCEL_NORMAL, wx.WXK_F5, self.id_restart),
            (wx.ACCEL_NORMAL, wx.WXK_F7, self.id_vol_down),
            (wx.ACCEL_NORMAL, wx.WXK_F8, self.id_vol_up),
            (wx.ACCEL_NORMAL, wx.WXK_F9, self.id_mute),
        ])
        self.SetAcceleratorTable(accel_tbl)

        self.Bind(wx.EVT_MENU, self.toggle_play_stop, id=self.id_play_stop)
        self.Bind(wx.EVT_MENU, lambda event: self.search_box.SetFocus(), id=self.id_focus_search)
        self.Bind(wx.EVT_MENU, self.restart_station, id=self.id_restart)
        self.Bind(wx.EVT_MENU, self.lower_volume, id=self.id_vol_down)
        self.Bind(wx.EVT_MENU, self.raise_volume, id=self.id_vol_up)
        self.Bind(wx.EVT_MENU, self.toggle_mute, id=self.id_mute)

    def on_tree_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            item = self.tree_widget.GetSelection()
            if item.IsOk():
                self.play_station(item)
        else:
            event.Skip()

    def on_tree_selection_changed(self, event):
        self.sound_manager.play("navigate")
        event.Skip()

    def play_station_event(self, event):
        item = event.GetItem()
        self.play_station(item)

    def play_station(self, item=None):
        if not item:
            item = self.tree_widget.GetSelection()
        if not item.IsOk() or self.tree_widget.GetItemData(item) is None:
            return

        station_name = self.tree_widget.GetItemText(item)
        url_string = self.tree_widget.GetItemData(item)

        if not url_string:
            return

        self.sound_manager.play("play_station")
        self.settings["last_station_name"] = station_name
        self.player.play(url_string)
        self.now_playing_label.SetLabel(f"التشغيل الحالي: {station_name}")
        self.show_announcement_popup(f"تشغيل: {station_name}")
        self.play_stop_button.SetLabel('إيقاف')

    def stop_station(self):
        self.player.stop()
        self.sound_manager.play("stop_station")
        self.now_playing_label.SetLabel("التشغيل الحالي: -")
        self.show_announcement_popup("إيقاف التشغيل")
        self.play_stop_button.SetLabel('تشغيل')

    def toggle_play_stop(self, event):
        if self.player.is_playing():
            self.stop_station()
        else:
            item = self.tree_widget.GetSelection()
            if item.IsOk():
                self.play_station(item)
            else:
                self.play_last_station()

    def show_announcement_popup(self, message):
        popup = TimedPopup(self, message)

    def _set_volume(self, volume, announce=True):
        self.volume_slider.SetValue(volume)
        self.player.set_volume(volume)
        self.settings["volume"] = volume
        if announce:
            self.show_announcement_popup(f"مستوى الصوت: {volume}%")

    def adjust_volume(self, event):
        volume = self.volume_slider.GetValue()
        self._set_volume(volume)

    def lower_volume(self, event):
        new_volume = max(self.volume_slider.GetValue() - 10, 0)
        self._set_volume(new_volume)

    def raise_volume(self, event):
        new_volume = min(self.volume_slider.GetValue() + 10, 100)
        self._set_volume(new_volume)

    def toggle_mute(self, event):
        self.player.toggle_mute()

    def restart_station(self, event):
        self.play_station()

    def play_last_station(self):
        last_station_name = self.settings.get("last_station_name")
        if not last_station_name:
            return

        root = self.tree_widget.GetRootItem()
        if not root.IsOk():
            return

        (child, cookie) = self.tree_widget.GetFirstChild(root)
        while child.IsOk():
            (grandchild, cookie2) = self.tree_widget.GetFirstChild(child)
            while grandchild.IsOk():
                if self.tree_widget.GetItemText(grandchild) == last_station_name:
                    self.tree_widget.SelectItem(grandchild)
                    self.play_station(grandchild)
                    return
                (grandchild, cookie2) = self.tree_widget.GetNextChild(child, cookie2)
            (child, cookie) = self.tree_widget.GetNextChild(root, cookie)


    def load_stations(self):
        self.progress_dialog = wx.ProgressDialog("جاري التحميل", "يرجى الانتظار...", parent=self)
        self.progress_dialog.Pulse()

        self.station_loader = StationLoader(self)
        self.station_loader.start()

    def on_stations_loaded(self, categories):
        self.categories = categories
        self.progress_dialog.Destroy()
        self.populate_stations(self.categories)
        self.sound_manager.play("update_success")
        self.play_last_station_if_enabled()

    def on_stations_load_error(self, error_message, is_critical):
        self.progress_dialog.Destroy()
        if is_critical:
            wx.MessageBox(error_message, "خطأ فادح", wx.OK | wx.ICON_ERROR)
        else:
            self.GetStatusBar().SetStatusText(error_message, 10000)

    def populate_stations(self, categories):
        self.tree_widget.DeleteAllItems()
        root = self.tree_widget.AddRoot("All Stations")
        for category in categories:
            parent = self.tree_widget.AppendItem(root, category["name"])
            for station in category.get("stations", []):
                child = self.tree_widget.AppendItem(parent, station["name"])
                self.tree_widget.SetItemData(child, station["url"])
        self.tree_widget.ExpandAll()

    def play_last_station_if_enabled(self):
        if self.settings.get("play_on_startup", False):
            self.play_last_station()

    def filter_stations(self, event):
        search_text = self.search_box.GetValue().lower()
        if not search_text:
            self.populate_stations(self.categories)
            return

        filtered_categories = []
        for category in self.categories:
            matching_stations = []
            for station in category.get("stations", []):
                if search_text in station["name"].lower():
                    matching_stations.append(station)
            
            if matching_stations:
                filtered_categories.append({
                    "name": category["name"],
                    "stations": matching_stations
                })

        self.populate_stations(filtered_categories)

    def check_for_updates(self):
        self.update_checker = UpdateChecker(CURRENT_VERSION, UPDATE_URL, self)
        self.update_checker.start()

    def show_update_dialog(self, new_version, download_url):
        message = (f"يتوفر تحديث جديد!\n\n"
                   f"الإصدار الحالي: {CURRENT_VERSION}\n"
                   f"الإصدار الجديد: {new_version}\n\n"
                   "هل تريد الذهاب إلى صفحة التنزيل الآن؟")

        dlg = wx.MessageDialog(self, message, "تحديث متوفر", wx.YES_NO | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES:
            webbrowser.open(download_url)
        dlg.Destroy()

    def apply_sound_settings(self):
        enabled = self.settings.get("sound_effects_enabled", True)
        self.sound_manager.set_enabled(enabled)

    def open_settings_dialog(self, event):
        with SettingsDialog(self.settings, self) as dialog:
            # The main settings dialog's OK/Cancel logic is now less important
            # for the feeds, as they are managed in a separate dialog.
            # However, we still need to apply other settings if changed.
            if dialog.ShowModal() == wx.ID_OK:
                new_settings = dialog.get_settings()
                theme_changed = self.settings.get("theme") != new_settings.get("theme")
                font_changed = self.settings.get("large_font") != new_settings.get("large_font")
                self.settings = new_settings
                save_settings(self.settings)
                self.apply_theme()
                self.apply_sound_settings()
                if theme_changed or font_changed:
                    wx.MessageBox("بعض الإعدادات تتطلب إعادة تشغيل التطبيق لتصبح سارية المفعول.", "الإعدادات", wx.OK | wx.ICON_INFORMATION)

        # Always refresh the feeds tree after closing the settings dialog
        self.on_refresh_feeds(event=None)


    def show_about_dialog(self, event):
        about_text = f"""Amwaj Radio v{CURRENT_VERSION}

تطبيق أمواج للاستماع إلى الإذاعات العربية.

الميزات الجديدة في هذا الإصدار:
- نظام مظاهر متقدم
- مؤثرات صوتية
- ميزة تسجيل البث
- مؤقت النوم
- تحسينات على الاستقرار وإصلاح الأخطاء

المطور: errachedy
"""
        wx.MessageBox(about_text, "حول البرنامج", wx.OK | wx.ICON_INFORMATION)

    def apply_theme(self):
        font = self.GetFont()
        if self.settings.get("large_font", False):
            font.SetPointSize(14)
        else:
            font.SetPointSize(wx.NORMAL_FONT.GetPointSize())
        self.SetFont(font)

        theme_name = self.settings.get("theme", "Light Mode")
        theme_colors = THEMES.get(theme_name, THEMES["Light Mode"])

        bg_colour = wx.Colour(theme_colors["bg"])
        fg_colour = wx.Colour(theme_colors["text"])

        # Apply theme to panels within the notebook
        self.radio_panel.SetBackgroundColour(bg_colour)
        self.radio_panel.SetForegroundColour(fg_colour)
        self.news_panel.SetBackgroundColour(bg_colour)
        self.news_panel.SetForegroundColour(fg_colour)

        # Apply theme to child widgets
        for panel in [self.radio_panel, self.news_panel]:
            for widget in panel.GetChildren():
                if isinstance(widget, (wx.StaticText, wx.CheckBox, wx.RadioBox, wx.TextCtrl, wx.Choice)):
                    widget.SetBackgroundColour(bg_colour)
                    widget.SetForegroundColour(fg_colour)
                elif isinstance(widget, wx.Button):
                    pass # Buttons might need special handling

        self.tree_widget.SetBackgroundColour(bg_colour)
        self.tree_widget.SetForegroundColour(fg_colour)

        if hasattr(self, 'feeds_tree'):
            self.feeds_tree.SetBackgroundColour(bg_colour)
            self.feeds_tree.SetForegroundColour(fg_colour)
            self.articles_list.SetBackgroundColour(bg_colour)
            self.articles_list.SetForegroundColour(fg_colour)

        self.panel.Refresh()


    def handle_player_error(self, event):
        logging.error("Player error detected.")
        wx.CallAfter(wx.MessageBox, "حدث خطأ أثناء محاولة تشغيل الإذاعة", "خطأ في التشغيل", wx.OK | wx.ICON_ERROR)
        wx.CallAfter(self.stop_station)

    def show_help_dialog(self, event):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            help_file_path = os.path.join(base_path, 'HELP.md')

            if not os.path.exists(help_file_path):
                wx.MessageBox(f"ملف المساعدة غير موجود في المسار المتوقع:\n{help_file_path}", "خطأ", wx.OK | wx.ICON_WARNING)
                return

            with open(help_file_path, "r", encoding="utf-8") as f:
                help_content = f.read()
            
            self.help_dialog = HelpDialog(help_content, self)
            self.help_dialog.ShowModal()
            self.help_dialog.Destroy()
        except Exception as e:
            logging.error(f"Could not show help dialog: {e}")
            wx.MessageBox(f"لا يمكن عرض ملف المساعدة: {e}", "خطأ", wx.OK | wx.ICON_ERROR)


    def populate_feeds_tree(self):
        self.feeds_tree.DeleteAllItems()
        root = self.feeds_tree.AddRoot("الخلاصات")
        categories = self.rss_manager.get_merged_categories()
        for cat_data in categories:
            display_name = cat_data["name"]
            if cat_data.get("source") == "local":
                display_name += " (محلي)"

            category_node = self.feeds_tree.AppendItem(root, display_name)
            self.feeds_tree.SetItemData(category_node, {"type": "category"})
            for feed_url in cat_data["feeds"]:
                feed_node = self.feeds_tree.AppendItem(category_node, feed_url)
                self.feeds_tree.SetItemData(feed_node, {"type": "feed", "url": feed_url})
        self.feeds_tree.ExpandAll()
        self.news_panel.Layout()

    def on_refresh_feeds(self, event):
        self.rss_manager = RSSManager()
        self.populate_feeds_tree()
        self.articles_list.DeleteAllItems()
        self.GetStatusBar().SetStatusText("تم تحديث قائمة الخلاصات.")

    def on_feed_selected(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        item_data = self.feeds_tree.GetItemData(item)
        if item_data and item_data.get("type") == "feed":
            feed_url = item_data.get("url")
            self.GetStatusBar().SetStatusText(f"جاري تحميل المقالات من {feed_url}...")
            self.articles_list.DeleteAllItems()
            loader = ArticleLoader(feed_url, self)
            loader.start()

    def on_articles_fetched(self, articles):
        self.articles = articles
        self.articles_list.DeleteAllItems()
        for i, article in enumerate(articles):
            self.articles_list.InsertItem(i, article["title"])
            self.articles_list.SetItem(i, 1, article["published"])
            self.articles_list.SetItemData(i, i)
        self.GetStatusBar().SetStatusText(f"تم تحميل {len(articles)} مقالة.")

    def on_articles_fetch_error(self, feed_url):
        self.GetStatusBar().SetStatusText(f"فشل تحميل المقالات من {feed_url}.")

    def on_article_activated(self, event):
        item_index = event.GetData()
        if 0 <= item_index < len(self.articles):
            article_link = self.articles[item_index].get("link")
            if article_link:
                webbrowser.open(article_link)

    def on_close(self, event):
        save_settings(self.settings)
        self.Destroy()