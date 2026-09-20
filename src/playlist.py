import configparser
import os
from random import shuffle

from winapp.controls_themed.listbox import *
from winapp.dialogs import *
from winapp.themes import *

from resources import *

EVENT_PLAYLIST_HAS_ITEMS_CHANGED = 1
EVENT_PLAYLIST_ACTIVE_ITEM_REMOVED = 2
EVENT_PLAYLIST_PLAY_ITEM_REQUESTED = 3


class MediaItem():

    ########################################
    #
    ########################################
    def __init__(self, filename, title=None, length=None):
        self.filename = filename
        self.title = title
        self.length = length
        self.invalid = False


########################################
# https://en.wikipedia.org/wiki/M3U
########################################
def load_m3u(m3u_file):
    playlist = []
    with open(m3u_file, 'r', encoding = 'utf-8-sig') as f:
        length, title = None, None
        for i, line in enumerate(f):
            if i == 0 and line.startswith('#EXTM3U'):
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith('#EXTINF:'):
                length, title = line.split('#EXTINF:')[1].split(',', 1)
            elif (len(line) != 0):
                playlist.append(MediaItem(line, title, length))
                length, title = None, None
    return playlist

########################################
#
########################################
def save_m3u(m3u_file, playlist):
    with open(m3u_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for i, media_item in enumerate(playlist):
            if media_item.length is not None or media_item.title:
                f.write(f'#EXTINF:')
                if media_item.length is not None:
                    f.write(f'{round(media_item.length)}')  # ceil?
                if media_item.title:
                    f.write(f',{media_item.title}')
                f.write('\n')
            f.write(f'{media_item.filename}\n')

########################################
# https://en.wikipedia.org/wiki/PLS_(file_format)
########################################
def load_pls(pls_file):
    parser = configparser.RawConfigParser()
    parser.read_file(open(pls_file, 'r', encoding = 'utf-8-sig'))
    num_entries = parser.getint("playlist", "NumberOfEntries")
    playlist = []
    for i in range(1, num_entries + 1):
        playlist.append(MediaItem(
            parser.get("playlist", "File%d" % i),
            parser.get("playlist", "Title%d" % i, fallback=None),
            parser.get("playlist", "Length%d" % i, fallback=None)
        ))
    return playlist

########################################
#
########################################
def save_pls(pls_file, playlist):
    with open(pls_file, 'w', encoding='utf-8') as f:
        f.write('[playlist]\n')
#        f.write('\n')
        for i, media_item in enumerate(playlist):
            f.write(f'File{i + 1}={media_item.filename}\n')
            if media_item.title:
                f.write(f'Title{i + 1}={media_item.title}\n')
            if media_item.length:
                f.write(f'Length{i + 1}={round(media_item.length)}\n')  # ceil?
#            f.write('\n')
        f.write(f'NumberOfEntries={len(playlist)}\n')
        f.write('Version=2\n')


########################################
#
########################################
class PlayList(ListBox):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, hmod_resources):

        self.playlist_items = []
        self.active_idx = -1
        self.hmod_resources = hmod_resources

        super().__init__(
            parent_window,
            style = (
                WS_CHILD | WS_VISIBLE | WS_TABSTOP | WS_VSCROLL
                | LBS_NOTIFY | LBS_NOINTEGRALHEIGHT
                | LBS_OWNERDRAWFIXED
                | LBS_HASSTRINGS
                | LBS_WANTKEYBOARDINPUT
            ),
            ex_style = WS_EX_ACCEPTFILES,
        )

        comctl32.MakeDragList(self.hwnd)
        WM_DRAGMSG = user32.RegisterWindowMessageW('commctrl_DragListMsg')

        self.set_font('Segoe UI', -12)
        self.hide_focus_rects()
        self.send_message(LB_SETITEMHEIGHT, 0, 15)

        ########################################
        #
        ########################################
        def _on_WM_CONTEXTMENU(hwnd, wparam, lparam):
            x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF

            h_menu = user32.LoadMenuW(hmod_resources, LPCWSTR(ID_POPUP_MENU_PLAYLIST))

            has_playlist = bool(self.playlist_items)
            if has_playlist:
                pt = POINT(x, y)
                user32.MapWindowPoints(None, self.hwnd, byref(pt), 1)
                idx = self.send_message(LB_ITEMFROMPOINT, 0, MAKELPARAM(pt.x, pt.y))
                if HIWORD(idx) == 0:
                    self.send_message(LB_SETCURSEL, idx, 0)
                else:
                    user32.EnableMenuItem(h_menu, IDM_PLAYLIST_EDIT_TITLE, MF_BYCOMMAND | MF_GRAYED)
                    user32.EnableMenuItem(h_menu, IDM_PLAYLIST_REMOVE, MF_BYCOMMAND | MF_GRAYED)
            else:
                for idm in (IDM_PLAYLIST_EXPORT, IDM_PLAYLIST_SHUFFLE, IDM_PLAYLIST_CLEAR, IDM_PLAYLIST_EDIT_TITLE, IDM_PLAYLIST_REMOVE):
                    user32.EnableMenuItem(h_menu, idm, MF_BYCOMMAND | MF_GRAYED)

            idm = user32.TrackPopupMenuEx(user32.GetSubMenu(h_menu, 0), TPM_LEFTBUTTON | TPM_RETURNCMD, x, y, self.hwnd, 0)
            self.send_message(LB_SETCURSEL, -1, 0)

            if idm == IDM_PLAYLIST_IMPORT:
                playlist_file = show_open_file_dialog(self, 'Import Playlist', '.m3u', 'Playlist Files (*.m3u *.pls)\0*.m3u;*.pls\0\0')
                if playlist_file:
                    if playlist_file.lower().endswith('.pls'):
                        playlist = load_pls(playlist_file)
                    else:
                        playlist = load_m3u(playlist_file)
                    self.clear()
                    for media_item in playlist:
                        self.add_item(media_item)
                    self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, bool(self.playlist_items))

            elif idm == IDM_PLAYLIST_EXPORT:
                playlist_file = show_save_file_dialog(self, 'Export Playlist', '.m3u', 'M3U Files (*.m3u)\0*.m3u\0PLS Files (*.pls)\0*.pls\0\0', 'playlist')
                if playlist_file:
                    playlist = list(self.playlist_items.values())  # TODO: order!
                    if playlist_file.lower().endswith('.pls'):
                        playlist = save_pls(playlist_file, playlist)
                    else:
                        playlist = save_m3u(playlist_file, playlist)

            elif idm == IDM_PLAYLIST_SHUFFLE:
                self.send_message(WM_SETREDRAW, FALSE, 0)

                if self.active_idx >= 0:
                    active_item = self.playlist_items[self.active_idx]

                shuffle(self.playlist_items)

                if self.active_idx >= 0:
                    self.active_idx = self.playlist_items.index(active_item)

                self.send_message(LB_RESETCONTENT, 0, 0)
                for media_item in self.playlist_items:
                    self.add_string(media_item.title or os.path.basename(media_item.filename))

                self.send_message( WM_SETREDRAW, TRUE, 0)

            elif idm == IDM_PLAYLIST_EDIT_TITLE:
                self.edit_title(idx)

            elif idm == IDM_PLAYLIST_REMOVE:
                self.delete_item(idx)
                if not self.playlist_items:
                    self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, False)

            elif idm == IDM_PLAYLIST_CLEAR:
                self.clear()

        self.register_message_callback(WM_CONTEXTMENU, _on_WM_CONTEXTMENU)

        ########################################
        #
        ########################################
        def _on_WM_DROPFILES(hwnd, wparam, lparam):
            self.handle_dropped_items(self.get_dropped_items(wparam))
            return FALSE

        self.register_message_callback(WM_DROPFILES, _on_WM_DROPFILES)

        ########################################
        #
        ########################################
        def _on_WM_DRAWITEM(hwnd, wparam, lparam):
            di = cast(lparam, POINTER(DRAWITEMSTRUCT)).contents
            if di.CtlType == ODT_LISTBOX:
                if di.itemID == 0xffffffff:
                    return TRUE
                media_item = self.playlist_items[di.itemID]
                if media_item.invalid:
                    gdi32.SetTextColor(di.hDC, 0x3333FF)
                elif di.itemID == self.active_idx:
                    gdi32.SetTextColor(di.hDC, 0xF89A26)
                else:
                    gdi32.SetTextColor(di.hDC, DARK_TEXT_COLOR if self.is_dark else 0x000000)

                if self.is_dark:
                    gdi32.SetBkColor(di.hDC, 0x3e3e3e if di.itemState & ODS_SELECTED else DARK_BG_COLOR)
                else:
                    gdi32.SetBkColor(di.hDC,  0xF1DACC if di.itemState & ODS_SELECTED else 0xffffff)

                # Get and display the text for the list item.
                buf = create_unicode_buffer(MAX_PATH)
                res = self.send_message(LB_GETTEXT, di.itemID, byref(buf))
                gdi32.ExtTextOutW(
                    di.hDC, 3, di.rcItem.top, 6, byref(di.rcItem),  # 6 = ETO_CLIPPED | ETO_OPAQUE
                    buf.value, len(buf.value), None
                )
                # If an application processes this message, it should return TRUE.
                return TRUE

        parent_window.register_message_callback(WM_DRAWITEM, _on_WM_DRAWITEM)

        class ctx:
            idx_drag = None

        ########################################
        #
        ########################################
        def _on_WM_DRAGMSG(hwnd, wparam, lparam):
            dli = cast(lparam, POINTER(DRAGLISTINFO)).contents

            if dli.uNotification == DL_BEGINDRAG:
                idx = comctl32.LBItemFromPt(self.hwnd, dli.ptCursor, TRUE)
                ctx.idx_drag = idx if idx >= 0 else None
                # Return TRUE to begin the drag operation, or FALSE to prevent the drag operation.
                return int(idx >= 0)

            elif dli.uNotification == DL_DROPPED:
                if ctx.idx_drag is None:
                    return

                comctl32.DrawInsert(parent_window.hwnd, self.hwnd, -1)

                idx_new = comctl32.LBItemFromPt(self.hwnd, dli.ptCursor, TRUE)

                if idx_new < 0:
                    user32.MapWindowPoints(None, self.hwnd, byref(dli.ptCursor), 1)
                    idx_new = self.send_message(LB_GETCOUNT, 0, 0) if dli.ptCursor.y > 0 else 0

                self.move_item(ctx.idx_drag, idx_new)  # old, new
                ctx.idx_drag = None

            elif dli.uNotification == DL_DRAGGING:
                idx = comctl32.LBItemFromPt(self.hwnd, dli.ptCursor, TRUE)
                comctl32.DrawInsert(parent_window.hwnd, self.hwnd, idx)

        parent_window.pane.register_message_callback(WM_DRAGMSG, _on_WM_DRAGMSG)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDBLCLK(hwnd, wparam, lparam):
            idx = self.send_message(LB_ITEMFROMPOINT, 0, lparam)
            if HIWORD(idx) == 0:
                self.play_index(idx)

        self.register_message_callback(WM_LBUTTONDBLCLK, _on_WM_LBUTTONDBLCLK)

    ########################################
    #
    ########################################
    def handle_dropped_items(self, dropped_items):
        def _add_item(f):
            if os.path.isfile(f):
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.m3u', '.pls'):
                    self.load_playlist(f, append = True)
                else:
                    self.add_item(MediaItem(f))

            elif os.path.isdir(f):
                for c in os.listdir(f):
                    _add_item(os.path.join(f, c))

        self.send_message(WM_SETREDRAW, FALSE, 0)
        for f in dropped_items:
            _add_item(f)
        self.send_message(WM_SETREDRAW, TRUE, 0)
        self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, True)

    ########################################
    #
    ########################################
    def load_playlist(self, playlist_file, append = False):
        if playlist_file.lower().endswith('.pls'):
            playlist = load_pls(playlist_file)
        else:
            playlist = load_m3u(playlist_file)
        if not append:
            self.clear()
        self.send_message(WM_SETREDRAW, FALSE, 0)
        for media_item in playlist:
            self.add_item(media_item)
        self.send_message(WM_SETREDRAW, TRUE, 0)
        self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, bool(self.playlist_items))

    ########################################
    #
    ########################################
    def clear(self):
        if not self.playlist_items:
            return
        self.playlist_items = []
        self.send_message(LB_RESETCONTENT, 0, 0)

        if self.active_idx >= 0:
            self.emit(EVENT_PLAYLIST_ACTIVE_ITEM_REMOVED)
            self.active_idx = -1

        self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, False)

    ########################################
    #
    ########################################
    def add_files(self, media_files, clear=False):
        self.send_message(WM_SETREDRAW, FALSE, 0)
        if clear:
            self.playlist_items = []
            self.send_message(LB_RESETCONTENT, 0, 0)

        for media_file in media_files:
            media_item = MediaItem(media_file)
            self.playlist_items.append(media_item)
            self.add_string(media_item.title or os.path.basename(media_item.filename))
        self.active_idx = 0
        self.send_message(WM_SETREDRAW, TRUE, 0)
        self.emit(EVENT_PLAYLIST_HAS_ITEMS_CHANGED, True)

    ########################################
    #
    ########################################
    def add_item(self, media_item):
        self.playlist_items.append(media_item)
        self.add_string(media_item.title or os.path.basename(media_item.filename))

    ########################################
    #
    ########################################
    def delete_item(self, idx):

        self.send_message(LB_DELETESTRING, idx, 0)
        del self.playlist_items[idx]

        if self.active_idx >= 0:
            if self.active_idx == idx:
                self.emit(EVENT_PLAYLIST_ACTIVE_ITEM_REMOVED)
                self.active_idx = -1
                self.redraw()
            elif self.active_idx > idx:
                self.active_idx -= 1
                self.redraw()

    ########################################
    #
    ########################################
    def move_item(self, idx_old, idx_new):
        self.send_message(WM_SETREDRAW, FALSE, 0)

        media_item = self.playlist_items[idx_old]

        del self.playlist_items[idx_old]
        self.send_message(LB_DELETESTRING, idx_old, 0)

        if idx_new > idx_old:
            idx_new -= 1  # ???

        self.playlist_items.insert(idx_new, media_item)
        self.send_message(LB_INSERTSTRING, idx_new, media_item.title or os.path.basename(media_item.filename))

        self.send_message(WM_SETREDRAW, TRUE, 0)

    ########################################
    #
    ########################################
    def play_index(self, playlist_idx):
        for idx in range(playlist_idx, len(self.playlist_items)):
            if not self.playlist_items[idx].invalid:
                self.active_idx = idx
                self.redraw()
                media_item = self.playlist_items[idx]
                self.emit(EVENT_PLAYLIST_PLAY_ITEM_REQUESTED, media_item)
                return True

        self.active_idx = -1
        self.redraw()

        return False

    ########################################
    #
    ########################################
    def play_next(self, loop = False):
        if self.active_idx < len(self.playlist_items) - 1:

            for idx in range(self.active_idx + 1, len(self.playlist_items)):
                if not self.playlist_items[idx].invalid:
                    self.active_idx = idx
                    self.redraw()
                    media_item = self.playlist_items[idx]
                    self.emit(EVENT_PLAYLIST_PLAY_ITEM_REQUESTED, media_item)
                    return True

        elif loop:
            return self.play_index(0)

        return False

    ########################################
    #
    ########################################
    def play_previous(self, loop = False):
        if self.active_idx > 0:

            for idx in range(self.active_idx - 1, -1, -1):
                if not self.playlist_items[idx].invalid:
                    self.active_idx = idx
                    self.redraw()
                    media_item = self.playlist_items[idx]
                    self.emit(EVENT_PLAYLIST_PLAY_ITEM_REQUESTED, media_item)
                    return True

        elif loop:
            return self.play_index(len(self.playlist_items) - 1)

        return False

    ########################################
    #
    ########################################
    def set_invalid(self, media_item):
        media_item.invalid = True
        self.redraw()

    ########################################
    #
    ########################################
    def redraw(self):
        user32.InvalidateRect(self.hwnd, None, TRUE)

    ########################################
    #
    ########################################
    def edit_title(self, idx):
        media_item = self.playlist_items[idx]

        ########################################
        #
        ########################################
        def _dialog_proc_edit_title(hwnd, msg, wparam, lparam):
            if msg == WM_INITDIALOG:
                hwnd_edit = user32.GetDlgItem(hwnd, IDC_EDIT_FILENAME)
                if self.is_dark:
                    dwm_use_dark_mode(hwnd, True)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDOK), 'DarkMode_Explorer', None)
                    uxtheme.SetWindowTheme(user32.GetDlgItem(hwnd, IDCANCEL), 'DarkMode_Explorer', None)
                    user32.SetWindowLongA(hwnd_edit, GWL_EXSTYLE, user32.GetWindowLongA(hwnd_edit, GWL_EXSTYLE) & ~WS_EX_STATICEDGE & ~WS_EX_CLIENTEDGE)
                    user32.SetWindowLongA(hwnd_edit, GWL_STYLE, user32.GetWindowLongA(hwnd_edit, GWL_STYLE) | WS_BORDER)
                    user32.SetWindowPos(hwnd_edit, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
                user32.SetWindowTextW(hwnd_edit, media_item.title or os.path.basename(media_item.filename))
                user32.SendMessageW(hwnd_edit, EM_SETSEL, 0, -1)
                center_window(hwnd, self.parent_window.hwnd)
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
                            media_item.title = text_buf.value
                            self.send_message(WM_SETREDRAW, FALSE, 0)
                            self.send_message(LB_DELETESTRING, idx, 0)
                            self.send_message(LB_INSERTSTRING, idx, text_buf.value)
                            self.send_message(WM_SETREDRAW, TRUE, 0)
                    user32.EndDialog(hwnd, 0)

            elif self.is_dark:
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
                elif msg == WM_CTLCOLOREDIT:
                    return dark_OnCtlColorEdit(wparam)

            else:
                if msg == WM_ERASEBKGND:
                    return light_OnEraseBkgnd(hwnd, wparam)
                elif msg == WM_PAINT:
                    return light_OnPaint(hwnd)
                elif msg == WM_CTLCOLORSTATIC:
                    return light_OnCtlColorStaticMsgBox(wparam)

            return FALSE

        dialog_proc = WNDPROC(_dialog_proc_edit_title)

        user32.DialogBoxParamW(
            self.hmod_resources,
            MAKEINTRESOURCEW(IDD_PLAYLIST_EDIT_TITLE),
            self.hwnd,
            dialog_proc,
            NULL
        )

    ########################################
    #
    ########################################
    def as_list(self):
        playlist = []
        for media_item in self.playlist_items:
            playlist.append((media_item.filename, media_item.title, media_item.length))
        return playlist

    ########################################
    #
    ########################################
    def from_list(self, playlist):
        self.send_message(WM_SETREDRAW, FALSE, 0)
        for row in playlist:
            self.add_item(MediaItem(*row))
        self.send_message(WM_SETREDRAW, TRUE, 0)
