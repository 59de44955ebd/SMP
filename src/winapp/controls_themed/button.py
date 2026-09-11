from ..controls.button import *
from ..themes import *


########################################
# Wrapper Class
########################################
class Button(Button):

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

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORBTN(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetDCBrushColor(wparam, self.bg_color_dark if self.is_dark else self.bg_color)
            return gdi32.GetStockObject(DC_BRUSH)
