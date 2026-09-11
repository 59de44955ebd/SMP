from ..controls.static import *
from ..themes import *


########################################
# Wrapper Class
########################################
class Static(Static):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        bg_color = 0xffffff,
        bg_color_dark = DARK_BG_COLOR,
        **kwargs
    ):
        self.bg_color = bg_color
        self.bg_color_dark = bg_color_dark

        super().__init__(*args, **kwargs)

        self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetTextColor(wparam, DARK_TEXT_COLOR if self.is_dark else 0x000000)
            gdi32.SetBkColor(wparam, self.bg_color_dark if self.is_dark else self.bg_color)
            gdi32.SetDCBrushColor(wparam, self.bg_color_dark if self.is_dark else self.bg_color)
            return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        self.force_redraw_window()  # triggers WM_CTLCOLORSTATIC
