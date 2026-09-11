from winapp.window import *
from winapp.themes import *


########################################
#
########################################
class MyStatusBar(Window):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, visible):
#        self.parts = (0, 120, 165)
#        self.part_alignment = [DT_LEFT, DT_CENTER, DT_RIGHT]

        self.parts = (0, 165)
        self.part_alignment = [DT_LEFT, DT_RIGHT]

        super().__init__(
            WC_STATUSBAR,
            parent_window = parent_window,
            style = WS_CHILD | (WS_VISIBLE if visible else 0),
        )

        # get height of statusbar
        rc = RECT()
        user32.SendMessageW(self.hwnd, SB_GETRECT, 0, byref(rc))
        self.height = rc.bottom

        self.register_message_callback(WM_PAINT, self._on_WM_PAINT)
        self.register_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)

        self.visible = visible

    ########################################
    #
    ########################################
#    def right_align_parts(self, width):
#        status_parts_count = len(self.parts)
#        sb_parts = (INT * status_parts_count)(160, width - 160, -1)
#        user32.SendMessageW(self.hwnd, SB_SETPARTS, status_parts_count, sb_parts)

    ########################################
    #
    ########################################
    def right_align_parts(self, width):
        status_parts_count = len(self.parts)
        sb_parts = (INT * status_parts_count)()
        for i in range(status_parts_count - 1):
            sb_parts[i] = width - sum(self.parts[i + 1:])
        sb_parts[status_parts_count - 1] = -1
        user32.SendMessageW(self.hwnd, SB_SETPARTS, status_parts_count, sb_parts)

    ########################################
    #
    ########################################
    def _on_WM_ERASEBKGND(self, hwnd, wparam, lparam):
        return 0

    ########################################
    #
    ########################################
    def _on_WM_PAINT(self, hwnd, wparam, lparam):
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(self.hwnd, byref(ps))

        user32.FillRect(hdc, byref(ps.rcPaint), DARK_BG_BRUSH if self.is_dark else COLOR_3DFACE + 1)

        user32.FillRect(hdc, byref(RECT(ps.rcPaint.left, ps.rcPaint.top, ps.rcPaint.right, ps.rcPaint.top + 1)), DARK_SEPARATOR_BRUSH if self.is_dark else SEPARATOR_BRUSH)

        gdi32.SelectObject(hdc, self.h_font)
        gdi32.SetBkMode(hdc, TRANSPARENT)

        if self.is_dark:
            gdi32.SetTextColor(hdc, DARK_TEXT_COLOR)

        rc_part = RECT()

        for i in range(len(self.parts)):
            user32.SendMessageW(self.hwnd, SB_GETRECT, i, byref(rc_part))

            if i == 0:
                rc_part.left += 9
            elif i == len(self.parts) - 1:
                rc_part.right += 5

            if ps.rcPaint.left >= rc_part.right or ps.rcPaint.right < rc_part.left:
                continue

            # Draw text
            text_len = user32.SendMessageW(self.hwnd, SB_GETTEXTLENGTHW, i, 0)
            buf = create_unicode_buffer(text_len + 1)
            user32.SendMessageW(self.hwnd, SB_GETTEXTW, i, buf)
            user32.DrawTextW(
                hdc, buf.value, text_len,
                byref(RECT(rc_part.left + 2, rc_part.top + 1, rc_part.right, rc_part.bottom - 1)),
                DT_SINGLELINE | DT_VCENTER | self.part_alignment[i]
            )

        user32.EndPaint(self.hwnd, byref(ps))
        return 0

    ########################################
    #
    ########################################
    def set_text(self, msg='', part = 0):
        user32.SendMessageW(self.hwnd, SB_SETTEXTW, part, msg)

    ########################################
    #
    ########################################
    def update_size(self, width = 0):
        user32.SendMessageW(self.hwnd, WM_SIZE, 0, 0)
        self.right_align_parts(width)
