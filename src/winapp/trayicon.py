import uuid

from ctypes import Union, Structure, c_ubyte, sizeof, byref
from ctypes.wintypes import UINT, DWORD, HWND, WCHAR, HICON

from .const import *
from .dlls import shell32

ID_TRAYICON = 300

class _TimeoutVersionUnion(Union):
    _fields_ = [('uTimeout', UINT),
                ('uVersion', UINT),]

class NOTIFYICONDATAW(Structure):
    def __init__(self, *args, **kwargs):
        super(NOTIFYICONDATAW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize', DWORD),
        ('hWnd', HWND),
        ('uID', UINT),
        ('uFlags', UINT),
        ('uCallbackMessage', UINT),
        ('hIcon', HICON),
        ('szTip', WCHAR * 128),
        ('dwState', DWORD),
        ('dwStateMask', DWORD),
        ('szInfo', WCHAR * 256),
        ('union', _TimeoutVersionUnion),
        ('szInfoTitle', WCHAR * 64),
        ('dwInfoFlags', DWORD),
        ('guidItem', c_ubyte * 16),  # GUID - but we don't want to depend on winapp.comtypes
        ('hBalloonIcon', HICON),
    ]


class TrayIcon(object):

    def __init__(
        self,
        parent_window,
        h_icon,
        message_id,
        tooltip,
        show = True,
        message_timeout = 5000
    ):
        self.trayiconinfo = NOTIFYICONDATAW()
        self.trayiconinfo.hWnd = parent_window.hwnd
        self.trayiconinfo.uID = ID_TRAYICON
        self.trayiconinfo.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP | NIF_SHOWTIP | NIF_GUID
        self.trayiconinfo.uCallbackMessage = message_id
        self.trayiconinfo.hIcon = h_icon
        self.trayiconinfo.szTip = tooltip
        self.trayiconinfo.dwState = NIS_SHAREDICON
        self.trayiconinfo.union.uTimeout = message_timeout
        self.trayiconinfo.dwInfoFlags = NIIF_INFO
        self.trayiconinfo.guidItem = (c_ubyte * 16)(*bytearray(uuid.uuid4().bytes))
        self.trayiconinfo.hBalloonIcon = 0
        if show:
            self.show()

    def __del__(self):
        shell32.Shell_NotifyIconW(NIM_DELETE, byref(self.trayiconinfo))

    def show(self, flag=True):
        ok = shell32.Shell_NotifyIconW(NIM_ADD if flag else NIM_DELETE, byref(self.trayiconinfo))
        if flag:
            self.trayiconinfo.union.uVersion = 4
            ok = shell32.Shell_NotifyIconW(NIM_SETVERSION, byref(self.trayiconinfo))

    def notify(self, info, info_title='', flags=NIIF_INFO):
        nid = NOTIFYICONDATAW()
        nid.uFlags = NIF_INFO | NIF_GUID
        nid.guidItem = self.trayiconinfo.guidItem
        nid.dwInfoFlags = flags
        nid.szInfoTitle = info_title
        nid.szInfo = info
        return shell32.Shell_NotifyIconW(NIM_MODIFY, byref(nid))

    def restore_tooltip(self):
        nid = NOTIFYICONDATAW()
        nid.uFlags = NIF_SHOWTIP | NIF_GUID
        nid.guidItem = self.trayiconinfo.guidItem
        return shell32.Shell_NotifyIconW(NIM_MODIFY, byref(nid))

    def set_tooltip(self, tooltip):
        self.trayiconinfo.szTip = tooltip
        nid = NOTIFYICONDATAW()
        nid.szTip = tooltip
        nid.uFlags = NIF_TIP | NIF_SHOWTIP | NIF_GUID
        nid.guidItem = self.trayiconinfo.guidItem
        return shell32.Shell_NotifyIconW(NIM_MODIFY, byref(nid))

    def set_icon(self, hicon):
        nid = NOTIFYICONDATAW()
        nid.hIcon = hicon
        nid.uFlags = NIF_ICON | NIF_SHOWTIP | NIF_GUID
        nid.guidItem = self.trayiconinfo.guidItem
        return shell32.Shell_NotifyIconW(NIM_MODIFY, byref(nid))
