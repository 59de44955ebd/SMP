import os
import sys
import time

from winapp.const import *
from winapp.dlls import *
from winapp.themes import *

from const import *

import mpv

def init(dll_dir):
    mpv.init(os.path.join(dll_dir, 'libmpv-2.dll'))


########################################
#
########################################
class Player():

    ########################################
    #
    ########################################
    def __init__(
        self,
        window: object,
        volume: float = .75
    ):
        self._window = window
        self._fullscreen = False
        self._has_audio = False
        self._has_video = False
        self._duration = 0
        self._loop = False
        self._volume = volume
        self._filename = None
        self.hwnd = None

        self._player = mpv.MPV()
        self._player.wid = window.hwnd
        self._player.volume = int(volume * 100)
        self._player.keep_open = 'yes'  # causes END_FILE never triggered

    ########################################
    #
    ########################################
    def close_file(self):
        if self._filename:
            if self.hwnd:
                user32.ShowWindow(self.hwnd, SW_HIDE)
            self._player.stop()
            self._filename = None
            self._has_audio = False
            self._has_video = False
            self._duration = 0

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed, **kwargs) -> bool:
        self.close_file()
        self._player.loadfile(media_file)

        ########################################
        #
        ########################################
        def _on_metadata(property_name, data):
            if data is not None:
                # mpv does something nasty when a new video window is injected into
                # the container, (forced) dark menus are reset to light mode.
                # This fixes it.
                uxtheme.SetPreferredAppMode(PreferredAppMode.ForceDark if self._window.is_dark else PreferredAppMode.ForceLight)

                self._player.unobserve_property('metadata', _on_metadata)
                self._filename = media_file
                self._duration = self._player.duration
                self._track_list = self._player.track_list
                for row in self._track_list:
                    if row['type'] == 'audio':
                        self._has_audio = True
                    elif row['type'] == 'video':
                        self._has_video = True
                on_parsed(True)

        self._player.observe_property('metadata', _on_metadata)

        ########################################
        #
        ########################################
        def _on_window(property_name, data):
            self.hwnd = data

        self._player.observe_property('window-id', _on_window)

        return True

    ########################################
    #
    ########################################
    def get_audio_tracks(self) -> list:
        audio_tracks = []
        for row in self._track_list:
            if row['type'] == 'audio':
                try:
                    info = f" - {row['metadata']['language']}"
                except:
                    info = ''
                audio_tracks.append([row['id'], f"Track {row['id']}{info} ({row['codec']})", row['selected']])
        return audio_tracks

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id: int):
        self._player.aid = str(track_id)

    ########################################
    #
    ########################################
    def get_video_tracks(self) -> list:
        video_tracks = []
        for row in self._track_list:
            if row['type'] == 'video':
                try:
                    info = f" - {row['metadata']['language']}"
                except:
                    info = ''
                video_tracks.append([row['id'], f"Track {row['id']}{info} ({row['codec']})", row['selected']])
        return video_tracks

    ########################################
    #
    ########################################
    def select_video_track(self, track_id: int):
        self._player.vid = str(track_id)
#        self.skip_back(1)

    ########################################
    #
    ########################################
    def get_sub_tracks(self) -> list:
        subs_tracks = []
        for row in self._player.track_list:
            if row['type'] == 'sub':
                info = f" - {row['title']}" if 'title' in row else ''
                subs_tracks.append([row['id'], f"Track {row['id']}{info} ({row['codec']})", row['selected']])
        return subs_tracks

    ########################################
    #
    ########################################
    def select_sub_track(self, track_id: int):
        if track_id == -1:
            self._player.sid = 'no'
        else:
            self._player.sid = str(track_id)

    ########################################
    #
    ########################################
    def load_sub_file(self, sub_file: str):
        try:
            self._player.sub_add(sub_file)
            return True
        except:
            return False

    ########################################
    #
    ########################################
    def hide_subtitles(self, flag: bool = True):
        if flag:
            self._player.sid = 'no'
        else:
            self._player.sid = 'auto'

    ########################################
    #
    ########################################
    def has_video(self) -> bool:
        return self._has_video

    ########################################
    #
    ########################################
    def has_audio(self) -> bool:
        return self._has_audio

    ########################################
    #
    ########################################
    def pause(self):
        self._player.pause = True

    ########################################
    #
    ########################################
    def play(self):
        self._player.pause = False

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        return not self._player.pause

    ########################################
    #
    ########################################
    def stop(self):
        self._player.pause = True
        self._player.time_pos = 0

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        #return self._player.volume / 100
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        self._volume = max(0, min(1, v))
        self._player.volume = int(self._volume * 100)

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        self._loop = flag
        self._player.loop = 'yes' if flag else 'no'

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        return self._duration

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        return (self._player.width, self._player.height)

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        return self._player.time_pos

    ########################################
    #
    ########################################
    def set_time(self, secs: float):
        self._player.time_pos = secs

    ########################################
    #
    ########################################
    def set_fullscreen(self, flag: bool):
        self._fullscreen = flag
        if self._fullscreen:
            self._window_parent_hwnd = user32.GetParent(self._window.hwnd)
            user32.SetParent(self._window.hwnd, None)
            user32.ShowWindow(self._window.hwnd, SW_SHOWMAXIMIZED)
        else:
            user32.ShowWindow(self._window.hwnd, SW_SHOWNORMAL)
            user32.SetParent(self._window.hwnd, self._window_parent_hwnd)

    ########################################
    #
    ########################################
    def is_fullscreen(self) -> bool:
        return self._fullscreen

    ########################################
    #
    ########################################
    def skip_back(self, secs: float):
        self._player.seek(-secs)
        if self._player.pause:
            time.sleep(.05)

    ########################################
    #
    ########################################
    def skip_forward(self, secs: float):
        self._player.seek(secs)
        if self._player.pause:
            time.sleep(.05)

    ########################################
    #
    ########################################
    def step_back(self, frames: int =1 ):
        for i in range(frames):
            self._player.frame_back_step()
        if self._player.pause:
            time.sleep(.05)

    ########################################
    #
    ########################################
    def step_forward(self, frames: int = 1):
        for i in range(frames):
            self._player.frame_step()
        if self._player.pause:
            time.sleep(.05)

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str, callback):
        try:
            self._player.screenshot_to_file(filename + '.png')
            callback('PNG', filename + '.png')
        except:
            pass

    ########################################
    # -1..1
    ########################################
    def set_brightness(self, value: float):
        self._player.brightness = int(value * 100)

    ########################################
    # -1..1
    ########################################
    def set_contrast(self, value: float):
        self._player.contrast = int(value * 100)

    ########################################
    # -1..1
    ########################################
    def set_hue(self, value: float):
        self._player.hue = int(value * 100)

    ########################################
    # -1..1
    ########################################
    def set_saturation(self, value: float):
        self._player.saturation = int(value * 100)

    ########################################
    # -1..1
    ########################################
    def set_gamma(self, value: float):
        self._player.gamma = int(value * 100)

    ########################################
    # e.g. '4:3', '' to reset to default, None means resize to window
    ########################################
    def set_aspect_ratio(self, ratio: str | None):
        if ratio is None:
            self._player.keepaspect = False
        else:
            if ratio:
                w, h = ratio.split(':')
                forced_ratio = int(w) / int(h)
            else:
                forced_ratio = -2
            self._player.video_aspect_override = forced_ratio
            self._player.keepaspect = True
