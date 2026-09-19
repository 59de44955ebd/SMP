from ctypes import *
from ctypes.wintypes import *

from winapp.const import *
from winapp.dlls import advapi32

from const import *

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
            'show_millisecs', 'show_menu', 'show_seek', 'show_controls', 'show_status', 'show_playlist', 'stayontop',
            'minimize_to_tray', 'auto_resize_to_video', 'single_instance', 'remember_playlist', 'use_meta_title',
            'fullscreen_dblclk'
        ):
            if advapi32.RegQueryValueExW(hkey, prop, None, None, byref(data), byref(cbData)) == ERROR_SUCCESS:
                settings[prop] = cast(data, POINTER(DWORD)).contents.value == 1
        # int
        for prop in ('theme', 'volume', 'splitter_pos'):  # 'engine',
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

        cbdata_str = DWORD()
        if advapi32.RegQueryValueExW(hkey, 'engine', None, None, None, byref(cbdata_str)) == ERROR_SUCCESS:
            data_str = (BYTE * cbdata_str.value)()
            if advapi32.RegQueryValueExW(hkey, 'engine', None, None, data_str, byref(cbdata_str)) == ERROR_SUCCESS:
                settings['engine'] = list(ENGINES.keys())[list(ENGINES.values()).index(cast(data_str, LPWSTR).value)]

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
            'show_millisecs', 'show_menu', 'show_seek', 'show_controls', 'show_status', 'show_playlist',
            'theme', 'volume', 'stayontop', 'minimize_to_tray', 'auto_resize_to_video', 'single_instance',
            'remember_playlist', 'use_meta_title', 'fullscreen_dblclk'
        ):
            advapi32.RegSetValueExW(hkey, prop, 0, REG_DWORD, byref(DWORD(int(getattr(main, prop)))), dwsize)

        advapi32.RegSetValueExW(hkey, 'splitter_pos', 0, REG_DWORD, byref(DWORD(main.pane.splitter.pos)), dwsize)

        if main.mediaplayer.is_fullscreen():
            main.mediaplayer.set_fullscreen(False)

        main.show(SW_SHOWNORMAL)

        rc = main.get_window_rect()
        buf = create_unicode_buffer(f'({rc.left},{rc.top},{rc.right-rc.left},{rc.bottom-rc.top})')
        advapi32.RegSetValueExW(hkey, 'rect', 0, REG_SZ, buf, sizeof(buf))

        buf = create_unicode_buffer(main.last_playlist)
        advapi32.RegSetValueExW(hkey, 'last_playlist', 0, REG_SZ, buf, sizeof(buf))

        buf = create_unicode_buffer(str(main.color_values))
        advapi32.RegSetValueExW(hkey, 'color_values', 0, REG_SZ, buf, sizeof(buf))

        buf = create_unicode_buffer(ENGINES[main.engine])
        advapi32.RegSetValueExW(hkey, 'engine', 0, REG_SZ, buf, sizeof(buf))

        advapi32.RegCloseKey(hkey)
