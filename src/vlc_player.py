import os
import sys
import time

from winapp.dlls import *
from winapp.const import *

from const import *

import vlc

TIMER_ID_END_REACHED = 1
TIMER_ID_PLAYING = 2

def init(vlc_path):
#    vlc.dll = CDLL(os.path.join(vlc_path, 'libvlc.dll'))
#    vlc.plugin_path = vlc_path
    vlc.init(vlc_path)

########################################
#
########################################
class Player():

    ########################################
    #
    ########################################
    def __init__(self, window, volume = .75):

        self._window = window
        self._fullscreen = False

        self._has_audio = False
        self._has_video = False
        self._is_midi = False
        self._duration = 0
        self._loop = False
        self._volume = volume

        options = ["--quiet", "--no-osd", f"--soundfont={os.path.join(RES_DIR, 'soundbank.sf2')}"]
        self._vlcInstance = vlc.Instance(options)

        self._player = self._vlcInstance.media_player_new()
        self._player.set_hwnd(window.hwnd)
        self._player.audio_set_volume(int(volume * 100))

        self._player.video_set_mouse_input(False)
        self._player.video_set_key_input(False)

        self._media = None

        self._player_event_manager = self._player.event_manager()

        ########################################
        #
        ########################################
        def _on_WM_TIMER(hwnd, wparam, lparam):
            user32.KillTimer(self._window.hwnd, wparam)

            if wparam == TIMER_ID_END_REACHED:
                self._handle_end_reached()

            elif wparam == TIMER_ID_PLAYING:
                self._player.audio_set_volume(int(self._volume * 100))

        self._window.register_message_callback(WM_TIMER, _on_WM_TIMER)

    ########################################
    #
    ########################################
    def _handle_end_reached(self):
        self._player.stop()
        if self._loop:
            self._player.play()
        self._media_event_manager.event_attach(vlc.EventType.MediaStateChanged, self._on_state_changed)

    ########################################
    #
    ########################################
    def _on_state_changed(self, e):

        if e.u.new_state == vlc.State.Ended:
            # Prevent that event is called twice, for whatever reason
            self._media_event_manager.event_detach(vlc.EventType.MediaStateChanged)

            # We can't call the player directly from the event callback
            user32.SetTimer(self._window.hwnd, TIMER_ID_END_REACHED, 0, 0)

        elif e.u.new_state == vlc.State.Playing:
            user32.SetTimer(self._window.hwnd, TIMER_ID_PLAYING, 0, 0)

    ########################################
    #
    ########################################
    def close_file(self):
        if self._media is not None:
            self._player.stop()
            self._player.set_media(None)
#            self._media_event_manager.event_detach(vlc.EventType.MediaParsedChanged)  # Needed???
#            self._media_event_manager.event_detach(vlc.EventType.MediaStateChanged)  # Needed???
            self._media_event_manager = None
            self._media.release()
            self._media = None

            self._has_audio = False
            self._has_video = False
            self._is_midi = False
            self._duration = 0

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed, **kwargs) -> bool:
        self.close_file()

        self._media = self._vlcInstance.media_new(media_file)
        self._media.add_option(":avcodec-hw=none")  # Needed for adjusting video on old/bad GPUs
        self._media_event_manager = self._media.event_manager()

        ext = os.path.splitext(media_file)[1].lower()
        self._is_midi = ext in ('.mid', '.rmi', '.kar')

        ########################################
        #
        ########################################
        def _on_parsed(e):
            it = self._media.tracks_get()
            if it:
                ok = True
                for info in it:
                    if info.type == vlc.TrackType.audio:
                        self._has_audio = True
                    elif info.type == vlc.TrackType.video:
                        self._has_video = True
                self._duration = self._media.get_duration() / 1000
            else:
                ok = False
            on_parsed(ok)

        self._media_event_manager.event_attach(vlc.EventType.MediaParsedChanged, _on_parsed)
        self._media_event_manager.event_attach(vlc.EventType.MediaStateChanged, self._on_state_changed)

        self._player.set_media(self._media)
        self._player.play()

        return True

    ########################################
    #
    ########################################
    def get_audio_tracks(self):
        audio_tracks = []
        try:
            track_names = {row[0]: row[1] for row in self._player.audio_get_track_description()}
            it = self._media.tracks_get()
            if it:
                active_track_id = self._player.audio_get_track()
                for info in it:
                    if info.type == vlc.TrackType.audio:
                        s = hex(info.codec)
                        codec = ''.join(reversed(list(chr(int(s[i:i+2], 16)) for i in range(2, len(s), 2))))
                        audio_tracks.append([info.id, f'{track_names[info.id].decode()} ({codec})', info.id == active_track_id])
        except:
            pass
        return audio_tracks

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id):
        self._player.audio_set_track(track_id)

    ########################################
    #
    ########################################
    def get_video_tracks(self):
        video_tracks = []
        try:
            track_names = {row[0]: row[1] for row in self._player.video_get_track_description()}
            it = self._media.tracks_get()
            if it:
                active_track_id = self._player.video_get_track()
                for info in it:
                    if info.type == vlc.TrackType.video:
                        s = hex(info.codec)
                        codec = ''.join(reversed(list(chr(int(s[i:i+2], 16)) for i in range(2, len(s), 2))))
                        video_tracks.append([info.id, f'{track_names[info.id].decode()} ({codec})', info.id == active_track_id])
        except:
            pass
        return video_tracks

    ########################################
    #
    ########################################
    def select_video_track(self, track_id):
        self._player.video_set_track(track_id)
        self.skip_back(1)

    ########################################
    #
    ########################################
    def get_sub_tracks(self):
        subs_tracks = []
        try:
            active_track_id = self._player.video_get_spu()
            for row in self._player.video_get_spu_description():
                track_id, name = row
                if track_id == -1:
                    continue
                subs_tracks.append([track_id, name.decode(), track_id == active_track_id])
        except:
            pass
        return subs_tracks

    ########################################
    #
    ########################################
    def select_sub_track(self, track_id):
        self._player.video_set_spu(track_id)

    ########################################
    #
    ########################################
    def load_sub_file(self, sub_file: str):
        ok = bool(self._player.video_set_subtitle_file(sub_file))
        if ok:
            time.sleep(.5)  # Otherwise get_sub_tracks() misses new sub
        return ok

    ########################################
    #
    ########################################
    def hide_subtitles(self, flag: bool = True):
        if flag:
            self._player.video_set_spu(-1)
        else:
            it = self._media.tracks_get()
            if it:
                for info in it:
                    if info.codec == 0x74627573:  # 'tsub'
                        self._player.video_set_spu(info.id)
                        break

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
        if self._duration == 0:
            self._player.stop()
        else:
            self._player.pause()

    ########################################
    #
    ########################################
    def play(self):
        self._player.play()

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        return self._player.is_playing()

    ########################################
    #
    ########################################
    def stop(self):
        self._player.stop()

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        #return self._player.audio_get_volume() / 100  # Doesn't work if player is stopped
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        self._volume = max(0, min(1, v))
        # For some weird reason VLC doesn't allow to set the volume in stopped state.
        # To handle this we set the volume whenever the player resumes playing.
        if self._player.get_state() != vlc.State.Stopped:
            self._player.audio_set_volume(int(self._volume * 100))

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        self._loop = flag

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        return self._duration
#        return self._media.get_duration() / 1000  # Wrong for livestreams when called later

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        return self._player.video_get_size()

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        return self._player.get_time() / 1000

    ########################################
    #
    ########################################
    def set_time(self, secs):
        self._player.set_time(int(secs * 1000))

    ########################################
    #
    ########################################
    def is_seekable(self) -> bool:
#        return self._player.is_seekable()  # Wrong for livestreams
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
        self.set_time(max(0, self.get_time() - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs):
        t = self.get_time() + secs
        if self._duration:
            t = min(self._duration, t)
        self.set_time(t)

    ########################################
    #
    ########################################
    def step_back(self, frames=1):
        fps = self._player.get_fps()
        if not fps:
            return
        ms = max(0, int(self._player.get_time() - frames * 1000 / fps))
        self._player.set_time(ms)

    ########################################
    #
    ########################################
    def step_forward(self, frames=1):
        fps = self._player.get_fps()
        if not fps:
            return
        t = self.get_time() + frames / fps
        if self._duration:
            t = min(self._duration, t)
        self._player.set_time(int(t * 1000))

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str, callback):
        res = self._player.video_take_snapshot(0, filename, 0, 0)
        if res == 0:
            callback('PNG')

    ########################################
    # -1..1
    ########################################
    def set_brightness(self, value: float):
        self._player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
        v = 1.0 + value
        self._player.video_set_adjust_float(vlc.VideoAdjustOption.Brightness, v)

    ########################################
    # -1..1
    ########################################
    def set_contrast(self, value: float):
        self._player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
        v = 1.0 + value
        self._player.video_set_adjust_float(vlc.VideoAdjustOption.Contrast, v)

    ########################################
    # -1..1
    ########################################
    def set_hue(self, value: float):
        self._player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
        v = value * 180
        self._player.video_set_adjust_float(vlc.VideoAdjustOption.Hue, v)

    ########################################
    # -1..1
    ########################################
    def set_saturation(self, value: float):
        self._player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
        v = 1.0 + value
        self._player.video_set_adjust_float(vlc.VideoAdjustOption.Saturation, v)

    ########################################
    # -1..1
    ########################################
    def set_gamma(self, value: float):
        self._player.video_set_adjust_int(vlc.VideoAdjustOption.Enable, 1)
        v = 1.0 + value
        self._player.video_set_adjust_float(vlc.VideoAdjustOption.Gamma, v)

    ########################################
    # e.g. '4:3', '' to reset to default, None means resize to window
    ########################################
    def set_aspect_ratio(self, ratio):

        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self._player.video_set_aspect_ratio(f'{width}:{height}')

        if ratio is None:
            rc = self._window.get_client_rect()
            self._player.video_set_aspect_ratio(f'{rc.right}:{rc.bottom}')
            self._window.register_message_callback(WM_SIZE, _on_WM_SIZE)

        else:
            self._window.unregister_message_callback(WM_SIZE)
            self._player.video_set_aspect_ratio(ratio)
