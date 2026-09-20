from ctypes import *
from ctypes.wintypes import *

from .const import *
from .dlls import *
from .themes import *
from .types import *

MSGBOX_BOTTOM_HEIGHT = 42

########################################
# Open/Save Filename
########################################

class OPENFILENAMEW(Structure):
    def __init__(self, *args, **kwargs):
        super(OPENFILENAMEW, self).__init__(*args, **kwargs)
        self.lStructSize = sizeof(OPENFILENAMEW)
    _fields_ = (
        ('lStructSize', DWORD),
        ('hwndOwner', HWND),
        ('hInstance', HINSTANCE),
        ('lpstrFilter', LPWSTR),
        ('lpstrCustomFilter', LPWSTR),
        ('nMaxCustFilter', DWORD),
        ('nFilterIndex', DWORD),
        ('lpstrFile', LPWSTR),
        ('nMaxFile', DWORD),
        ('lpstrFileTitle', LPWSTR),
        ('nMaxFileTitle', DWORD),
        ('lpstrInitialDir', LPCWSTR),
        ('lpstrTitle', LPCWSTR),
        ('Flags', DWORD),
        ('nFileOffset', WORD),
        ('nFileExtension', WORD),
        ('lpstrDefExt', LPCWSTR),
        ('lCustData', LPARAM),
        ('lpfnHook', DLGHOOKPROC),
        ('lpTemplateName', LPCWSTR),
        ('pvReserved', LPVOID),
        ('dwReserved', DWORD),
        ('FlagsEx', DWORD),
    )

########################################
#
########################################
def show_open_file_dialog(
    parent_window,
    title = 'Open...',
    default_extension = '',
    filter_string = 'All Files (*.*)\0*.*\0\0',
    initial_path = ''
):
    file_buffer = create_unicode_buffer(initial_path, MAX_PATH)
    ofn = OPENFILENAMEW()
    ofn.hwndOwner = parent_window.hwnd
    ofn.lpstrTitle = title
    ofn.lpstrFile = cast(file_buffer, LPWSTR)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrDefExt = default_extension
    ofn.lpstrFilter = cast(create_unicode_buffer(filter_string), c_wchar_p)
    ofn.Flags = OFN_ENABLESIZING | OFN_PATHMUSTEXIST
    ok = comdlg32.GetOpenFileNameW(byref(ofn))
    return file_buffer[:].split('\0', 1)[0] if ok else None

########################################
#
########################################
def show_save_file_dialog(
    parent_window,
    title = 'Save...',
    default_extension = '',
    filter_string = 'All Files (*.*)\0*.*\0\0',
    initial_path = '',
    flags = OFN_ENABLESIZING | OFN_OVERWRITEPROMPT,

    hinstance = None,
    lpTemplateName = None,
    lpfnHook = None,
    nFilterIndex = 0,
):
    file_buffer = create_unicode_buffer(initial_path, MAX_PATH)
    ofn = OPENFILENAMEW()
    ofn.hwndOwner = parent_window.hwnd
    ofn.lpstrTitle = title
    ofn.lpstrFile = cast(file_buffer, LPWSTR)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrDefExt = default_extension
    ofn.lpstrFilter = cast(create_unicode_buffer(filter_string), c_wchar_p)
    ofn.Flags = flags
    ofn.hInstance = hinstance
    ofn.nFilterIndex = nFilterIndex
    if lpTemplateName:
        ofn.lpTemplateName = lpTemplateName
    if lpfnHook:
        ofn.lpfnHook = lpfnHook
    ok = comdlg32.GetSaveFileNameW(byref(ofn))
    return file_buffer[:].split('\0', 1)[0] if ok else None

########################################
#
########################################
def light_OnEraseBkgnd(hwnd, hdc):
    rc = RECT()
    user32.GetClientRect(hwnd, byref(rc))
    user32.FillRect(hdc, byref(rc), COLOR_WINDOW + 1)
    return TRUE

########################################
#
########################################
def dark_OnEraseBkgnd(hwnd, hdc):
    rc = RECT()
    user32.GetClientRect(hwnd, byref(rc))
    user32.FillRect(hdc, byref(rc), DARKER_BG_BRUSH)
    return TRUE

########################################
#
########################################
def light_OnPaint(hwnd):
    ps = PAINTSTRUCT()
    hdc = user32.BeginPaint(hwnd, byref(ps))
    ps.rcPaint.top = ps.rcPaint.bottom - MSGBOX_BOTTOM_HEIGHT
    user32.FillRect(hdc, byref(ps.rcPaint), COLOR_3DFACE + 1)
    user32.EndPaint(hwnd, byref(ps))
    return 0

########################################
# Lower part with buttons
########################################
def dark_OnPaint(hwnd):
    ps = PAINTSTRUCT()
    hdc = user32.BeginPaint(hwnd, byref(ps))
    ps.rcPaint.top = ps.rcPaint.bottom - MSGBOX_BOTTOM_HEIGHT
    user32.FillRect(hdc, byref(ps.rcPaint), DARK_BG_BRUSH)
    user32.EndPaint(hwnd, byref(ps))
    return 0

########################################
#
########################################
def dark_OnCtlColorDlg(hdc):
    gdi32.SetBkColor(hdc, DARK_BG_COLOR)
    return DARK_BG_BRUSH

########################################
#
########################################
def dark_OnCtlColorStatic(hdc):
    gdi32.SetTextColor(hdc, DARK_TEXT_COLOR)
    gdi32.SetBkColor(hdc, DARK_BG_COLOR)
    return DARK_BG_BRUSH

########################################
#
########################################
def light_OnCtlColorStaticMsgBox(hdc):
    gdi32.SetBkColor(hdc, 0xffffff)
    return COLOR_WINDOW + 1

########################################
#
########################################
def dark_OnCtlColorStaticMsgBox(hdc):
    gdi32.SetTextColor(hdc, DARK_TEXT_COLOR)
    gdi32.SetBkColor(hdc, DARKER_BG_COLOR)
    return DARKER_BG_BRUSH

########################################
#
########################################
def dark_OnCtlColorBtn(hdc):
    gdi32.SetDCBrushColor(hdc, DARK_BG_COLOR)
    return gdi32.GetStockObject(DC_BRUSH)

########################################
#
########################################
def dark_OnCtlColorEdit(hdc):
    gdi32.SetTextColor(hdc, DARK_TEXT_COLOR)
    gdi32.SetBkColor(hdc, DARK_BG_COLOR)
    gdi32.SetDCBrushColor(hdc, DARK_BG_COLOR)
#    gdi32.SetBkColor(hdc, DARK_CONTROL_BG_COLOR)
#    gdi32.SetDCBrushColor(hdc, DARK_CONTROL_BG_COLOR)
    return gdi32.GetStockObject(DC_BRUSH)

########################################
#
########################################
def _dark_messagebox_subclass_proc(hwnd, msg, wparam, lparam, uidsubclass, dwrefdata):

    if msg == WM_ERASEBKGND:
        return dark_OnEraseBkgnd(hwnd, wparam)

    elif msg == WM_PAINT:
        return dark_OnPaint(hwnd)

    elif msg == WM_CTLCOLORDLG:
        return dark_OnCtlColorDlg(wparam)

    elif msg == WM_CTLCOLORSTATIC:
        return dark_OnCtlColorStaticMsgBox(wparam)

    elif msg == WM_CTLCOLORBTN:
        return dark_OnCtlColorBtn(wparam)

    return comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)

dark_messagebox_subclass_proc = SUBCLASSPROC(_dark_messagebox_subclass_proc)

# For HOOKPROC
class CWPRETSTRUCT(Structure):
    _fields_ = [
        ("lResult", LPARAM),
        ("lParam", LPARAM),
        ("wParam", WPARAM),
        ("message", UINT),
        ("hwnd", HWND),
    ]

########################################
#
########################################
def show_message_box(parent_window, text, caption = '', utype = MB_ICONINFORMATION | MB_OK):
    if parent_window.is_dark:
        classname_buf = create_unicode_buffer(10)

        global hook_proc
        global h_hook

        ########################################
        #
        ########################################
        def _hook_proc(ncode, wparam, lparam):
            if ncode < 0:
                return user32.CallNextHookEx(h_hook, ncode, wparam, lparam)
            msg = cast(lparam, POINTER(CWPRETSTRUCT)).contents
            user32.GetClassNameW(msg.hwnd, classname_buf, 10)
            if classname_buf.value == '#32770':
                if msg.message == WM_INITDIALOG:
                    dwm_use_dark_mode(msg.hwnd, True)
                    comctl32.SetWindowSubclass(msg.hwnd, dark_messagebox_subclass_proc, 0, 0)
                    hwnd = user32.FindWindowExW(msg.hwnd, None, WC_BUTTON, None)
                    while hwnd:
                        uxtheme.SetWindowTheme(hwnd, 'DarkMode_Explorer', None)
                        hwnd = user32.FindWindowExW(msg.hwnd, hwnd, WC_BUTTON, None)
            return user32.CallNextHookEx(h_hook, ncode, wparam, lparam)

        hook_proc = HOOKPROC(_hook_proc)
        h_hook = user32.SetWindowsHookExW(WH_CALLWNDPROCRET, hook_proc, 0, kernel32.GetCurrentThreadId())
        res = user32.MessageBoxW(parent_window.hwnd, text, caption, utype)
        user32.UnhookWindowsHookEx(h_hook)
        return res
    else:
        return user32.MessageBoxW(parent_window.hwnd, text, caption, utype)
