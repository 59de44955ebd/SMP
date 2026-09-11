import os
import sys

APP_NAME = 'SMP'
APP_CLASS = 'SMPClass'
APP_VERSION = '0.1'

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
