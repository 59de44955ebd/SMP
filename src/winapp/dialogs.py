from ctypes import *
from ctypes.wintypes import *

from .const import *
from .dlls import *
from .types import *

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
#def show_message_box(parent_window, text, caption = '', utype = MB_ICONINFORMATION | MB_OK):
#    return user32.MessageBoxW(parent_window.hwnd, text, caption, utype)

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
