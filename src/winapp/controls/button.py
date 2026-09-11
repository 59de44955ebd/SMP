# https://learn.microsoft.com/en-us/windows/win32/controls/buttons
from ..window import *


########################################
# Button Control Structures
########################################
#class BUTTON_IMAGELIST(Structure):
#    _fields_ = [
#        ("himl", HANDLE),
#        ("margin", RECT),
#        ("uAlign", UINT),
#    ]


########################################
# Wrapper Class
########################################
class Button(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 94, height = 23,
        window_title = 'OK',
        wrap_hwnd = None,
        bg_color = 0xffffff
    ):
        super().__init__(
            WC_BUTTON,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd
        )

        self.bg_color = bg_color

        self.parent_window.register_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)

    ########################################
    #
    ########################################
    def destroy_window(self):
        self.parent_window.unregister_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)
        super().destroy_window()

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORBTN(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
#            gdi32.SetBkColor(wparam, self.bg_color)
            gdi32.SetDCBrushColor(wparam, self.bg_color)
            return gdi32.GetStockObject(DC_BRUSH)
