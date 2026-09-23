import base64
import os
import re
from webview2 import *

from winapp.const import *
from winapp.themes import *
from winapp.window import *

from const import *

SETTINGS.ADDITIONAL_BROWSER_ARGUMENTS = '--allow-file-access-from-files --disable-web-security'
SETTINGS.DEFAULT_CONTEXT_MENUS_ENABLED = False
# Use a local profile folder
if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')


########################################
#
########################################
class Player(WebView2):

    ########################################
    #
    ########################################
    def __init__(self,  parent_window, volume = .75):
        self._window = parent_window
        self._volume = volume

        self._fullscreen = False

        self._media_file = None
        self._subs_files = []
        self._sub_idx = -1

        self._has_audio = False
        self._has_video = False
        self._is_midi = False

        self._duration = 0
        self._width = 0
        self._height = 0
        self._time = 0
        self._playing = False

        self._image_values = {
            'brightness': 0,
            'contrast': 0,
            'hue': 0,
            'saturation': 0
        }

        self._initialized = False

        super().__init__(
            parent_hwnd = parent_window.hwnd,
            url = 'file:///' + os.path.join(RES_DIR, 'index.htm').replace('\\', '/'),
            is_hidden = True,
        )

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self.put_bounds(RECT(0, 0, width, height))

        parent_window.register_message_callback(WM_SIZE, _on_WM_SIZE)

        ########################################
        #
        ########################################
        def _on_dom_content_loaded(webview):

            ########################################
            #
            ########################################
            def _on_parsed(ok, width, height, duration, has_audio):
                if ok:
                    self._width = width
                    self._height = height
                    self._duration = duration or 0
                    self._has_audio = has_audio
                    self._has_video = height > 0
                self.on_parsed(ok)

            self.expose('on_parsed', _on_parsed)

            ########################################
            #
            ########################################
            def _on_time_update(t):
                self._time = t

            self.expose('on_time_update', _on_time_update)

            ########################################
            #
            ########################################
            def _on_state_change(is_playing):
                self._playing = bool(is_playing)

            self.expose('on_state_change', _on_state_change)

            ########################################
            #
            ########################################
            def _on_initialized():
                self._initialized = True
                user32.SetWindowLongA(self.hwnd, GWL_STYLE, WS_CHILD | WS_VISIBLE | WS_DISABLED)
                self.execute_js(f'player.set_volume({self._volume});')

                for k, v in self._image_values.items():
                    if v != 0:
                        getattr(self, f'set_{k}')(v)

                if self._media_file:
                    self._load(self._media_file)
                    self._media_file = None

            self.expose('on_initialized', _on_initialized)

        self.connect(EVENT.DOM_CONTENT_LOADED, _on_dom_content_loaded)

    ########################################
    #
    ########################################
    def close_file(self):
        if self._initialized:
            self.execute_js('player.close();')

        self._media_file = None
        self._sub_files = []
        self._sub_idx = -1

        self._has_audio = False
        self._has_video = False
        self._is_midi = False

        self._duration = 0
        self._width = 0
        self._height = 0
        self._time = 0
        self._playing = False

        self.set_visible(False)

    ########################################
    #
    ########################################
    def _load(self, media_file):
        ext = os.path.splitext(media_file)[1].lower()
        self._is_midi = ext in ('.mid', '.rmi')
        is_local = '://' not in media_file
        self._sub_files = []
        if is_local:
            is_video = ext in ('.mp4', '.mov', '.mkv', '.ogv', '.webm')
            if is_video:
                base_name = os.path.splitext(os.path.basename(media_file))[0]
                d = os.path.dirname(media_file)
                pat = re.compile(base_name + r'(\..+){0,1}.(srt|vtt|webvtt)', flags = re.I)
                self._sub_files = [os.path.join(d, f) for f in os.listdir(d) if pat.match(f)]

            media_file = f"file:///{media_file.replace('\\', '/')}"

        self.execute_js(f'player.load("{media_file}", {int(self._is_midi)});')

        if self._sub_files:
            self.execute_js(f'player.load_subs("file:///{self._sub_files[0].replace('\\', '/')}");')
            self._sub_idx = 0

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed, **kwargs) -> bool:
        if self._media_file:
            self.close_file()
        self.on_parsed = on_parsed
        if self._initialized:
            self._load(media_file)
        else:
            self._media_file = media_file
        self.set_visible(True)

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id):
        self._player.audio_set_track(track_id)

    ########################################
    #
    ########################################
    def get_sub_tracks(self):
        return [(i, os.path.basename(f), i == self._sub_idx) for i, f in enumerate(self._sub_files)]

    ########################################
    #
    ########################################
    def select_sub_track(self, track_id):
        if track_id == -1:
            self.execute_js(f'player.hide_subs(1);')
        else:
            self.execute_js(f'player.load_subs("file:///{self._sub_files[track_id].replace('\\', '/')}");')
        self._sub_idx = track_id

    ########################################
    # TODO: check if successfully loaded?
    ########################################
    def load_sub_file(self, sub_file: str):
        self._sub_files.append(sub_file)
        self._sub_idx = len(self._sub_files) - 1

        if self._initialized:
            self.execute_js(f'player.load_subs("file:///{sub_file.replace('\\', '/')}");')
        return True

    ########################################
    #
    ########################################
    def hide_subtitles(self, flag: bool = True):
        if self._initialized:
            self.execute_js(f'player.hide_subs({int(flag)});')

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
    def is_midi(self) -> bool:
        return self._is_midi

    ########################################
    #
    ########################################
    def pause(self):
        self._playing = False
        if self._initialized:
            self.execute_js('player.pause();')

    ########################################
    #
    ########################################
    def play(self):
        self._playing = True
        if self._initialized:
            self.execute_js('player.play();')

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        return self._playing

    ########################################
    #
    ########################################
    def stop(self):
        self._playing = False
        if self._initialized:
            self.execute_js('player.stop();')

    ########################################
    #
    ########################################
    def get_volume(self) -> float:
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        self._volume = v
        if self._initialized:
            self.execute_js(f'player.set_volume({v});')

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        if self._initialized:
            flag = 'true' if flag else 'false'
            self.execute_js(f'player.set_loop({flag});')

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        return self._duration

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        return (self._width, self._height)

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        return self._time

    ########################################
    #
    ########################################
    def set_time(self, sec: float):
        self._time = sec
        if self._initialized:
            self.execute_js(f'player.set_time({sec});')

    ########################################
    #
    ########################################
    def is_seekable(self) -> bool:
        return self._duration > 0

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
    def skip_back(self, secs):
        self.set_time(max(0, self._time - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs):
        t = self._time + secs
        if self._duration:
            t = min(self._duration, t)
        self.set_time(t)

    ########################################
    # No web API available for finding FPS, so we pretend it's 25
    ########################################
    def step_back(self, frames=1):
        self.set_time(max(0, self._time - frames / 25))

    ########################################
    # No web API available for finding FPS, so we pretend it's 25
    ########################################
    def step_forward(self, frames=1):
        t = self._time + frames / 25
        if self._duration:
            t = min(self._duration, t)
        self.set_time(t)

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str, callback):

        ########################################
        #
        ########################################
        def _on_get_video_image(error_code, png_data_url):
            if error_code == 0:
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(png_data_url[22:-1]))
                callback('PNG')

        self.execute_js('player.get_video_image()', _on_get_video_image)

    ########################################
    # value: -1..1
    ########################################
    def set_brightness(self, value: float):
        if self._initialized:
            value = int(100 + value * 100)
            self.execute_js(f'player.set_brightness({value});')
        else:
            self._image_values['brightness'] = value

    ########################################
    # value: -1..1
    ########################################
    def set_contrast(self, value: float):
        if self._initialized:
            value = int(100 + value * 100)
            self.execute_js(f'player.set_contrast({value});')
        else:
            self._image_values['contrast'] = value

    ########################################
    # value: -1..1
    ########################################
    def set_saturation(self, value: float):
        if self._initialized:
            value = int(100 + value * 100)
            self.execute_js(f'player.set_saturation({value});')
        else:
            self._image_values['saturation'] = value

    ########################################
    # value: -1..1
    ########################################
    def set_hue(self, value: float):
        if self._initialized:
            value = int(360 + value * 180)
            self.execute_js(f'player.set_hue({value});')
        else:
            self._image_values['hue'] = value

    ########################################
    # e.g. '4:3', '' to reset to default, None means resize to window
    ########################################
    def set_aspect_ratio(self, ratio: str):
        if ratio:
            ax, ay = ratio.split(':')
            self.execute_js(f'player.set_aspect_ratio({ax},{ay});')
        elif ratio is None:
            self.execute_js(f'player.set_aspect_ratio(0);')
        else:
            self.execute_js(f'player.set_aspect_ratio();')
