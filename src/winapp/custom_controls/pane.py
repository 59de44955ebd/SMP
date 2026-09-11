from ..controls_themed.toolbar import *
from .splitter import *

PANE_CLASS = "PaneClass"

EVENT_PANE_CLOSE_REQUESTED = 1

IDM_PANE_CLOSE = 1
CAPTION_HEIGHT = 23

_window_proc = WNDPROC(user32.DefWindowProcW)

newclass = WNDCLASSEXW()
newclass.lpfnWndProc = _window_proc
newclass.style = CS_VREDRAW | CS_HREDRAW
newclass.lpszClassName = PANE_CLASS
newclass.hbrBackground = COLOR_3DFACE + 1
user32.RegisterClassExW(byref(newclass))


class Pane(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        h_bitmap = None,
        h_bitmap_dark = None,
        window_title = None,
        child_window = None,
        is_right = False,
        initial_pos = 300,
    ):

        self.window_title = window_title

        super().__init__(
            PANE_CLASS,
            style = style,
            ex_style = ex_style,
            window_title = window_title,
            parent_window = parent_window
        )

        if h_bitmap:
            toolbar_buttons = (
                ('Close', IDM_PANE_CLOSE, BTNS_AUTOSIZE),
            )
            self.toolbar = ToolBar(
                self,
                width = 23, height = 19,
                style = WS_CHILD | WS_VISIBLE | CCS_NODIVIDER | TBSTYLE_FLAT | TBSTYLE_TRANSPARENT | TBSTYLE_LIST | CCS_NORESIZE,
                toolbar_buttons = toolbar_buttons,
                bitmap_size = (8, 7),
                h_bitmap = h_bitmap,
                h_bitmap_dark = h_bitmap_dark or h_bitmap,
                hide_text = True,
                padding = (6, 9)
            )

            ########################################
            #
            ########################################
            def _on_WM_COMMAND(hwnd, wparam, lparam):
                command_id = LOWORD(wparam)
                if command_id == IDM_PANE_CLOSE:
                    self.emit(EVENT_PANE_CLOSE_REQUESTED)
                return 0

            self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)
        else:
            self.toolbar = None

        if child_window:
             self.set_child(child_window)
        else:
            self.child = None

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            if self.child:
                self.child.set_window_pos(
                width = width, height = height - CAPTION_HEIGHT,
                flags = SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE
            )
            if self.toolbar:
                self.toolbar.set_window_pos(width - 21, 3, flags = SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)

        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

        ########################################
        #
        ########################################
        def _on_WM_PAINT(hwnd, wparam, lparam):
            ps = PAINTSTRUCT()
            hdc = user32.BeginPaint(hwnd, byref(ps))
            gdi32.SetBkMode(hdc, TRANSPARENT)
            gdi32.SetTextColor(hdc, DARK_TEXT_COLOR if self.is_dark else 0x000000)
            gdi32.SelectObject(hdc, self.h_font)
            user32.DrawTextW(hdc, self.window_title, -1, RECT(4, 0, 100, CAPTION_HEIGHT), DT_SINGLELINE | DT_LEFT | DT_VCENTER)

            ps.rcPaint.top = CAPTION_HEIGHT - 1
            ps.rcPaint.bottom = CAPTION_HEIGHT
            user32.FillRect(hdc, byref(ps.rcPaint), COLOR_WINDOWFRAME + 1)  # Caption bottom border

            user32.EndPaint(hwnd, byref(ps))
            return FALSE

        self.register_message_callback(WM_PAINT, _on_WM_PAINT)

        self.splitter = Splitter(
            parent_window,
            style = WS_CHILD | (WS_VISIBLE if style & WS_VISIBLE else 0),
            initial_pos = initial_pos,
            is_reversed = is_right
        )

    ########################################
    #
    ########################################
    def set_title(self, title):
        self.window_title = title

    ########################################
    #
    ########################################
    def show(self, show_cmd):
        self.splitter.show(show_cmd)
        super().show(show_cmd)

    ########################################
    #
    ########################################
    def set_child(self, child_window):
        self.child = child_window
        user32.SetParent(self.child.hwnd, self.hwnd)
        self.child.set_window_pos(0, 23, flags=SWP_NOSIZE)
        self.child.show()

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, DARK_BG_BRUSH if is_dark else COLOR_3DFACE + 1)
