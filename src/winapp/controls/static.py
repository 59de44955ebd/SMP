# https://learn.microsoft.com/en-us/windows/win32/controls/static-controls
from ..window import *


########################################
# Wrapper Class
########################################
class Static(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None,
        wrap_hwnd = None,
#        bg_color = 0xffffff
    ):
        super().__init__(
            WC_STATIC,
            parent_window = parent_window,
            style = style,
            ex_style=ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd
        )

#        self.bg_color = bg_color

#        self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)

    ########################################
    #
    ########################################
#    def destroy_window(self):
#        self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
#        super().destroy_window()

    ########################################
    #
    ########################################
#    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
#        if lparam == self.hwnd:
#            gdi32.SetBkColor(wparam, self.bg_color)
#            gdi32.SetDCBrushColor(wparam, self.bg_color)
#            return gdi32.GetStockObject(DC_BRUSH)
