import json
import os
import pymediainfo
import sys
import traceback

from winapp.mainwin_themed import *
from winapp.controls_themed.listbox import *
from winapp.controls_themed.static import *
from winapp.controls_themed.toolbar import *
from winapp.controls_themed.tooltips import *
from winapp.custom_controls.pane import *
from winapp.dialogs import *
from winapp.trayicon import *
from winapp.utils.lnk import get_lnk_infos
from winapp.utils.taskbar import taskbar, TBPF

from const import *
from myslider import *
from mystatusbar import *
from resources import *
from playlist import *

RATIOS = {
    IDM_RATIO_DEFAULT: '',
    IDM_RATIO_4_3: '4:3',
    IDM_RATIO_5_4: '5:4',
    IDM_RATIO_16_9: '16:9',
    IDM_RATIO_16_10: '16:10',
    IDM_RATIO_235_100: '235:100',
    IDM_RATIO_185_100: '185:100',
    IDM_RATIO_NONE: None,
}

########################################
# Load settings from registry
########################################
def load_settings() -> dict:
    settings = {}
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\59de44955ebd\\{APP_NAME}', byref(hkey)) == ERROR_SUCCESS:
        data = (BYTE * sizeof(DWORD))()
        cbData = DWORD(sizeof(data))
        # bool
        for prop in (
            'show_millisecs', 'show_menu', 'show_seek', 'show_controls', 'show_status', 'show_playlist', 'stayontop', 'minimize_to_tray', 'auto_resize_to_video',
            'single_instance', 'remember_playlist', 'use_meta_title'
        ):
            if advapi32.RegQueryValueExW(hkey, prop, None, None, byref(data), byref(cbData)) == ERROR_SUCCESS:
                settings[prop] = cast(data, POINTER(DWORD)).contents.value == 1
        # int
        for prop in ('engine', 'theme', 'volume', 'splitter_pos'):
            if advapi32.RegQueryValueExW(hkey, prop, None, None, byref(data), byref(cbData)) == ERROR_SUCCESS:
                settings[prop] = cast(data, POINTER(DWORD)).contents.value
        # str
        cbdata_str = DWORD()
        if advapi32.RegQueryValueExW(hkey, 'rect', None, None, None, byref(cbdata_str)) == ERROR_SUCCESS:
            data_str = (BYTE * cbdata_str.value)()
            if advapi32.RegQueryValueExW(hkey, 'rect', None, None, data_str, byref(cbdata_str)) == ERROR_SUCCESS:
                settings['rect'] = cast(data_str, LPWSTR).value

        cbdata_str = DWORD()
        if advapi32.RegQueryValueExW(hkey, 'last_playlist', None, None, None, byref(cbdata_str)) == ERROR_SUCCESS:
            data_str = (BYTE * cbdata_str.value)()
            if advapi32.RegQueryValueExW(hkey, 'last_playlist', None, None, data_str, byref(cbdata_str)) == ERROR_SUCCESS:
                settings['last_playlist'] = cast(data_str, LPWSTR).value

        cbdata_str = DWORD()
        if advapi32.RegQueryValueExW(hkey, 'color_values', None, None, None, byref(cbdata_str)) == ERROR_SUCCESS:
            data_str = (BYTE * cbdata_str.value)()
            if advapi32.RegQueryValueExW(hkey, 'color_values', None, None, data_str, byref(cbdata_str)) == ERROR_SUCCESS:
                settings['color_values'] = cast(data_str, LPWSTR).value

    else:
        advapi32.RegCreateKeyW(HKEY_CURRENT_USER, f'Software\\59de44955ebd\\{APP_NAME}' , byref(hkey))
    advapi32.RegCloseKey(hkey)
    return settings

########################################
# Save settings to registry
########################################
def save_settings(main):
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\59de44955ebd\\{APP_NAME}', byref(hkey)) == ERROR_SUCCESS:
        dwsize = sizeof(DWORD)
        # int / bool
        for prop in (
            'engine', 'show_millisecs', 'show_menu', 'show_seek', 'show_controls', 'show_status', 'show_playlist', 'theme', 'volume', 'stayontop', 'minimize_to_tray',
            'auto_resize_to_video', 'single_instance', 'remember_playlist', 'use_meta_title'
        ):
            advapi32.RegSetValueExW(hkey, prop, 0, REG_DWORD, byref(DWORD(int(getattr(main, prop)))), dwsize)

        advapi32.RegSetValueExW(hkey, 'splitter_pos', 0, REG_DWORD, byref(DWORD(main.pane.splitter.pos)), dwsize)

        if main.mediaplayer.is_fullscreen():
            main.mediaplayer.set_fullscreen(False)

#        if user32.IsZoomed(main.hwnd):
        main.show(SW_SHOWNORMAL)

        rc = main.get_window_rect()
        buf = create_unicode_buffer(f'({rc.left},{rc.top},{rc.right-rc.left},{rc.bottom-rc.top})')
        advapi32.RegSetValueExW(hkey, 'rect', 0, REG_SZ, buf, sizeof(buf))

        buf = create_unicode_buffer(main.last_playlist)
        advapi32.RegSetValueExW(hkey, 'last_playlist', 0, REG_SZ, buf, sizeof(buf))

        buf = create_unicode_buffer(str(main.color_values))
        advapi32.RegSetValueExW(hkey, 'color_values', 0, REG_SZ, buf, sizeof(buf))

        advapi32.RegCloseKey(hkey)


APP_SETTINGS = load_settings()

if APP_SETTINGS.get('single_instance'):
     # Simple single instance implementation
    hwnd = user32.FindWindowW(APP_CLASS, None)
    if hwnd:
        if len(sys.argv) > 1:
            cds = COPYDATASTRUCT(0, sizeof(WCHAR) * (len(sys.argv[1]) + 1), cast(LPWSTR(sys.argv[1]), LPVOID))
            user32.SendMessageW(hwnd, WM_COPYDATA, 0, byref(cds))
        user32.ShowWindow(hwnd, SW_SHOWNORMAL)
        user32.SetForegroundWindow(hwnd)
        sys.exit(0)


FILTER_DIR = os.path.join(APP_DIR, 'filters')
HAS_DIRECTSHOW = os.path.isfile(os.path.join(FILTER_DIR, 'LAVSplitter.ax'))

VLC_PATH = APP_DIR
HAS_VLC = os.path.isfile(os.path.join(APP_DIR, 'libvlc.dll'))
if not HAS_VLC:
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_LOCAL_MACHINE, 'Software\\VideoLAN\\VLC', byref(hkey)) == ERROR_SUCCESS:
        data_str = (BYTE * MAX_PATH)()
        cbdata_str = DWORD(sizeof(data_str))
        if advapi32.RegQueryValueExW(hkey, 'InstallDir', None, None, data_str, byref(cbdata_str)) == ERROR_SUCCESS:
            VLC_PATH = cast(data_str, LPWSTR).value
            HAS_VLC = os.path.isfile(os.path.join(VLC_PATH, 'libvlc.dll'))
        advapi32.RegCloseKey(hkey)

if 'engine' not in APP_SETTINGS:
    APP_SETTINGS['engine'] = IDM_ENGINE_WEBVIEW
elif APP_SETTINGS['engine'] == IDM_ENGINE_DIRECTSHOW and not HAS_DIRECTSHOW:
    APP_SETTINGS['engine'] = IDM_ENGINE_WEBVIEW
elif APP_SETTINGS['engine'] == IDM_ENGINE_VLC and not HAS_VLC:
    APP_SETTINGS['engine'] = IDM_ENGINE_WEBVIEW

if APP_SETTINGS['engine'] == IDM_ENGINE_DIRECTSHOW:
#    from dshow_player import *
    import dshow_player
    dshow_player.FILTER_DIR = FILTER_DIR
    Player = dshow_player.Player

elif APP_SETTINGS['engine'] == IDM_ENGINE_VLC:
    from vlc_player import *
    vlc.dll = CDLL(os.path.join(VLC_PATH, 'libvlc.dll'))
    vlc.plugin_path = VLC_PATH

else:
    from webview2_player import *

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

# for pip mode
class WINDOWPOS(Structure):
    _fields_ = [
        ("hwnd", HWND),
        ("hwndInsertAfter", HWND),
        ("x", INT),
        ("y", INT),
        ("cx", INT),
        ("cy", INT),
        ("flags", UINT),
    ]

class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ("rgrc", RECT * 3),
        ("lppos", POINTER(WINDOWPOS)),
    ]

BLACK_BRUSH = gdi32.CreateSolidBrush(0x0000000)

########################################
# Returns integer tuple (hours, minutes, seconds, milliseconds)
########################################
def time_to_hms(secs: float) -> tuple:
    h = int(secs / 3600)
    secs -= h * 3600
    m = int(secs / 60)
    secs -= m * 60
    return h, m, int(secs), int(1000 * (secs % 1))


class App(MainWin):

    ########################################
    #
    ########################################
    def __init__(self):

        # Default settings
        self.show_millisecs = False
        self.show_menu = True
        self.show_seek = True
        self.show_controls = True
        self.show_status = True
        self.show_playlist = False
        self.stayontop = False
        self.minimize_to_tray = False
        self.auto_resize_to_video = False
        self.single_instance = False
        self.volume = 75
        self.theme = IDM_THEME_DARK
        self.remember_playlist = False
        self.use_meta_title = False

        if 'rect' in APP_SETTINGS:
            left, top, width, height = eval(APP_SETTINGS['rect'])
            del APP_SETTINGS['rect']
        else:
            left, top, width, height = CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT

        if 'splitter_pos' in APP_SETTINGS:
            splitter_pos = APP_SETTINGS['splitter_pos']
            del APP_SETTINGS['splitter_pos']
        else:
            splitter_pos = 200

        if 'last_playlist' in APP_SETTINGS:
            last_playlist = eval(APP_SETTINGS['last_playlist'])
            del APP_SETTINGS['last_playlist']
        else:
            last_playlist = None

        if 'color_values' in APP_SETTINGS:
            self.color_values = eval(APP_SETTINGS['color_values'])
            del APP_SETTINGS['color_values']
        else:
            self.color_values = {'brightness': 100, 'contrast': 100, 'hue': 100, 'saturation': 100}

        for k, v in APP_SETTINGS.items():
            setattr(self, k, v)

        if self.engine == IDM_ENGINE_DIRECTSHOW:
            self.engine_name = 'DirectShow'
        elif self.engine == IDM_ENGINE_VLC:
            self.engine_name = 'VLC'
        else:
            self.engine_name = 'WebView'

        self.media_file = None
        self.update_counter = 0

        self.is_loop = False
        self.is_mute = False
        self.min_tracksize = POINT(394, 0)
        self.media_duration = 0
        self.time_format = ''
        self.aspect_ratio = IDM_RATIO_DEFAULT
        self.has_playlist = False

        self.COMMAND_MESSAGE_MAP = {
            # File
            IDM_OPEN_FILE:              self.action_open,
            IDM_OPEN_URL:               self.action_open_url,
            IDM_CLOSE:                  self.action_close,
            IDM_SHOW_MEDIAINFOS:        self.action_show_media_infos,
            IDM_OPEN_LOCATION:          self.action_open_location,
            IDM_EXIT:                   lambda: user32.SendMessageW(self.hwnd, WM_CLOSE, 0, 0),

            # Playback
            IDM_PLAY_PAUSE:             self.action_play_pause,
            IDM_STOP:                   self.action_stop,
            IDM_LOOP:                   self.action_toggle_loop,
            IDM_SKIP_BACK:              self.action_skip_back,
            IDM_SKIP_FORWARD:           self.action_skip_forward,
            IDM_STEP_BACK:              self.action_step_back,
            IDM_STEP_FORWARD:           self.action_step_forward,
            IDM_PLAY_PREVIOUS:          self.action_play_previous,
            IDM_PLAY_NEXT:              self.action_play_next,
            IDM_REWIND:                 self.action_rewind,

            # Audio
            IDM_VOLUME_DOWN:            lambda: self.action_change_volume(-VOLUME_STEP),
            IDM_VOLUME_UP:              lambda: self.action_change_volume(VOLUME_STEP),
            IDM_MUTE:                   self.action_toggle_mute,

            # Video
            IDM_ZOOM_50:                lambda: self.action_zoom(.5),
            IDM_ZOOM_100:               lambda: self.action_zoom(1),
            IDM_ZOOM_200:               lambda: self.action_zoom(2),
            IDM_RATIO_DEFAULT:          lambda: self.action_set_aspect_ratio(IDM_RATIO_DEFAULT),
            IDM_RATIO_4_3:              lambda: self.action_set_aspect_ratio(IDM_RATIO_4_3),
            IDM_RATIO_5_4:              lambda: self.action_set_aspect_ratio(IDM_RATIO_5_4),
            IDM_RATIO_16_9:             lambda: self.action_set_aspect_ratio(IDM_RATIO_16_9),
            IDM_RATIO_16_10:            lambda: self.action_set_aspect_ratio(IDM_RATIO_16_10),
            IDM_RATIO_235_100:          lambda: self.action_set_aspect_ratio(IDM_RATIO_235_100),
            IDM_RATIO_185_100:          lambda: self.action_set_aspect_ratio(IDM_RATIO_185_100),
            IDM_RATIO_NONE:             lambda: self.action_set_aspect_ratio(IDM_RATIO_NONE),
            IDM_COLOR_CONTROLS:         self.action_color_controls,
            IDM_SNAPSHOT:               self.action_snapshot,

            # Subtitle
            IDM_LOAD_SUBS:              self.action_load_sub_file,

            # View
            IDM_THEME_AUTO:             lambda: self.action_set_theme(IDM_THEME_AUTO),
            IDM_THEME_LIGHT:            lambda: self.action_set_theme(IDM_THEME_LIGHT),
            IDM_THEME_DARK:             lambda: self.action_set_theme(IDM_THEME_DARK),
            IDM_FULLSCREEN:             self.action_toggle_fullscreen,

            IDM_INTERFACE_MIN:          lambda: self.action_toggle_interface(False),
            IDM_INTERFACE_FULL:         lambda: self.action_toggle_interface(True),

            IDM_SHOW_MENU:              self.action_toggle_menu,
            IDM_SHOW_SEEK:              self.action_toggle_seek,
            IDM_SHOW_CONTROLS:          self.action_toggle_controls,
            IDM_SHOW_STATUS:            self.action_toggle_status,
            IDM_SHOW_PLAYLIST:          self.action_toggle_playlist,

            # Options
            IDM_ENGINE_DIRECTSHOW:      lambda: self.action_set_engine(IDM_ENGINE_DIRECTSHOW),
            IDM_ENGINE_VLC:             lambda: self.action_set_engine(IDM_ENGINE_VLC),
            IDM_ENGINE_WEBVIEW:         lambda: self.action_set_engine(IDM_ENGINE_WEBVIEW),
            IDM_STAY_ON_TOP:            self.action_toggle_stayontop,
            IDM_MINIMIZE_TO_TRAY:       self.action_toggle_minimize_to_tray,
            IDM_AUTO_RESIZE_TO_VIDEO:   self.action_toggle_auto_resize_to_video,
            IDM_SINGLE_INSTANCE:        self.action_toggle_single_instance,
            IDM_REMEMBER_PLAYLIST:      self.action_toggle_remember_playlist,
            IDM_USE_META_TITLE:         self.action_toggle_use_meta_title,

            # Help
            IDM_UPDATE_APP:             self.action_update_app,
            IDM_ABOUT:                  self.action_about,

            # Accelerators
            IDA_ESCAPE:                 self.action_escape_fullscreen,
        }

        super().__init__(
            window_class = APP_CLASS,
            window_title = f'{APP_NAME} [{self.engine_name}]',
            class_style = 0,
            ex_style = WS_EX_ACCEPTFILES,
            h_accel = user32.LoadAcceleratorsW(HMOD_RESOURCES, LPCWSTR(1)),
            h_icon = user32.LoadIconW(HMOD_RESOURCES, LPCWSTR(1)),
            h_brush = COLOR_3DFACE + 1,
            h_menu = user32.LoadMenuW(HMOD_RESOURCES, LPCWSTR(1)),
            left = left, top = top, width = width, height = height,
        )

        # Create a copy of the main menu as popup menu
        self.h_menu_popup = user32.CreatePopupMenu()
        buf = create_unicode_buffer(64)
        mi = MENUITEMINFOW()
        mi.fMask = MIIM_STRING
        mi.dwTypeData = cast(buf, LPWSTR)
        for i in range(user32.GetMenuItemCount(self.h_menu)):
            mi.cch = 64
            user32.GetMenuItemInfoW(self.h_menu, i, TRUE, byref(mi))
            user32.AppendMenuW(self.h_menu_popup, MF_POPUP, user32.GetSubMenu(self.h_menu, i), buf.value)
        user32.AppendMenuW(self.h_menu_popup, MF_SEPARATOR, -1, '')
        user32.AppendMenuW(self.h_menu_popup, MF_STRING, IDM_EXIT, '&Quit\tCtrl+Q')

        if not self.show_menu:
            user32.SetMenu(self.hwnd, None)
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_MENU, MF_BYCOMMAND | MF_UNCHECKED)
        if not self.show_seek:
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_SEEK, MF_BYCOMMAND | MF_UNCHECKED)
        if not self.show_controls:
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_CONTROLS, MF_BYCOMMAND | MF_UNCHECKED)
        if not self.show_status:
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_STATUS, MF_BYCOMMAND | MF_UNCHECKED)

        flag = MF_BYCOMMAND | MF_CHECKED

        user32.CheckMenuItem(self.h_menu, self.theme, MF_BYCOMMAND | MF_CHECKED)
        user32.CheckMenuItem(self.h_menu, self.engine, MF_BYCOMMAND | MF_CHECKED)

        if self.show_playlist:
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_PLAYLIST, flag)

        if self.stayontop:
            user32.CheckMenuItem(self.h_menu, IDM_STAY_ON_TOP, flag)
        if self.minimize_to_tray:
            user32.CheckMenuItem(self.h_menu, IDM_MINIMIZE_TO_TRAY, flag)
        if self.auto_resize_to_video:
            user32.CheckMenuItem(self.h_menu, IDM_AUTO_RESIZE_TO_VIDEO, flag)
        if self.single_instance:
            user32.CheckMenuItem(self.h_menu, IDM_SINGLE_INSTANCE, flag)
#        if self.show_subtitles:
#            user32.CheckMenuItem(self.h_menu, IDM_SHOW_SUBTITLES, flag)
        if self.remember_playlist:
            user32.use_meta_title(self.h_menu, IDM_REMEMBER_PLAYLIST, flag)
        if self.use_meta_title:
            user32.CheckMenuItem(self.h_menu, IDM_USE_META_TITLE, flag)

        if not HAS_DIRECTSHOW:
            user32.EnableMenuItem(self.h_menu, IDM_ENGINE_DIRECTSHOW, MF_BYCOMMAND | MF_GRAYED)

        if not HAS_VLC:
            user32.EnableMenuItem(self.h_menu, IDM_ENGINE_VLC, MF_BYCOMMAND | MF_GRAYED)

        use_dark_mode = self.theme == IDM_THEME_DARK or (self.theme == IDM_THEME_AUTO and reg_should_use_dark_mode())

        self.create_player()
        self.create_seekbar()
        self.create_toolbar(use_dark_mode)
        self.create_statusbar()
        self.create_systray()
        self.create_playlist(splitter_pos)

        if self.engine != IDM_ENGINE_WEBVIEW:
            self.h_menu_audio_tracks = user32.CreateMenu()
            h_menu_audio = user32.GetSubMenu(self.h_menu, IDX_MENU_AUDIO)
            user32.InsertMenuW(h_menu_audio, 0, MF_BYPOSITION | MF_POPUP, self.h_menu_audio_tracks, 'Audio &Track')
            user32.InsertMenuW(h_menu_audio, 1, MF_BYPOSITION | MF_SEPARATOR, self.h_menu_audio_tracks, '')

            self.h_menu_video_tracks = user32.CreateMenu()
            h_menu_video = user32.GetSubMenu(self.h_menu, IDX_MENU_VIDEO)
            user32.InsertMenuW(h_menu_video, 0, MF_BYPOSITION | MF_POPUP, self.h_menu_video_tracks, 'Video &Track')
            user32.InsertMenuW(h_menu_video, 1, MF_BYPOSITION | MF_SEPARATOR, self.h_menu_video_tracks, '')

        self.h_menu_sub_tracks = user32.CreateMenu()
        h_menu_sub = user32.GetSubMenu(self.h_menu, IDX_MENU_SUB)
        user32.InsertMenuW(h_menu_sub, 0, MF_BYPOSITION | MF_POPUP, self.h_menu_sub_tracks, 'Sub &Track')
        user32.InsertMenuW(h_menu_sub, 1, MF_BYPOSITION | MF_SEPARATOR, self.h_menu_sub_tracks, '')

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            if wparam == SIZE_MINIMIZED:
                if self.minimize_to_tray:
                    self.show(SW_HIDE)
                    self.trayicon.show()
                return 0
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self.statusbar.update_size(width)
            self.update_layout(width, height)

        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

        ########################################
        #
        ########################################
        def _on_WM_DROPFILES(hwnd, wparam, lparam):
            self.handle_dropped_items(self.get_dropped_items(wparam))

        self.register_message_callback(WM_DROPFILES, _on_WM_DROPFILES)

        ########################################
        #
        ########################################
        def _on_WM_COPYDATA(hwnd, wparam, lparam):
            cds = cast(lparam, POINTER(COPYDATASTRUCT)).contents
            self.load_media_file(cast(cds.lpData, LPWSTR).value)

        self.register_message_callback(WM_COPYDATA, _on_WM_COPYDATA)

        ########################################
        #
        ########################################
        def _on_WM_COMMAND(hwnd, wparam, lparam):
            if lparam == 0 or lparam == self.toolbar.hwnd:
                command_id = LOWORD(wparam)
                if command_id in self.COMMAND_MESSAGE_MAP:
                    self.COMMAND_MESSAGE_MAP[command_id]()
                return
            control_code = HIWORD(wparam)
            if lparam == self.static_mute.hwnd:
                if control_code == STN_CLICKED:
                    self.action_toggle_mute()

        self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)

        ########################################
        #
        ########################################
        def _on_WM_NOTIFY(hwnd, wparam, lparam):
            mh = cast(lparam, POINTER(NMHDR)).contents
            msg = mh.code

            if mh.hwndFrom == self.statusbar.hwnd:
                if msg == NM_CLICK:
                    nm = cast(lparam, POINTER(NMMOUSE)).contents
                    if nm.dwItemSpec == IDX_STATUSBAR_PART_TIME:
                        self.action_toggle_show_millisecs()

            elif mh.hwndFrom == self.slider_seek.tooltips.hwnd:
                if msg == TTN_GETDISPINFOW:
                    pt = POINT()
                    user32.GetCursorPos(byref(pt))
                    user32.MapWindowPoints(None, self.slider_seek.hwnd, byref(pt), 1)
                    lpnmtdi = cast(lparam, POINTER(NMTTDISPINFOW))
                    h, m, s, ms = time_to_hms(self.media_duration * pt.x / (self.slider_seek.width - 1))
                    if self.media_duration >= 3600:
                        lpnmtdi.contents.szText = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
                    else:
                        lpnmtdi.contents.szText = '{:02d}:{:02d}'.format(m, s)

        self.register_message_callback(WM_NOTIFY, _on_WM_NOTIFY)

        ########################################
        #
        ########################################
        def _on_WM_GETMINMAXINFO(hwnd, wparam, lparam):
            mmi = cast(lparam, POINTER(MINMAXINFO))
            mmi.contents.ptMinTrackSize = self.min_tracksize
            return 0

        self.register_message_callback(WM_GETMINMAXINFO, _on_WM_GETMINMAXINFO)

        ########################################
        #
        ########################################
        def _on_WM_SETTINGCHANGE(hwnd, wparam, lparam):
            if self.theme != IDM_THEME_AUTO:
                return
            if lparam and cast(lparam, LPCWSTR).value == 'ImmersiveColorSet':
                self.apply_theme(reg_should_use_dark_mode())

        self.register_message_callback(WM_SETTINGCHANGE, _on_WM_SETTINGCHANGE)

        ########################################
        #
        ########################################
        def _on_WM_NCHITTEST(hwnd, wparam, lparam):
            hit = user32.DefWindowProcW(hwnd, WM_NCHITTEST, wparam, lparam)
            if hit == HTCLIENT:
                hit = HTCAPTION
            return hit

        self.register_message_callback(WM_NCHITTEST, _on_WM_NCHITTEST)

        self.hide_focus_rects()

        self.update_ui_reset()
        self.update_ui_has_playlist(False)

        if use_dark_mode:
            self.apply_theme(True)

        self.update_min_size(False)
        self.show()

        if self.stayontop:
            self.set_stayontop(True)

        if last_playlist and self.remember_playlist:
            self.playlist.from_list(last_playlist)

        if len(sys.argv) > 1:
            self.create_timer(lambda: self.load_media_file(sys.argv[1]), 0, True)

    ########################################
    #
    ########################################
    def handle_dropped_items(self, dropped_items):
        if len(dropped_items) > 1 or os.path.isdir(dropped_items[0]):
            self.action_close()
            self.playlist.handle_dropped_items(dropped_items)
            if not self.show_playlist:
                self.action_toggle_playlist()
            self.playlist.play_next()
        elif os.path.isfile(dropped_items[0]):
            self.load_media_file(dropped_items[0])
        self.activate_window()

    ########################################
    #
    ########################################
    def update_layout(self, width = None, height = None):
        if height is None:
            rc = self.get_client_rect()
            width, height = rc.right, rc.bottom

        _height = height

        if self.statusbar.visible:
            height -= self.statusbar.height

        # Keep toolbar at bottom
        self.toolbar.set_window_pos(
            0, height - self.toolbar.height,
            width, self.toolbar.height,
            flags = SWP_NOACTIVATE | SWP_NOZORDER
        )

        if self.toolbar.visible:
            height -= self.toolbar.height

        if self.slider_seek.visible:
            height -= (self.slider_seek.height + 6)

        # Reposition and resize the seek trackbar
        self.slider_seek.set_window_pos(3, height + 3, width - 6, self.slider_seek.height)

        # Reposition mute button
        self.static_mute.set_window_pos(width - self.slider_volume.width - 16 - 12, 7, flags = SWP_NOSIZE)

        # Reposition volume trackbar
        self.slider_volume.set_window_pos(width - self.slider_volume.width - 3, 6 + 1, flags = SWP_NOSIZE)

        if self.pane.visible:
            x = max(0, width - self.pane.splitter.pos)

            self.pane.set_window_pos(
                x = x + SPLITTER_SIZE, y = 0,
                width = width - x - SPLITTER_SIZE, height = height,
                flags = SWP_NOZORDER | SWP_NOACTIVATE
            )

            self.pane.splitter.set_window_pos(
                x = x, y = 0,
                width = SPLITTER_SIZE, height = height,
                flags = SWP_NOZORDER | SWP_NOACTIVATE
            )

            width -= self.pane.splitter.pos

        self.video_container.set_window_pos(
            width = width, height = height,
            flags = SWP_NOMOVE | SWP_NOACTIVATE | SWP_NOZORDER
        )

        user32.InvalidateRect(self.hwnd, byref(RECT(0, height, width, _height)), TRUE)

    ########################################
    #
    ########################################
    def update_min_size(self, force=True):
        rc_win = self.get_window_rect()
        rc_win_client = self.get_client_rect()
        self.ui_width = rc_win.right - rc_win.left - rc_win_client.right  # window frame

        if self.show_playlist:
            self.ui_width += self.pane.splitter.pos

        self.ui_height = rc_win.bottom - rc_win.top - rc_win_client.bottom  # title bar, menu, window frame
        if self.show_seek:
            self.ui_height += (self.slider_seek.height + 6)
        if self.show_controls:
            self.ui_height += self.toolbar.height
        if self.show_status:
            self.ui_height += self.statusbar.height
        self.min_tracksize.y = self.ui_height

        if force:
            # Triggers WM_GETMINMAXINFO
            self.set_window_pos(
                width = rc_win.right - rc_win.left,
                height = rc_win.bottom - rc_win.top,
                flags = SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE
            )

    ########################################
    #
    ########################################
    def action_set_engine(self, idm):
        if IS_FROZEN:
            command = f'"{self.media_file}"' if self.media_file else ''
            cwd = None
        else:
            command = 'main.py' + (f' "{self.media_file}"' if self.media_file else '')
            cwd = os.path.dirname(os.path.realpath(__file__))
        self.engine = idm
        user32.SendMessageW(self.hwnd, WM_CLOSE, 0, 0)
        shell32.ShellExecuteW(None, None, sys.executable, command, cwd, SW_SHOWNORMAL)

    ########################################
    #
    ########################################
    def timer_start(self):
        self.create_timer(self._timer_proc, TIME_DISPLAY_UPDATE_PERIOD, timer_id=ID_TIMER_UPDATE_TIME)
        kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)

    ########################################
    #
    ########################################
    def timer_stop(self):
        self.kill_timer(ID_TIMER_UPDATE_TIME)
        kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    ########################################
    #
    ########################################
    def check_menu_item(self, idm, flag):
        user32.CheckMenuItem(self.h_menu, idm, MF_BYCOMMAND | (MF_CHECKED if flag else MF_UNCHECKED))

    ########################################
    #
    ########################################
    def create_player(self):

        self._windowproc_player = WNDPROC(user32.DefWindowProcW)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self._windowproc_player
        newclass.style = CS_DBLCLKS  # CS_VREDRAW | CS_HREDRAW #|
        newclass.lpszClassName = 'VideoContainer'
        newclass.hbrBackground = BLACK_BRUSH
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        user32.RegisterClassExW(byref(newclass))

        self.video_container = Window(
            window_class = newclass.lpszClassName,
            style = WS_CHILD | WS_VISIBLE,
#            ex_style = WS_EX_TRANSPARENT | WS_EX_LAYERED,
            parent_window = self
        )

        self.mediaplayer = Player(
            self.video_container,
            volume = self.volume / 100,
        )

        for k, v in self.color_values.items():
            if v != 100:
                getattr(self.mediaplayer, f'set_{k}')((v - 100) / 100)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):
            if self.media_file:
                self.action_play_pause()

        self.video_container.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)

        ########################################
        #
        ########################################
        def _on_WM_CONTEXTMENU(hwnd, wparam, lparam):
            pt = POINT()
            user32.GetCursorPos(byref(pt))
            user32.TrackPopupMenuEx(self.h_menu_popup, TPM_LEFTBUTTON, pt.x, pt.y, self.hwnd, 0)

        self.video_container.register_message_callback(WM_CONTEXTMENU, _on_WM_CONTEXTMENU)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDBLCLK(hwnd, wparam, lparam):
            self.action_toggle_fullscreen()

        self.video_container.register_message_callback(WM_LBUTTONDBLCLK, _on_WM_LBUTTONDBLCLK)

    ########################################
    #
    ########################################
    def create_seekbar(self):

        self.slider_seek = MySlider(self, height = 16, show_knob = True, show_tooltip = True)

        ########################################
        #
        ########################################
        def _on_seek_pos_changed(pos):
            secs = self.media_duration * pos
            self.mediaplayer.set_time(secs)
            if self._state == STATE_STOPPED:
                self.update_ui_player_state(STATE_PAUSED)
            self.update_time_display(secs)

        self.slider_seek.connect(EVENT_POS_CHANGED, _on_seek_pos_changed)

    ########################################
    #
    ########################################
    def create_toolbar(self, use_dark_mode):
        toolbar_buttons = (
            ('Play', IDM_PLAY_PAUSE, BTNS_BUTTON),
            ('Stop', IDM_STOP, BTNS_BUTTON | BTNS_CHECK),
            ('-'),
            ('Previous', IDM_PLAY_PREVIOUS),
            ('Skip back', IDM_SKIP_BACK),
            ('Skip forward', IDM_SKIP_FORWARD),
            ('Next', IDM_PLAY_NEXT),
            ('-'),
            ('Loop', IDM_LOOP, BTNS_BUTTON | BTNS_CHECK),
        )

        self.toolbar = ToolBar(
            self,
            h_imagelist = comctl32.ImageList_LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_TOOLBAR), 24, 0, CLR_NONE, IMAGE_BITMAP, LR_CREATEDIBSECTION),
            h_imagelist_dark = comctl32.ImageList_LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_TOOLBAR_DARK), 24, 0, CLR_NONE, IMAGE_BITMAP, LR_CREATEDIBSECTION),
            h_imagelist_disabled = comctl32.ImageList_LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_TOOLBAR_DISABLED), 24, 0, CLR_NONE, IMAGE_BITMAP, LR_CREATEDIBSECTION),
            toolbar_buttons = toolbar_buttons,
            style = WS_CHILD | CCS_NODIVIDER | CCS_NOMOVEY | TBSTYLE_TOOLTIPS | TBSTYLE_FLAT | BTNS_AUTOSIZE | (WS_VISIBLE if self.show_controls else 0),
            icon_size = 24,
            hide_text = True,
        )
        self.toolbar.height += 8

        self.toolbar.send_message(TB_SETPADDING, 0, MAKELONG(10, 11))
        self.toolbar.send_message(TB_SETINDENT, 4, 0)

        # Create volume slider and add it to the toolbar
        self.slider_volume = MySlider(self.toolbar, height = 16, width = 102, initial_pos = self.volume / 100, show_text = True)

        ########################################
        #
        ########################################
        def _on_volume_pos_changed(pos):
            self.volume = int(100 * pos)
            if not self.is_mute:
                self.mediaplayer.set_volume(pos)

        self.slider_volume.connect(EVENT_POS_CHANGED, _on_volume_pos_changed)

        ########################################
        #
        ########################################
        def _on_WM_MOUSEWHEEL(hwnd, wparam, lparam):
            self.volume = max(0, min(100, self.volume + VOLUME_STEP * c_short(HIWORD(wparam)).value // 120))
            self.slider_volume.set_pos(self.volume / 100)
            if not self.is_mute:
                self.mediaplayer.set_volume(self.volume / 100)

        self.register_message_callback(WM_MOUSEWHEEL, _on_WM_MOUSEWHEEL)

        # Create mute button
        self.static_mute = Static(
            self.toolbar,
            width = 16, height = 16,
            style = WS_CHILD | WS_VISIBLE | SS_NOTIFY | SS_BITMAP,
            bg_color = 0xf0f0f0,
        )

        user32.SetClassLongPtrW(self.static_mute.hwnd, GCL_HCURSOR, user32.LoadCursorW(0, IDC_HAND))

        # Create tooltip for mute button
        self.static_mute_tooltip = Tooltips(parent_window=self)
        toolInfo = TOOLINFOW()
        toolInfo.uFlags = TTF_IDISHWND | TTF_SUBCLASS
        toolInfo.uId = self.static_mute.hwnd
        toolInfo.lpszText = 'Mute'
        user32.SendMessageW(self.static_mute_tooltip.hwnd, TTM_ADDTOOLW, 0, byref(toolInfo))

        if use_dark_mode:
            self.bitmap_volume = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_DARK), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
            self.bitmap_volume_mute = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_MUTE_DARK), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
        else:
            self.bitmap_volume = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
            self.bitmap_volume_mute = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_MUTE), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)

        self.static_mute.send_message(STM_SETIMAGE, IMAGE_BITMAP, self.bitmap_volume)

    ########################################
    #
    ########################################
    def create_statusbar(self):
        self.statusbar = MyStatusBar(self, self.show_status)

    ########################################
    #
    ########################################
    def create_systray(self):
        self.trayicon = TrayIcon(self, self.h_icon, WM_USER, APP_NAME, show = False)

        ########################################
        #
        ########################################
        def _on_MSG_TRAYICON(hwnd, wparam, lparam):
            msg = LOWORD(lparam)

            if msg == WM_LBUTTONUP:
                self.show(SW_RESTORE)
                self.set_foreground_window()
                self.trayicon.show(False)
                return 0

            elif msg == WM_RBUTTONUP:
                pt = POINT()
                user32.GetCursorPos(byref(pt))
                self.set_foreground_window()
                user32.TrackPopupMenuEx(self.h_menu_popup, TPM_LEFTBUTTON, pt.x, pt.y, self.hwnd, 0)

        self.register_message_callback(WM_USER, _on_MSG_TRAYICON)

    ########################################
    #
    ########################################
    def create_playlist(self, splitter_pos):

        self.pane = Pane(
            self,
            window_title = 'Playlist',
            h_bitmap = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_CLOSE_BUTTON), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION),
            h_bitmap_dark = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_CLOSE_BUTTON_DARK), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION),
            style = WS_CHILD | WS_BORDER | (WS_VISIBLE if self.show_playlist else 0),
            is_right = True,
            initial_pos = splitter_pos,
        )

        self.playlist = PlayList(self, HMOD_RESOURCES)

        self.pane.set_child(self.playlist)

        ########################################
        #
        ########################################
        def _on_splitter_moved():
            rc = self.get_client_rect()
            width, height = rc.right, rc.bottom

            if self.statusbar.visible:
                height -= self.statusbar.height

            if self.toolbar.visible:
                height -= self.toolbar.height

            if self.slider_seek.visible:
                height -= (self.slider_seek.height + 6)

            self.video_container.set_window_pos(
                width = width - self.pane.splitter.pos, height = height,
                flags = SWP_NOMOVE | SWP_NOACTIVATE | SWP_NOZORDER
            )

            self.pane.set_window_pos(
                x = width - self.pane.splitter.pos + SPLITTER_SIZE, y = 0,
                width = self.pane.splitter.pos - SPLITTER_SIZE, height = height,
                flags = SWP_NOZORDER | SWP_NOACTIVATE
            )

        self.pane.splitter.connect(EVENT_SPLITTER_MOVED, _on_splitter_moved)

        ########################################
        #
        ########################################
        def _on_pane_closed():
            self.show_playlist = False
            user32.CheckMenuItem(self.h_menu, IDM_SHOW_PLAYLIST, MF_BYCOMMAND | MF_UNCHECKED)
            self.pane.show(SW_HIDE)
            self.update_layout()
            self.update_min_size()

        self.pane.connect(EVENT_PANE_CLOSE_REQUESTED, _on_pane_closed)

        self.playlist.connect(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, self.update_ui_has_playlist)
        self.playlist.connect(EVENT_PLAYLIST_ACTIVE_ITEM_REMOVED, self.action_close)

        ########################################
        #
        ########################################
        def _load_playlist_item(media_item):
#            if media_item.invalid:
#                self.action_close()
#                return

            ########################################
            #
            ########################################
            def _on_parsed(ok):
                if not ok:
                    self.playlist.set_invalid(media_item)
                    if self.playlist.play_next():
                        self.action_close()

            self.create_timer(lambda: self.load_media_file(media_item.filename, caption = media_item.title, callback = _on_parsed), 0, True)

        self.playlist.connect(EVENT_PLAYLIST_PLAY_ITEM_REQUESTED, _load_playlist_item)

    ########################################
    #
    ########################################
    def action_play_pause(self):
        if self.mediaplayer.is_playing():
            self.timer_stop()
            self.mediaplayer.pause()
            state = STATE_PAUSED
        else:
            self.mediaplayer.play()
            self.timer_start()
            state = STATE_PLAYING

        self.update_ui_player_state(state)

    ########################################
    #
    ########################################
    def action_play_previous(self):
        if not self.playlist.play_previous(True):
            self.action_close()

    ########################################
    #
    ########################################
    def action_play_next(self):
        if not self.playlist.play_next(True):
            self.action_close()

    ########################################
    #
    ########################################
    def action_stop(self):
        self.timer_stop()
        self.mediaplayer.stop()
        self.update_ui_player_state(STATE_STOPPED)

    ########################################
    #
    ########################################
    def action_open(self):
        media_file = show_open_file_dialog(self, 'Open', '.mp4', 'All Files (*.*)\0*.*\0\0')
        if media_file:
            self.load_media_file(media_file)
            self.mediaplayer.play()
        self.activate_window()

    ########################################
    #
    ########################################
    def action_open_url(self):

        ########################################
        #
        ########################################
        def _dialog_proc_enter_url(hwnd, msg, wparam, lparam):
            if msg == WM_INITDIALOG:
                if self.is_dark:
                    dwm_use_dark_mode(hwnd, True)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDOK), 'DarkMode_Explorer', None)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDCANCEL), 'DarkMode_Explorer', None)
                hwnd_edit = user32.GetDlgItem(hwnd, IDC_EDIT_FILENAME)
                user32.SetWindowLongA(hwnd_edit, GWL_EXSTYLE, user32.GetWindowLongA(hwnd_edit, GWL_EXSTYLE) & ~WS_EX_STATICEDGE & ~WS_EX_CLIENTEDGE)
                user32.SetWindowLongA(hwnd_edit, GWL_STYLE, user32.GetWindowLongA(hwnd_edit, GWL_STYLE) | WS_BORDER)
                user32.SetWindowPos(hwnd_edit, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
                center_window(hwnd, self.hwnd)
                user32.SetFocus(hwnd_edit)

            elif msg == WM_COMMAND:
                control_id = LOWORD(wparam)
                command = HIWORD(wparam)
                if command == BN_CLICKED:
                    if control_id == IDOK:
                        hwnd_edit = user32.GetDlgItem(hwnd, IDC_EDIT_FILENAME)
                        text_len = user32.SendMessageW(hwnd_edit, WM_GETTEXTLENGTH, 0, 0) + 1
                        if text_len > 1:
                            text_buf = create_unicode_buffer(text_len)
                            user32.SendMessageW(hwnd_edit, WM_GETTEXT, text_len, text_buf)
                            media_url = text_buf.value
                            if not media_url.startswith('http'):
                                media_url = f'https://{media_url}'
                            self.statusbar.set_text('Loading...', IDX_STATUSBAR_PART_STATE)
                            self.create_timer(lambda: self.load_media_file(media_url), 0, True)
                    user32.EndDialog(hwnd, 0)

            elif self.is_dark:
                if msg == WM_CTLCOLORDLG:
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORSTATIC:
                    gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORBTN:
                    gdi32.SetDCBrushColor(wparam, DARK_BG_COLOR)
                    return gdi32.GetStockObject(DC_BRUSH)
                elif msg == WM_CTLCOLOREDIT:
                    gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
                    gdi32.SetBkColor(wparam, DARK_CONTROL_BG_COLOR)
                    gdi32.SetDCBrushColor(wparam, DARK_CONTROL_BG_COLOR)
                    return gdi32.GetStockObject(DC_BRUSH)

            return FALSE

        dialog_proc = WNDPROC(_dialog_proc_enter_url)

        user32.DialogBoxParamW(
            HMOD_RESOURCES,
            MAKEINTRESOURCEW(IDD_OPEN_URL),
            self.hwnd,
            dialog_proc,
            NULL
        )

    ########################################
    #
    ########################################
    def action_load_sub_file(self):
        sub_file = show_open_file_dialog(self, 'Load Subtitles', '.srt',
            'Subtitle files (*.srt;*.webvtt;*.vtt)\0*.srt;*.webvtt;*.vtt\0\0')
        if sub_file:
#            try:

            ok = self.mediaplayer.load_sub_file(sub_file)
            if not ok:
                return

            ok = TRUE
            while ok:
                ok = user32.RemoveMenu(self.h_menu_sub_tracks, 0, MF_BYPOSITION)

            self._active_sub_track_id = None
            sub_tracks = self.mediaplayer.get_sub_tracks()
            if sub_tracks:
                user32.AppendMenuW(self.h_menu_sub_tracks, MF_STRING, IDM_SUB_TRACK, 'Disable')
                self.COMMAND_MESSAGE_MAP[IDM_SUB_TRACK] = lambda: self.action_select_sub_track(-1)
                for track in sub_tracks:
#                        print(track)
                    track_id, name, enabled = track
                    idm = IDM_SUB_TRACK + 1 + track_id
                    self.COMMAND_MESSAGE_MAP[idm] = lambda track_id=track_id: self.action_select_sub_track(track_id)
                    user32.AppendMenuW(self.h_menu_sub_tracks, MF_STRING | (MF_CHECKED if enabled else 0), idm, name)
                    if enabled:
                        self._active_sub_track_id = track_id

                user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_SUB), 0, MF_BYPOSITION | MF_ENABLED)
#            except:
#                print('mediaplayer.load_subtitles failed')

        self.activate_window()

    ########################################
    #
    ########################################
    def action_open_location(self):
        if self.media_file is None or '://' in self.media_file:
            return
        shell32.ShellExecuteW(None, None, 'explorer.exe', f'/select,"{self.media_file}"', None, SW_SHOWNORMAL)

    ########################################
    #
    ########################################
    def action_close(self):
        if self.mediaplayer.is_fullscreen():
            self.action_toggle_fullscreen()
        self.timer_stop()
        self.media_file = None
        self.media_duration = 0
        self.mediaplayer.close_file()

        self.set_window_text(f'{APP_NAME} [{self.engine_name}]')
        self.trayicon.set_tooltip(f'{APP_NAME} [{self.engine_name}]')
        self.statusbar.set_text('Closed', IDX_STATUSBAR_PART_STATE)
        self.statusbar.set_text('', IDX_STATUSBAR_PART_TIME)

        self.update_ui_reset()

    ########################################
    #
    ########################################
    def action_about(self):

        ########################################
        #
        ########################################
        def _dialog_proc_about(hwnd, msg, wparam, lparam):

            if msg == WM_INITDIALOG:
                if self.is_dark:
                    dwm_use_dark_mode(hwnd, True)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDOK), 'DarkMode_Explorer', None)
                center_window(hwnd, self.hwnd)

            elif msg == WM_COMMAND:
                command = HIWORD(wparam)
                if command == BN_CLICKED:
                    user32.EndDialog(hwnd, 0)

            elif msg == WM_NOTIFY:
                mh = cast(lparam, POINTER(NMHDR)).contents
                msg = mh.code
                if msg == NM_CLICK:
                    shell32.ShellExecuteW(None, None, 'https://github.com/59de44955ebd/SMP', None, None, SW_SHOWNORMAL)

            elif self.is_dark:
                if msg == WM_CTLCOLORDLG:
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORSTATIC:
                    gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORBTN:
                    gdi32.SetDCBrushColor(wparam, DARK_BG_COLOR)
                    return gdi32.GetStockObject(DC_BRUSH)

            return FALSE

        dialog_proc = WNDPROC(_dialog_proc_about)

        user32.DialogBoxParamW(
            HMOD_RESOURCES,
            MAKEINTRESOURCEW(IDD_ABOUT),
            None,
            dialog_proc,
            NULL
        )

    ########################################
    #
    ########################################
    def action_snapshot(self):
        t = self.mediaplayer.get_time()
        tmp_file = os.path.join(os.environ['TMP'], '~smpcapture')

        ########################################
        #
        ########################################
        def _on_snapshot(image_type):
            if image_type:
                ext = image_type.lower()
                filename = f'{os.path.basename(self.media_file)}_snapshot_{t:.3f}'
                img_file = show_save_file_dialog(self, 'Save', f'.{ext}', f'{image_type} Files\0*.{ext}\0\0', filename)
                if img_file:
                    if os.path.isfile(img_file):
                        os.unlink(img_file)
                    os.rename(tmp_file, img_file)
                else:
                    os.unlink(tmp_file)

        self.mediaplayer.take_snapshot(tmp_file, _on_snapshot)

    ########################################
    #
    ########################################
    def action_change_volume(self, step):
        self.volume = max(0, min(100, self.volume + step))
#        self.slider_volume.send_message(TBM_SETPOS, 1, self.volume)
        self.slider_volume.set_pos(self.volume / 100)
        if not self.is_mute:
            self.mediaplayer.set_volume(self.volume / 100)

    ########################################
    #
    ########################################
    def action_update_app(self):
        command = f'"{os.path.join(RES_DIR, "update_app.ps1")}" "{APP_NAME}" {APP_VERSION} "https://github.com/59de44955ebd/{APP_NAME}"'
        if os.path.isfile(os.path.join(os.path.dirname(sys.executable), 'uninstall.exe')):
            command += f' "{APP_NAME}-x64-setup.exe"'
        shell32.ShellExecuteW(None, None, 'powershell.exe', command, None, SW_HIDE)

    ########################################
    #
    ########################################
    def action_color_controls(self):
        sliders = {}
        statics = {}

        ########################################
        #
        ########################################
        def _dialog_proc_color_controls(hwnd, msg, wparam, lparam):
            if msg == WM_INITDIALOG:
                if self.is_dark:
                    dwm_use_dark_mode(hwnd, True)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDC_BTN_RESET), 'DarkMode_Explorer', None)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDCANCEL), 'DarkMode_Explorer', None)
                for i, k in enumerate(['brightness', 'contrast', 'hue', 'saturation']):
                    hwnd_slider = user32.GetDlgItem(hwnd, [IDC_CC_TRACKBAR_BRIGHTNESS, IDC_CC_TRACKBAR_CONTRAST, IDC_CC_TRACKBAR_HUE, IDC_CC_TRACKBAR_SATURATION][i])
                    user32.SendMessageW(hwnd_slider, TBM_SETRANGEMAX, FALSE, 200)
                    user32.SendMessageW(hwnd_slider, TBM_SETPOS, TRUE, self.color_values[k])
                    sliders[k] = hwnd_slider
                    statics[k] = user32.GetDlgItem(hwnd, [IDC_CC_STATIC_BRIGHTNESS, IDC_CC_STATIC_CONTRAST, IDC_CC_STATIC_HUE, IDC_CC_STATIC_SATURATION][i])
                    user32.SetWindowTextW(statics[k], str(self.color_values[k] - 100))
                center_window(hwnd, self.hwnd)

            elif msg == WM_COMMAND:
                control_id = LOWORD(wparam)
                command = HIWORD(wparam)
                if command == BN_CLICKED:
                    if control_id == IDC_BTN_RESET:
                        for k, hwnd_slider in sliders.items():
                            self.color_values[k] = 100
                            getattr(self.mediaplayer, f'set_{k}')(0)
                            user32.SendMessageW(hwnd_slider, TBM_SETPOS, TRUE, 100)
                            user32.SetWindowTextW(statics[k], '0')

                    elif control_id == IDCANCEL:
                        user32.EndDialog(hwnd, 0)

            elif msg == WM_HSCROLL:
                lo, hi, = wparam & 0xFFFF, (wparam >> 16) & 0xFFFF
                if lo == TB_ENDTRACK:
                    return 0

                if lo == TB_PAGEDOWN or lo == TB_PAGEUP:  # Click on slider
                    pt = POINT()
                    user32.GetCursorPos(byref(pt))
                    rc = RECT()
                    user32.GetWindowRect(lparam, byref(rc))
                    hi = int((pt.x - rc.left - 10) / (rc.right - rc.left - 20) * 200)
                    user32.SendMessageW(lparam, TBM_SETPOS, TRUE, hi)

                elif lo == TB_THUMBTRACK or lo == TB_THUMBPOSITION:
                    hi = SHORT(hi).value

                idx = list(sliders.values()).index(lparam)
                k = list(sliders.keys())[idx]
                self.color_values[k] = hi
                getattr(self.mediaplayer, f'set_{k}')((hi - 100) / 100)  # -1..1
                user32.SetWindowTextW(statics[k], str(hi - 100))  # -100 .. 100

            elif self.is_dark:
                if msg == WM_CTLCOLORDLG:
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORSTATIC:
                    gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORBTN:
                    gdi32.SetDCBrushColor(wparam, DARK_BG_COLOR)
                    return gdi32.GetStockObject(DC_BRUSH)

            return FALSE

        dialog_proc = WNDPROC(_dialog_proc_color_controls)

        user32.DialogBoxParamW(
            HMOD_RESOURCES,
            MAKEINTRESOURCEW(IDD_COLOR_CONTROLS),
            None,
            dialog_proc,
            NULL
        )

    ########################################
    #
    ########################################
    def action_show_media_infos(self):

        class ctx:
            pass

        h_font = gdi32.CreateFontW(
            -kernel32.MulDiv(8, DPI_Y, 72), 0, 0, 0, FW_DONTCARE, FALSE, FALSE, FALSE, ANSI_CHARSET, OUT_TT_PRECIS,
            CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, 'Consolas'
        )

        ########################################
        #
        ########################################
        def _dialog_proc_media_infos(hwnd, msg, wparam, lparam):

            if msg == WM_INITDIALOG:
                ctx.hwnd_edit = user32.GetDlgItem(hwnd, IDC_EDIT_FILENAME)
                if self.is_dark:
                    dwm_use_dark_mode(hwnd, True)
                    uxtheme.SetWindowTheme(ctx.hwnd_edit, 'DarkMode_Explorer', None)
                user32.SendMessageW(ctx.hwnd_edit, WM_SETFONT, h_font, MAKELPARAM(1, 0))
                user32.SendMessageW(ctx.hwnd_edit, EM_SETMARGINS, EC_LEFTMARGIN, 10)
                infos = pymediainfo.MediaInfo.parse(self.media_file, output='text', full=False, cover_data=False)
                user32.SetWindowTextW(ctx.hwnd_edit, '\r\n' + infos)
                center_window(hwnd, self.hwnd)

            elif msg == WM_SIZE:
                width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                user32.SetWindowPos(ctx.hwnd_edit, 0, 0, 0, width, height, SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE)

            elif msg == WM_COMMAND:
                control_id = LOWORD(wparam)
                command = HIWORD(wparam)
                if control_id == IDCANCEL:
                    user32.EndDialog(hwnd, 0)
                elif command == EN_SETFOCUS:
                    user32.SendMessageW(ctx.hwnd_edit, EM_SETSEL, 0, 0)

            elif self.is_dark:
                if msg == WM_CTLCOLORDLG:
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH
                elif msg == WM_CTLCOLORSTATIC:
                    gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
                    gdi32.SetBkColor(wparam, DARK_BG_COLOR)
                    return DARK_BG_BRUSH

            return FALSE

        dialog_proc = WNDPROC(_dialog_proc_media_infos)

        user32.DialogBoxParamW(
            HMOD_RESOURCES,
            MAKEINTRESOURCEW(IDD_MEDIA_INFOS),
            None, #self.hwnd,
            dialog_proc,
            NULL
        )

        gdi32.DeleteObject(h_font)

    ########################################
    #
    ########################################
    def action_skip_back(self):
        if self.media_file is None:
            return
        self.mediaplayer.skip_back(.5)
        self.update_time(True)

    ########################################
    #
    ########################################
    def action_skip_forward(self):
        if self.media_file is None:
            return
        self.mediaplayer.skip_forward(.5)
        self.update_time(True)

    ########################################
    #
    ########################################
    def action_step_back(self):
        if self.media_file is None:
            return
        self.mediaplayer.step_back(1)
        self.update_time(True)

    ########################################
    #
    ########################################
    def action_step_forward(self):
        if self.media_file is None:
            return
        self.mediaplayer.step_forward(1)
        self.update_time(True)

    ########################################
    #
    ########################################
    def action_rewind(self):
        if self.media_file is None:
            return
        self.mediaplayer.set_time(0)
        self.update_time(True)

    ########################################
    #
    ########################################
    def action_toggle_fullscreen(self):
        if self.media_file is None or not self.mediaplayer.has_video():
            return
        fullscreen = not self.mediaplayer.is_fullscreen()
        if self.stayontop:
            self.set_stayontop(not fullscreen)
        self.mediaplayer.set_fullscreen(fullscreen)
        user32.ShowCursor(int(not fullscreen))

    ########################################
    #
    ########################################
    def action_escape_fullscreen(self):
        if self.media_file is None or not self.mediaplayer.has_video():
            return
        self.mediaplayer.set_fullscreen(False)
        user32.ShowCursor(TRUE)

    ########################################
    #
    ########################################
    def action_toggle_interface(self, show_ui):
        for idm in (IDM_SHOW_MENU, IDM_SHOW_SEEK, IDM_SHOW_CONTROLS, IDM_SHOW_STATUS):
            self.check_menu_item(idm, show_ui)
        self.show_menu = self.show_seek = self.show_controls = self.show_status = show_ui
        user32.SetMenu(self.hwnd, self.h_menu if show_ui else None)
        self.check_menu_item(IDM_SHOW_SEEK, self.show_seek)
        show = int(show_ui)
        self.slider_seek.show(show)
        self.toolbar.show(show)
        self.statusbar.show(show)
        self.update_layout()
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_stayontop(self):
        self.stayontop = not self.stayontop
        self.set_stayontop(self.stayontop)
        self.check_menu_item(IDM_STAY_ON_TOP, self.stayontop)

    ########################################
    #
    ########################################
    def action_set_aspect_ratio(self, idm):
        user32.CheckMenuItem(self.h_menu, self.aspect_ratio, MF_BYCOMMAND | MF_UNCHECKED)
        self.aspect_ratio = idm
        user32.CheckMenuItem(self.h_menu, self.aspect_ratio, MF_BYCOMMAND | MF_CHECKED)
        self.mediaplayer.set_aspect_ratio(RATIOS[idm])

    ########################################
    #
    ########################################
    def action_toggle_show_millisecs(self):
        self.show_millisecs = not self.show_millisecs
        self.update_time_format()
        if self.media_file:
            self.update_time(True)

    ########################################
    #
    ########################################
    def action_toggle_menu(self):
        self.show_menu = not self.show_menu
        self.check_menu_item(IDM_SHOW_MENU, self.show_menu)
        user32.SetMenu(self.hwnd, self.h_menu if self.show_menu else None)
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_seek(self):
        self.show_seek = not self.show_seek
        self.check_menu_item(IDM_SHOW_SEEK, self.show_seek)
        self.slider_seek.show(int(self.show_seek))
        self.update_layout()
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_controls(self):
        self.show_controls = not self.show_controls
        self.check_menu_item(IDM_SHOW_CONTROLS, self.show_controls)
        self.toolbar.show(int(self.show_controls))
        self.update_layout()
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_status(self):
        self.show_status = not self.show_status
        self.check_menu_item(IDM_SHOW_STATUS, self.show_status)
        self.statusbar.show(int(self.show_status))
        self.update_layout()
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_playlist(self):
        self.show_playlist = not self.show_playlist
        self.check_menu_item(IDM_SHOW_PLAYLIST, self.show_playlist)
        self.pane.show(int(self.show_playlist))
        self.update_layout()
        self.update_min_size()

    ########################################
    #
    ########################################
    def action_toggle_minimize_to_tray(self):
        self.minimize_to_tray = not self.minimize_to_tray
        self.check_menu_item(IDM_MINIMIZE_TO_TRAY, self.minimize_to_tray)

    ########################################
    #
    ########################################
    def action_toggle_auto_resize_to_video(self):
        self.auto_resize_to_video = not self.auto_resize_to_video
        self.check_menu_item(IDM_AUTO_RESIZE_TO_VIDEO, self.auto_resize_to_video)
        if self.auto_resize_to_video:
            self.action_zoom(1)

    ########################################
    #
    ########################################
    def action_toggle_single_instance(self):
        self.single_instance = not self.single_instance
        hkey = HKEY()
        if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\59de44955ebd\\{APP_NAME}', byref(hkey)) == ERROR_SUCCESS:
            dwsize = sizeof(DWORD)
            advapi32.RegSetValueExW(hkey, 'single_instance', 0, REG_DWORD, byref(DWORD(int(self.single_instance))), dwsize)
            advapi32.RegCloseKey(hkey)
        self.check_menu_item(IDM_SINGLE_INSTANCE, self.single_instance)

    ########################################
    #
    ########################################
    def action_toggle_remember_playlist(self):
        self.remember_playlist = not self.remember_playlist
        self.check_menu_item(IDM_REMEMBER_PLAYLIST, self.remember_playlist)

    ########################################
    #
    ########################################
    def action_toggle_use_meta_title(self):
        self.use_meta_title = not self.use_meta_title
        self.check_menu_item(IDM_USE_META_TITLE, self.use_meta_title)
        if self.media_file:
            if self.use_meta_title:
               try:
                    meta = json.loads(pymediainfo.MediaInfo.parse(self.media_file, output='JSON', full=False, cover_data=False))
                    self.set_window_text(f'{meta["media"]["track"][0]["Title"]} - {APP_NAME} [{self.engine_name}]')
                    return
               except:
                    pass
            self.set_window_text(f'{os.path.basename(self.media_file)} - {APP_NAME} [{self.engine_name}]')

    ########################################
    #
    ########################################
    def action_toggle_loop(self):
        self.is_loop = not self.is_loop
        self.check_menu_item(IDM_LOOP, self.is_loop)
        self.toolbar.send_message(TB_CHECKBUTTON, IDM_LOOP, self.is_loop)
        self.mediaplayer.set_loop(self.is_loop)

    ########################################
    #
    ########################################
    def action_toggle_mute(self):
        self.is_mute = not self.is_mute
        self.check_menu_item(IDM_MUTE, self.is_mute)
        if self.is_mute:
            self.mediaplayer.set_volume(0)
        else:
            self.mediaplayer.set_volume(self.volume / 100)
        self.static_mute.send_message(STM_SETIMAGE, IMAGE_BITMAP, self.bitmap_volume_mute if self.is_mute else self.bitmap_volume)
        self.toolbar.redraw_window()

    ########################################
    #
    ########################################
    def action_set_theme(self, idm):
        user32.CheckMenuItem(self.h_menu, self.theme, MF_BYCOMMAND | MF_UNCHECKED)
        self.theme = idm
        user32.CheckMenuItem(self.h_menu, self.theme, MF_BYCOMMAND | MF_CHECKED)

        if idm == IDM_THEME_AUTO:
            is_dark = reg_should_use_dark_mode()
        else:
            is_dark = idm == IDM_THEME_DARK

        if is_dark != self.is_dark:
            self.apply_theme(is_dark)

            if self.is_dark:
                self.bitmap_volume = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_DARK), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
                self.bitmap_volume_mute = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_MUTE_DARK), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
            else:
                self.bitmap_volume = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
                self.bitmap_volume_mute = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDB_VOLUME_MUTE), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)

            self.static_mute.send_message(STM_SETIMAGE, IMAGE_BITMAP, self.bitmap_volume_mute if self.is_mute else self.bitmap_volume)

            self.toolbar.redraw_window()

    ########################################
    #
    ########################################
    def action_zoom(self, factor):
        if user32.IsZoomed(self.hwnd):
            self.show(SW_RESTORE)
        w, h = self.mediaplayer.get_size()
        w, h = int(w * factor) + self.ui_width, int(h * factor) + self.ui_height
        self.set_window_pos(width = w, height = h, flags = SWP_NOMOVE)

    ########################################
    #
    ########################################
    def load_media_file(self, filename, caption=None, callback=None):
        had_media = self.media_file is not None
        if had_media:
            self.action_close()

#        was_playing = self.mediaplayer.is_playing()
#        if was_playing:
#            self.timer_stop()

        is_url = '://' in filename
        if not is_url:
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.lnk':
                filename = get_lnk_infos(filename)[0]
            elif ext in ('.m3u', '.pls'):
                self.playlist.load_playlist(filename)
                if not self.show_playlist:
                    self.action_toggle_playlist()
                self.playlist.play_next()
                return

        ########################################
        #
        ########################################
        def _on_parsed(ok):
            if callback:
                callback(ok)
            if not ok:
                return  #self.action_close()

            self.media_file = filename

            self.set_window_text(f'{caption if caption else os.path.basename(filename)} - {APP_NAME} [{self.engine_name}]')
            self.trayicon.set_tooltip(f'{caption if caption else os.path.basename(filename)} - {APP_NAME} [{self.engine_name}]')

            self.update_counter = 0

            self.media_duration = self.mediaplayer.get_duration()
            self.update_time_format()

            has_video = self.mediaplayer.has_video()
            if has_video:
                w, h = self.mediaplayer.get_size()

                if self.auto_resize_to_video and not is_url and not user32.IsZoomed(self.hwnd):
                    self.set_window_pos(width = self.ui_width + w, height = self.ui_height + h, flags = SWP_NOMOVE)

                self._active_sub_track_id = None
                sub_tracks = self.mediaplayer.get_sub_tracks()
                if sub_tracks:
                    user32.AppendMenuW(self.h_menu_sub_tracks, MF_STRING, IDM_SUB_TRACK, 'Disable')
                    self.COMMAND_MESSAGE_MAP[IDM_SUB_TRACK] = lambda: self.action_select_sub_track(-1)
                    for track in sub_tracks:
                        track_id, name, enabled = track
                        idm = IDM_SUB_TRACK + 1 + track_id
                        self.COMMAND_MESSAGE_MAP[idm] = lambda track_id=track_id: self.action_select_sub_track(track_id)
                        user32.AppendMenuW(self.h_menu_sub_tracks, MF_STRING | (MF_CHECKED if enabled else 0), idm, name)
                        if enabled:
                            self._active_sub_track_id = track_id

                    user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_SUB), 0, MF_BYPOSITION | MF_ENABLED)

                if self.engine != IDM_ENGINE_WEBVIEW:
                    self._active_video_track_id = None
                    video_tracks = self.mediaplayer.get_video_tracks()
                    if video_tracks:
                        for track in video_tracks:
                            track_id, name, enabled = track
                            idm = IDM_VIDEO_TRACK + 1 + track_id
                            self.COMMAND_MESSAGE_MAP[idm] = lambda track_id=track_id: self.action_select_video_track(track_id)
                            user32.AppendMenuW(self.h_menu_video_tracks, MF_STRING | (MF_CHECKED if enabled else 0), idm, name)
                            if enabled:
                                self._active_video_track_id = track_id
                        user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_VIDEO), 0, MF_BYPOSITION | MF_ENABLED)

            self.mediaplayer.play()
            self.timer_start()

            self.update_ui_has_media(has_video, self.media_duration > 0, is_url)

#            if not was_playing:
            self.update_ui_player_state(STATE_PLAYING)

            if self.use_meta_title and caption is None:
                try:
                    meta = json.loads(pymediainfo.MediaInfo.parse(self.media_file, output='JSON', full=False, cover_data=False))
                    self.set_window_text(f'{meta["media"]["track"][0]["Title"]} - {APP_NAME} [{self.engine_name}]')
                except:
                    pass


            if self.engine != IDM_ENGINE_WEBVIEW:
                self._active_audio_track_id = None
                audio_tracks = self.mediaplayer.get_audio_tracks()
                if audio_tracks:
                    for track in audio_tracks:
                        track_id, name, enabled = track
                        idm = IDM_AUDIO_TRACK + 1 + track_id
                        self.COMMAND_MESSAGE_MAP[idm] = lambda track_id=track_id: self.action_select_audio_track(track_id)
                        user32.AppendMenuW(self.h_menu_audio_tracks, MF_STRING | (MF_CHECKED if enabled else 0), idm, name)
                        if enabled:
                            self._active_audio_track_id = track_id
                    user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_AUDIO), 0, MF_BYPOSITION | MF_ENABLED)

        # Make the callback return immediately (needed for VLC)
        self.mediaplayer.load_media_file(filename, on_parsed = lambda ok: self.create_timer(lambda: _on_parsed(ok), 0, True))

    ########################################
    #
    ########################################
    def action_select_audio_track(self, track_id):
        if track_id == self._active_audio_track_id:
            return

        self.mediaplayer.select_audio_track(track_id)

        if self._active_audio_track_id is not None:
            idm = IDM_AUDIO_TRACK + 1 + self._active_audio_track_id
            user32.CheckMenuItem(self.h_menu_audio_tracks, idm, MF_BYCOMMAND | MF_UNCHECKED)

        self._active_audio_track_id = track_id
        user32.CheckMenuItem(self.h_menu_audio_tracks, IDM_AUDIO_TRACK + 1 + track_id, MF_BYCOMMAND | MF_CHECKED)

    ########################################
    #
    ########################################
    def action_select_video_track(self, track_id):
        if track_id == self._active_video_track_id:
            return

        self.mediaplayer.select_video_track(track_id)

        if self._active_video_track_id is not None:
            idm = IDM_VIDEO_TRACK + 1 + self._active_video_track_id
            user32.CheckMenuItem(self.h_menu_video_tracks, idm, MF_BYCOMMAND | MF_UNCHECKED)

        self._active_video_track_id = track_id
        user32.CheckMenuItem(self.h_menu_video_tracks, IDM_VIDEO_TRACK + 1 + track_id, MF_BYCOMMAND | MF_CHECKED)

    ########################################
    #
    ########################################
    def action_select_sub_track(self, track_id):
        if track_id == self._active_sub_track_id:
            return

        self.mediaplayer.select_sub_track(track_id)

        if self._active_sub_track_id is not None:
            idm = IDM_SUB_TRACK + 1 + self._active_sub_track_id
            user32.CheckMenuItem(self.h_menu_sub_tracks, idm, MF_BYCOMMAND | MF_UNCHECKED)

        self._active_sub_track_id = track_id
        user32.CheckMenuItem(self.h_menu_sub_tracks, IDM_SUB_TRACK + 1 + track_id, MF_BYCOMMAND | MF_CHECKED)

    ########################################
    #
    ########################################
    def update_ui_reset(self):
        self.slider_seek.enable_window(False)
        for idm in (IDM_PLAY_PAUSE, IDM_STOP, IDM_SKIP_BACK, IDM_SKIP_FORWARD):
            self.toolbar.send_message(TB_ENABLEBUTTON, idm, FALSE)
        for idm in (
            IDM_PLAY_PAUSE, IDM_STOP, IDM_CLOSE, IDM_SNAPSHOT, IDM_SHOW_MEDIAINFOS,
            IDM_SKIP_BACK, IDM_SKIP_FORWARD, IDM_STEP_BACK, IDM_STEP_FORWARD, IDM_REWIND,
            IDM_FULLSCREEN, IDM_LOAD_SUBS, IDM_OPEN_LOCATION, IDM_SHOW_MEDIAINFOS,
            IDM_ZOOM_50, IDM_ZOOM_100, IDM_ZOOM_200
        ):
            user32.EnableMenuItem(self.h_menu, idm, MF_BYCOMMAND | MF_GRAYED)

        taskbar.SetProgressState(self.hwnd, TBPF.NOPROGRESS)
        self._state = STATE_STOPPED

        if self.engine != IDM_ENGINE_WEBVIEW:
            ok = TRUE
            while ok:
                ok = user32.RemoveMenu(self.h_menu_audio_tracks, 0, MF_BYPOSITION)
            user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_AUDIO), 0, MF_BYPOSITION | MF_GRAYED)

            ok = TRUE
            while ok:
                ok = user32.RemoveMenu(self.h_menu_video_tracks, 0, MF_BYPOSITION)
            user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_VIDEO), 0, MF_BYPOSITION | MF_GRAYED)

        ok = TRUE
        while ok:
            ok = user32.RemoveMenu(self.h_menu_sub_tracks, 0, MF_BYPOSITION)
        user32.EnableMenuItem(user32.GetSubMenu(self.h_menu, IDX_MENU_SUB), 0, MF_BYPOSITION | MF_GRAYED)

    ########################################
    #
    ########################################
    def update_ui_has_media(self, has_video, has_duration, is_url):
        self.slider_seek.enable_window(has_duration)

        for idm in (IDM_PLAY_PAUSE, IDM_STOP):
            self.toolbar.send_message(TB_ENABLEBUTTON, idm, TRUE)
        for idm in (IDM_SKIP_BACK, IDM_SKIP_FORWARD):
            self.toolbar.send_message(TB_ENABLEBUTTON, idm, int(has_duration))

        state = MF_BYCOMMAND | MF_ENABLED
        for idm in (IDM_PLAY_PAUSE, IDM_STOP, IDM_CLOSE, IDM_SNAPSHOT, IDM_SHOW_MEDIAINFOS):
            user32.EnableMenuItem(self.h_menu, idm, state)

        state = MF_BYCOMMAND | (MF_ENABLED if has_video else MF_GRAYED)
        for idm in (IDM_FULLSCREEN, IDM_ZOOM_50, IDM_ZOOM_100, IDM_ZOOM_200):
            user32.EnableMenuItem(self.h_menu, idm, state)

        state = MF_BYCOMMAND | (MF_ENABLED if has_duration else MF_GRAYED)
        for idm in (IDM_SKIP_BACK, IDM_SKIP_FORWARD, IDM_STEP_BACK, IDM_STEP_FORWARD, IDM_REWIND):
            user32.EnableMenuItem(self.h_menu, idm, state)

        state = MF_BYCOMMAND | (MF_ENABLED if not is_url else MF_GRAYED)
        user32.EnableMenuItem(self.h_menu, IDM_OPEN_LOCATION, state)

        state = MF_BYCOMMAND | (MF_ENABLED if has_video and not is_url else MF_GRAYED)
        user32.EnableMenuItem(self.h_menu, IDM_LOAD_SUBS, state)

    ########################################
    #
    ########################################
    def update_ui_player_state(self, state):
        self.toolbar.send_message(TB_CHECKBUTTON, IDM_STOP, int(state == STATE_STOPPED))

        tbi = TBBUTTONINFOW()
        tbi.dwMask = TBIF_IMAGE | TBIF_TEXT

        if state == STATE_STOPPED:
#            self.slider_seek.send_message(TBM_SETPOS, 1, 0)
            self.slider_seek.set_pos(0)
            self.statusbar.set_text('Stopped', IDX_STATUSBAR_PART_STATE)
            self.statusbar.set_text('', IDX_STATUSBAR_PART_TIME)
            tbi.iImage = 0
            tbi.pszText  = 'Play'
            taskbar.SetProgressState(self.hwnd, TBPF.NOPROGRESS)

        elif state == STATE_PAUSED:
            self.statusbar.set_text('Paused', IDX_STATUSBAR_PART_STATE)
            tbi.iImage = 0
            tbi.pszText  = 'Play'
            taskbar.SetProgressState(self.hwnd, TBPF.PAUSED)

        elif state == STATE_PLAYING:
            self.statusbar.set_text('Playing', IDX_STATUSBAR_PART_STATE)
            tbi.iImage = 7
            tbi.pszText  = 'Pause'

            if self.media_duration >= MIN_PROGRESS_DURATION:
                taskbar.SetProgressState(self.hwnd, TBPF.NORMAL)
                if self._state == STATE_STOPPED:
                    taskbar.SetProgressValue(self.hwnd, 1, 10000)  # For immediate update of taskbar color
            else:
                taskbar.SetProgressState(self.hwnd, TBPF.INDETERMINATE)

        self.toolbar.send_message(TB_SETBUTTONINFOW, IDM_PLAY_PAUSE, byref(tbi))
        self._state = state

    ########################################
    #
    ########################################
    def update_ui_has_playlist(self, has_playlist):
        state = MF_BYCOMMAND | (MF_ENABLED if has_playlist else MF_GRAYED)
        for idm in (IDM_PLAY_PREVIOUS, IDM_PLAY_NEXT):
            self.toolbar.send_message(TB_ENABLEBUTTON, idm, 1 if has_playlist else 0)
            user32.EnableMenuItem(self.h_menu, idm, state)

    ########################################
    #
    ########################################
    def _timer_proc(self):
        self.update_time()
        # Detect end reached
        if not self.mediaplayer.is_playing() and not self.is_loop:
            if self.playlist.play_next():
                return
            self.timer_stop()
            self.update_ui_player_state(STATE_STOPPED)

    ########################################
    # Updates slider position and time display in statusbar
    ########################################
    def update_time(self, force=False):
        secs = self.mediaplayer.get_time()
#        print(secs)
        if self.media_duration > 0:

#            self.slider_seek.send_message(TBM_SETPOS, 1, int(SEEK_RANGE * secs / self.media_duration))
            self.slider_seek.set_pos(secs / self.media_duration)

        self.update_counter += 1
        if force or self.update_counter % TIME_DISPLAY_UPDATE_STATUS_EVERY == 0:
            self.update_time_display(secs)

    ########################################
    #
    ########################################
    def update_time_format(self):
        if self.media_duration >= 3600:
            self.time_format = '{:02d}:{:02d}:{:02d}.{:03d}' if self.show_millisecs else '{:02d}:{:02d}:{:02d}'
        else:
            self.time_format = '{:02d}:{:02d}.{:03d}' if self.show_millisecs else '{:02d}:{:02d}'
        if self.media_duration > 0:
            h, m, s, ms = time_to_hms(self.media_duration)
            if self.media_duration >= 3600:
                self.time_format += (f' / {h:02d}:{m:02d}:{s:02d}.{ms:03d}' if self.show_millisecs else f' / {h:02d}:{m:02d}:{s:02d}')
            else:
                self.time_format += (f' / {m:02d}:{s:02d}.{ms:03d}' if self.show_millisecs else f' / {m:02d}:{s:02d}')

    ########################################
    #
    ########################################
    def update_time_display(self, secs):
        h, m, s, ms = time_to_hms(secs)
        self.statusbar.set_text(
            self.time_format.format(h, m, s, ms) if self.media_duration >= 3600 else self.time_format.format(m, s, ms),
            IDX_STATUSBAR_PART_TIME
        )

        if self.media_duration >= MIN_PROGRESS_DURATION and secs >= 1:
            taskbar.SetProgressValue(self.hwnd, int(secs), int(self.media_duration))

    ########################################
    #
    ########################################
    def quit(self):
        self.last_playlist = str(self.playlist.as_list()) if self.remember_playlist else '[]'
        save_settings(self)
        self.media_file = None
        self.mediaplayer.close_file()
        super().quit()


if __name__ == '__main__':
    sys.excepthook = traceback.print_exception
    app = App()
    sys.exit(app.run())
