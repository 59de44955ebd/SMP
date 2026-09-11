from ..controls.trackbar import *
from ..themes import *


########################################
# Wrapper Class
########################################
class TrackBar(TrackBar, FocusHandler):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        bg_color_dark = DARK_BG_COLOR,
        **kwargs
    ):
        self.bg_color_dark = bg_color_dark

        super().__init__(*args, **kwargs)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        # Update tooltip colors
        hwnd_tooltip = user32.SendMessageW(self.hwnd, TBM_GETTOOLTIPS, 0, 0)
        if hwnd_tooltip:
            uxtheme.SetWindowTheme(hwnd_tooltip, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetDCBrushColor(wparam, self.bg_color_dark if self.is_dark else self.bg_color)
            return gdi32.GetStockObject(DC_BRUSH)
