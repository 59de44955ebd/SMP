from winapp.window import *
from winapp.themes import *
from winapp.controls_themed.tooltips import *

SLIDER_CLASS_NAME = 'SliderClass'

EVENT_POS_CHANGED = 1

SLIDER_BG_BRUSH = COLOR_3DFACE + 1
SLIDER_BG_BRUSH_DARK = gdi32.CreateSolidBrush(0x171717)

BAR_BRUSH = gdi32.CreateSolidBrush(0xFFD0A0)  #0xDBCDBF)  #F2E1D5)
BAR_BRUSH_DARK = DARK_CONTROL_BG_BRUSH  #gdi32.CreateSolidBrush(0xD77800)  #0xB16B25)  #B76E25)  # HIGHLIGHT_BRUSH

BORDER_BRUSH = gdi32.CreateSolidBrush(0x848484)
DARK_BORDER_BRUSH = gdi32.CreateSolidBrush(0)

KNOB_BRUSH = gdi32.CreateSolidBrush(0xD77800)

_windowproc = WNDPROC(user32.DefWindowProcW)

_slider_class = WNDCLASSEXW()
_slider_class.lpfnWndProc = _windowproc
_slider_class.style = CS_VREDRAW | CS_HREDRAW | CS_GLOBALCLASS
_slider_class.lpszClassName = SLIDER_CLASS_NAME
_slider_class.hbrBackground = SLIDER_BG_BRUSH
_slider_class.hCursor = user32.LoadCursorW(0, IDC_ARROW)
user32.RegisterClassExW(byref(_slider_class))


########################################
#
########################################
class MySlider(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = WS_EX_COMPOSITED,
        left = 0, top = 0, width = 0, height = 0,
        wrap_hwnd = None,
        initial_pos = 0,
        show_knob = False,
        show_text = False,
        show_tooltip = False,
    ):
        self.pos = initial_pos
        self.width = width
        self.height = height
        self.show_knob = show_knob
        self.show_text = show_text

        self.is_down = False

        super().__init__(
            SLIDER_CLASS_NAME,
            style = style,
            ex_style = ex_style,
            parent_window = parent_window,
            wrap_hwnd = wrap_hwnd,
            left = left, top = top, width = width, height = height,
        )

        ########################################
        #
        ########################################
        def _on_WM_PAINT(hwnd, wparam, lparam):
            ps = PAINTSTRUCT()
            hdc = user32.BeginPaint(hwnd, byref(ps))

            x = round((self.width - 1) * self.pos)

            user32.FillRect(hdc, byref(RECT(0, 0, x + 1, self.height)), BAR_BRUSH_DARK if self.is_dark else BAR_BRUSH)
            if self.show_knob:
                user32.FillRect(hdc, byref(RECT(x - 1, 0, x + 2, self.height)), KNOB_BRUSH)

            rc = RECT(0, 0, self.width, self.height)

            user32.FrameRect(hdc, byref(rc), DARK_BORDER_BRUSH if self.is_dark else BORDER_BRUSH)

            if self.show_text:
                gdi32.SetBkMode(hdc, TRANSPARENT)
                gdi32.SetTextColor(hdc, DARK_TEXT_COLOR if self.is_dark else 0x000000)
                gdi32.SelectObject(hdc, self.h_font)
                rc.top += 1
                user32.DrawTextW(hdc, f'{round(100 * self.pos)}%', -1, rc, DT_SINGLELINE | DT_CENTER | DT_VCENTER)

            user32.EndPaint(hwnd, byref(ps))
            return FALSE

        self.register_message_callback(WM_PAINT, _on_WM_PAINT)

        ########################################
        #
        ########################################
        def _on_WM_MOUSEMOVE(hwnd, wparam, lparam):
            self.pos = max(0, min(1, GET_X_LPARAM(lparam) / (self.width - 1)))
            user32.InvalidateRect(self.hwnd, None, TRUE)
            self.emit(EVENT_POS_CHANGED, self.pos)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):
            self.is_down = True
            self.pos = GET_X_LPARAM(lparam) / (self.width - 1)
            user32.InvalidateRect(hwnd, None, TRUE)
            self.emit(EVENT_POS_CHANGED, self.pos)
            self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)
            user32.SetCapture(hwnd)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONUP(hwnd, wparam, lparam):
            self.is_down = False
            user32.ReleaseCapture()
            self.unregister_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)

        self.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)
        self.register_message_callback(WM_LBUTTONUP, _on_WM_LBUTTONUP)

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            self.width = lparam & 0xFFFF

        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

        if show_tooltip:
            self.tooltips = Tooltips(
                self,
                style = WS_POPUP | TTS_ALWAYSTIP | TTS_NOANIMATE | TTS_NOFADE
            )
            toolInfo = TOOLINFOW()
            toolInfo.hwnd = self.parent_window.hwnd
            toolInfo.uFlags = TTF_IDISHWND | TTF_SUBCLASS
            toolInfo.uId = self.hwnd
            toolInfo.lpszText = LPSTR_TEXTCALLBACKW
            self.tooltips.send_message(TTM_ADDTOOLW, 0, byref(toolInfo))

            ########################################
            #
            ########################################
            def _on_WM_MOUSEMOVE2(hwnd, wparam, lparam):
                if not self.is_down:
                    self.tooltips.send_message(TTM_POPUP, 0, 0)

            self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE2)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        user32.SetClassLongPtrW(self.hwnd, GCL_HBRBACKGROUND, SLIDER_BG_BRUSH_DARK if is_dark else SLIDER_BG_BRUSH)

    ########################################
    #
    ########################################
    def set_pos(self, pos):
        self.pos = pos
        user32.InvalidateRect(self.hwnd, None, TRUE)
