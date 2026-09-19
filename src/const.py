import os
import sys

from resources import *

IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    APP_DIR = os.path.dirname(__file__)
    RES_DIR = APP_DIR
else:
    APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    RES_DIR = os.path.join(APP_DIR, 'resources')

IDX_MENU_AUDIO = 2
IDX_MENU_VIDEO = 3
IDX_MENU_SUB = 4

IDX_STATUSBAR_PART_STATE = 0
IDX_STATUSBAR_PART_TIME = 1

ID_TIMER_UPDATE_TIME = 5000
TIME_DISPLAY_UPDATE_PERIOD = 250
TIME_DISPLAY_UPDATE_STATUS_EVERY = 4
SEEK_RANGE = 10000

STATE_STOPPED = 1
STATE_PAUSED = 2
STATE_PLAYING = 3

MIN_PROGRESS_DURATION = 5

VOLUME_STEP = 5

THEME_AUTO = 0
THEME_LIGHT = 1
THEME_DARK = 2

COLOR_KEYS = ['brightness', 'contrast', 'hue', 'saturation', 'gamma']

ENGINES = {
    IDM_ENGINE_DIRECTSHOW: 'DirectShow',
    IDM_ENGINE_MPV: 'mpv',
    IDM_ENGINE_VLC: 'VLC',
    IDM_ENGINE_WEBVIEW: 'WebView'
}

RATIOS = {
    IDM_RATIO_DEFAULT: '',
    IDM_RATIO_4_3: '4:3',
    IDM_RATIO_5_4: '5:4',
    IDM_RATIO_16_9: '16:9',
    IDM_RATIO_16_10: '16:10',
    IDM_RATIO_235_100: '235:100',
    IDM_RATIO_185_100: '185:100',
    IDM_RATIO_NONE: None,
}
