from ..window import *
from ..themes import *

SPLITTER_CLASS_NAME = 'SplitterClass'
SPLITTER_SIZE = 4

EVENT_SPLITTER_MOVING_STARTED = 2
EVENT_SPLITTER_MOVED = 0
EVENT_SPLITTER_MOVING = 1

SPLITTER_BG_BRUSH = COLOR_3DFACE + 1
SPLITTER_BG_BRUSH_DARK = DARK_BG_BRUSH

SPLITTER_BRUSH_MOVING = gdi32.CreateSolidBrush(0x808080)

_window_proc = WNDPROC(user32.DefWindowProcW)

_splitter_class = WNDCLASSEXW()
_splitter_class.lpfnWndProc = _window_proc
#        _splitter_class.style = CS_VREDRAW | CS_HREDRAW
_splitter_class.lpszClassName = SPLITTER_CLASS_NAME
_splitter_class.hbrBackground = COLOR_3DFACE + 1
user32.RegisterClassExW(byref(_splitter_class))


########################################
#
########################################
class Splitter(Window):

    def __init__(
        self,
        parent_window,
        style = WS_CHILD,
        initial_pos = 0,
        is_vertical = False,
        is_reversed = False,
    ):
        self.pos = initial_pos
        self.is_vertical = is_vertical
        self.is_reversed = is_reversed
        self.x = 0
        self.y = 0
        self.h_cursor = user32.LoadCursorW(0, IDC_SIZENS if is_vertical else IDC_SIZEWE)

        super().__init__(
            SPLITTER_CLASS_NAME,
            style = style,
            ex_style = WS_EX_TOOLWINDOW,
            parent_window = parent_window,
            left = 0 if is_vertical else initial_pos,
            top = initial_pos if is_vertical else 0,
            width = 0 if is_vertical else SPLITTER_SIZE,
            height = SPLITTER_SIZE if is_vertical else 0,
        )

        ########################################
        #
        ########################################
        def _on_WM_MOUSEMOVE(hwnd, wparam, lparam):

            if self.is_vertical:
                y = GET_Y_LPARAM(lparam) - self._click_y
                pt = POINT(0, y)
                user32.MapWindowPoints(self.parent_window.hwnd, None, byref(pt), 1)
                self.y = max(min(pt.y, self.rc_parent.bottom - SPLITTER_SIZE), self.rc_parent.top)

            else:
                x = GET_X_LPARAM(lparam) - self._click_x
                pt = POINT(x, 0)
                user32.MapWindowPoints(self.parent_window.hwnd, None, byref(pt), 1)
                self.x = max(min(pt.x, self.rc_parent.right - SPLITTER_SIZE), self.rc_parent.left)

            user32.SetWindowPos(self.hwnd, 0, self.x, self.y, 0, 0, SWP_NOZORDER | SWP_NOSIZE | SWP_NOACTIVATE)
            self.emit(EVENT_SPLITTER_MOVING)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):

            if self.is_reversed:
                self.rc_parent = self.parent_window.get_client_rect()
                user32.MapWindowPoints(self.parent_window.hwnd, None, byref(self.rc_parent), 2)

            if self.is_vertical:
                self._click_y = GET_Y_LPARAM(lparam)
                pt = POINT(0, self.y)
                user32.MapWindowPoints(self.parent_window.hwnd, None, byref(pt), 1)
                self.x = pt.x

            else:
                self._click_x = GET_X_LPARAM(lparam)
                pt = POINT(self.x, 0)
                user32.MapWindowPoints(self.parent_window.hwnd, None, byref(pt), 1)
                self.y = pt.y

            user32.SetParent(self.hwnd, None)
            user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, SPLITTER_BRUSH_MOVING)
            user32.SetWindowPos(self.hwnd, HWND_TOP, pt.x, pt.y, 0, 0, SWP_FRAMECHANGED | SWP_NOSIZE)

            self.parent_window.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)
            user32.SetCapture(parent_window.hwnd)

            self.emit(EVENT_SPLITTER_MOVING_STARTED)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONUP(hwnd, wparam, lparam):
            user32.ReleaseCapture()
            self.parent_window.unregister_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)

            pt = POINT(self.x, self.y)
            user32.MapWindowPoints(None, self.parent_window.hwnd, byref(pt), 1)

            if self.is_vertical:
                self.pos = self.rc_parent.bottom - self.rc_parent.top - pt.y if self.is_reversed else pt.y
            else:
                self.pos = self.rc_parent.right - self.rc_parent.left - pt.x if self.is_reversed else pt.x

            user32.SetParent(self.hwnd, parent_window.hwnd)
            user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, SPLITTER_BG_BRUSH_DARK if self.is_dark else SPLITTER_BG_BRUSH)
            user32.SetWindowPos(self.hwnd, 0, pt.x, pt.y, 0, 0, SWP_NOZORDER | SWP_NOSIZE | SWP_NOACTIVATE)

            self.emit(EVENT_SPLITTER_MOVED)

        self.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)
        self.parent_window.register_message_callback(WM_LBUTTONUP, _on_WM_LBUTTONUP)

        ########################################
        #
        ########################################
        def _on_WM_SETCURSOR(hwnd, wparam, lparam):
            user32.SetCursor(self.h_cursor)
            return TRUE

        self.register_message_callback(WM_SETCURSOR, _on_WM_SETCURSOR)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        self.is_dark = is_dark
        user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, SPLITTER_BG_BRUSH_DARK if self.is_dark else SPLITTER_BG_BRUSH)

    ########################################
    #
    ########################################
    def set_window_pos(self, x=0, y=0, width=0, height=0, hwnd_insert_after=0, flags=0):
        self.x, self.y = x, y
        user32.SetWindowPos(self.hwnd, hwnd_insert_after, x, y, width, height, flags)
