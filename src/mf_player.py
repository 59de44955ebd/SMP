import os
import time

from winapp.window import *

MFTIME = c_int64 #c_longlong
LPFLOAT = POINTER(FLOAT)
SIZE_T = c_longlong

_mf = None

def init(dll_file):
    global _mf
    _mf = CDLL(dll_file)
    #STDAPI Init(HWND hVideo, HWND hEvent)
    _mf.Init.argtypes = (HWND, HWND)
    #STDAPI CloseFile()
    #STDAPI GetAspectRatio(LPDWORD pRatio)
    _mf.GetAspectRatio.argtypes = (LPDWORD,)
    #STDAPI GetCapabilities(LPDWORD pCaps)
    _mf.GetCapabilities.argtypes = (LPDWORD,)
    #STDAPI GetCharacteristics(LPDWORD pCaps)
    _mf.GetCharacteristics.argtypes = (LPDWORD,)
    #STDAPI GetCurrentImage(BITMAPINFOHEADER *pBih, BYTE **pDib, DWORD *pcbDib, LONGLONG *pTimeStamp)
    _mf.GetCurrentImage.argtypes = (POINTER(BITMAPINFOHEADER), POINTER(LPBYTE), LPDWORD, POINTER(c_longlong))
    #STDAPI GetDuration(UINT64 *pDur)
    _mf.GetDuration.argtypes = (POINTER(MFTIME),)
    #STDAPI GetFrameRate(float *pfRate)
    _mf.GetFrameRate.argtypes = (LPFLOAT,)
    #STDAPI GetMetadata(BYTE **pData, DWORD *pDataSize)
    _mf.GetMetadata.argtypes = (POINTER(LPBYTE), LPDWORD)
    #STDAPI GetMute(BOOL *pbMute)
    _mf.GetMute.argtypes = (LPBOOL,)
    #STDAPI GetRate(float *pfRate)
    _mf.GetRate.argtypes = (LPFLOAT,)
    #STDAPI GetSize(LPDWORD pSize)
    _mf.GetSize.argtypes = (LPDWORD,)
    #STDAPI GetState(LPINT pState)
    _mf.GetState.argtypes = (LPINT,)
    #STDAPI GetStream(DWORD idx, LPDWORD pType, LPDWORD pFourCC, LPBOOL pSelected, LPWSTR lang, size_t lang_buf_size)
    _mf.GetStream.argtypes = (DWORD, LPDWORD, LPDWORD, LPBOOL, LPWSTR, SIZE_T)
    #STDAPI GetStreamCount(LPDWORD pCount)
    _mf.GetStreamCount.argtypes = (LPDWORD,)
    #STDAPI GetTime(MFTIME *pTime)
    _mf.GetTime.argtypes = (POINTER(MFTIME),)
    #STDAPI GetVolume(float *pfLevel)
    _mf.GetVolume.argtypes = (LPFLOAT,)
    #STDAPI HasAudio(LPBOOL pHasAudio)
    _mf.HasAudio.argtypes = (LPBOOL,)
    #STDAPI HasVideo(LPBOOL pHasVideo)
    _mf.HasVideo.argtypes = (LPBOOL,)
    #STDAPI LoadFile(LPCWSTR url)
    _mf.LoadFile.argtpyes = (LPCWSTR,)
    #STDAPI Pause()
    #STDAPI Play()
    #STDAPI Repaint()
    #STDAPI ResizeVideo(WORD width, WORD height)
    #STDAPI Scrub(BOOL bScrub)
    #STDAPI SelectAudioStream(DWORD idx)
    #STDAPI SelectVideoStream(DWORD idx)
    #STDAPI SetAspectRatioMode(DWORD mode)
    #STDAPI SetFullscreen(BOOL fFullscreen)
    #STDAPI SetMute(BOOL bMute)
    #STDAPI SetProcAmpValue(DWORD dwProperty, float value)
    _mf.SetProcAmpValue.argtypes = (DWORD, FLOAT)
    #STDAPI SetRate(float rate)
    _mf.SetRate.argtypes = (FLOAT,)
    #STDAPI SetTime(MFTIME time)
    _mf.SetTime.argtypes = (MFTIME,)
    #STDAPI SetVideoRect(RECT rc)
    _mf.SetVideoRect.argtypes = (RECT,)
    #STDAPI SetVolume(float fLevel)
    _mf.SetVolume.argtypes = (FLOAT,)
    #STDAPI Shutdown()
    #STDAPI Stop()

WM_APP_NOTIFY = WM_APP + 1

# Custom
STATE_CLOSED = 0        # No session.
STATE_READY = 1         # Session was created, ready to open a file.
STATE_OPEN_PENDING = 2  # Session is opening a file.
STATE_PLAYING = 3       # Session is playing a file.
STATE_PAUSED = 4        # Session is paused.
STATE_STOPPED = 5       # Session is stopped (ready to play).
STATE_CLOSING = 6       # Application has closed the session, but is waiting for MESessionClosed.

SCRUB_NONE = 0
SCRUB_ACTIVE = 1
SCRUB_CLOSING = 2

# Events
class Event:
    MEUnknown = 0
    MEError = 1
    MEExtendedType = 2
    MENonFatalError = 3
    MESessionUnknown = 100
    MESessionTopologySet = 101
    MESessionTopologiesCleared = 102
    MESessionStarted = 103
    MESessionPaused = 104
    MESessionStopped = 105
    MESessionClosed = 106
    MESessionEnded = 107
    MESessionRateChanged = 108
    MESessionScrubSampleComplete = 109
    MESessionCapabilitiesChanged = 110
    MESessionTopologyStatus = 111
    MESessionNotifyPresentationTime = 112
    MENewPresentation = 113
    MELicenseAcquisitionStart = 114
    MELicenseAcquisitionCompleted = 115
    MEIndividualizationStart = 116
    MEIndividualizationCompleted = 117
    MEEnablerProgress = 118
    MEEnablerCompleted = 119
    MEPolicyError = 120
    MEPolicyReport = 121
    MEBufferingStarted = 122
    MEBufferingStopped = 123
    MEConnectStart = 124
    MEConnectEnd = 125
    MEReconnectStart = 126
    MEReconnectEnd = 127
    MERendererEvent = 128
    MESessionStreamSinkFormatChanged = 129
    MESourceUnknown = 200,
    MESourceStarted = 201
    MEStreamStarted = 202
    MESourceSeeked = 203
    MEStreamSeeked = 204
    MENewStream = 205
    MEUpdatedStream = 206
    MESourceStopped = 207
    MEStreamStopped = 208
    MESourcePaused = 209
    MEStreamPaused = 210
    MEEndOfPresentation = 211
    MEEndOfStream = 212
    MEMediaSample = 213
    MEStreamTick = 214
    MEStreamThinMode = 215
    MEStreamFormatChanged = 216
    MESourceRateChanged = 217
    MEEndOfPresentationSegment = 218
    MESourceCharacteristicsChanged = 219
    MESourceRateChangeRequested = 220
    MESourceMetadataChanged = 221

# For debugging reveived events
#DEBUG_EVENT_NAMES = {}
#for k, v in Event.__dict__.items():
#    if not k.startswith('_'):
#        DEBUG_EVENT_NAMES[v] = k

MF_TOPOSTATUS_READY = 100

MF_UNITS_PER_SEC = 10000000

# enum MFVideoAspectRatioMode
MFVideoARMode_None = 0
MFVideoARMode_PreservePicture = 0x1

DXVA2_ProcAmp_Brightness = 0x1
DXVA2_ProcAmp_Contrast = 0x2
DXVA2_ProcAmp_Hue = 0x4
DXVA2_ProcAmp_Saturation = 0x8

class PlayerException(Exception):
    pass

def _fourcc_to_str(four_cc):
    s = hex(int(four_cc))[2:]
    return ''.join([chr(int(s[i:i+2], 16)) for i in range(6, -2, -2)])

AUDIO_TYPES = {
    1:      'PCM',
    0x00FF: 'RAW AAC',
    0x1610: 'AAC',
    0x1600: 'ADTS',
    0x6C61: 'ALAC',
    0x0092: 'AC3 SPDIF',
    0xE06D802C: 'AC3',
    0x0009: 'DRM',
    0x0008: 'DTS',
    0xF1AC: 'FLAC',
    0x0003: 'IEEE FLOAT',
    0x0055: 'MP3',
    0x0050: 'MPEG',
    0x000A: 'MSP1',
    0x704F: 'OPUS',
    0x0164: 'WMA SPDIF',
    0x0163: 'WMA LOSSLESS',
    0x0161: 'WMA 2',
    0x0162: 'WMA 3',
}

# Media Foundation doesn't support MIDI. We use an additional DirectShow player
# that doesn't depend on external filters (the "engine_directshow" directory)
# to implement basic MIDI playback without SoundFont support.
# But in case "engine_directshow" exists, we do use it to play MIDI
# via SoundFont.
APP_DIR = os.path.join(os.path.dirname(__file__), '..')
DIRECTSHOW_PATH = os.path.join(APP_DIR, 'engine_directshow')
USE_BASS_MIDI = (
    os.path.isfile(os.path.join(DIRECTSHOW_PATH, 'BassAudioSource.ax')) and
    os.path.isfile(os.path.join(DIRECTSHOW_PATH, 'bass.dll')) and
    os.path.isfile(os.path.join(DIRECTSHOW_PATH, 'bassmidi.dll'))
)


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
        volume: float = .75,
    ):
        self._window = window
        self._volume = volume
        self._midi_player = None

        self._loop = False
        self._fullscreen = False

        self._frame_step = 0
        self._has_media = False
        self._has_video = False
        self._is_midi = False
        self._is_track_update = False
        self._scrub_pending = False
        self._scrub_state = SCRUB_NONE
        self._state = STATE_CLOSED

        _mf.Init(window.hwnd, window.hwnd)
        _mf.SetVolume(volume)

        ########################################
        #
        ########################################
        def _on_WM_APP_NOTIFY(hwnd, wparam, lparam):
            event_type, hr = wparam, lparam
#            print(DEBUG_EVENT_NAMES[event_type] if event_type in DEBUG_EVENT_NAMES else event_type, hr)

            if event_type == Event.MESessionTopologyStatus:
                if hr == MF_TOPOSTATUS_READY:

                    d = MFTIME()
                    _mf.GetDuration(byref(d))
                    self._duration = d.value

                    flag = BOOL()
                    _mf.HasVideo(byref(flag))
                    self._has_video = bool(flag.value)

                    if self._has_video:
                        fps = self._get_frame_rate()
                        if fps > 0:
                            self._frame_step = 1 / fps

                    if self._is_track_update:
                        self._is_track_update = False
                        if not self.is_playing():
                            _mf.Pause()
                            _mf.SetRate(1.0)
                    else:
                        self._has_media = True
                        _mf.Play()
                        self.on_parsed(True)

            elif event_type == Event.MESessionScrubSampleComplete:
                self._scrub_pending = False
                if self._scrub_state == SCRUB_CLOSING:
                    self._scrub_state == SCRUB_NONE

                    self._set_rate(1.0)

                    if self._state == STATE_PLAYING:
                        _mf.Play()

                    elif self.has_video():
                        ########################################
                        # We even start it if it was paused before to fix a bug in Media Foundations's
                        # EVR, otherwise it occasionally stops painting the video when paused.
                        ########################################
                        _mf.Play()
                        _mf.Pause()
                        time.sleep(.1)
                        _mf.SetVolume(self._volume)

            elif event_type == Event.MEEndOfPresentation:
                # The MEEndOfPresentation event signals that playback has reached the end of the file.
                # The Media Session automatically switches back to the stopped state.

                _mf.SetTime(0)
                if not self._loop:
                    _mf.Pause()
                    self._state = STATE_STOPPED

        self._window.register_message_callback(WM_APP_NOTIFY, _on_WM_APP_NOTIFY)

        ########################################
        #
        ########################################
        def _on_WM_PAINT(hwnd, wparam, lparam):
            if self._has_video:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, byref(ps))
                _mf.Repaint()
                user32.EndPaint(hwnd, byref(ps))

        self._window.register_message_callback(WM_PAINT, _on_WM_PAINT)

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            if self._has_video:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, byref(ps))
                _mf.ResizeVideo(width, height)
                _mf.Repaint()
                user32.EndPaint(hwnd, byref(ps))

        self._window.register_message_callback(WM_SIZE, _on_WM_SIZE)

    ########################################
    #
    ########################################
    def _redraw(self):
        user32.ShowWindow(self._window.hwnd, SW_INVALIDATE)
        user32.ShowWindow(self._window.hwnd, SW_SHOWNORMAL)

    ########################################
    #
    ########################################
    def _get_rate(self) -> float:
        f = FLOAT()
        hr = _mf.GetRate(byref(f))
        return f.value

    ########################################
    # We use this to switch from rate 0 to 1 and v.v., which requires paused state
    ########################################
    def _set_rate(self, rate: float):
        _mf.Pause()
        hr = _mf.SetRate(rate)

    ########################################
    #
    ########################################
    def has_media(self) -> bool:
        return self._has_media

    ########################################
    #
    ########################################
    def has_video(self) -> bool:
        return self._has_video

    ########################################
    #
    ########################################
    def has_audio(self) -> bool:
        flag = BOOL()
        hr = _mf.HasAudio(byref(flag))
        return flag.value

    ########################################
    #
    ########################################
    def is_midi(self) -> bool:
        return self._is_midi

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed) -> bool:
        self.close_file()

        ext = os.path.splitext(media_file)[1].lower()
        if ext in ('.mid', '.rmi', '.kar'):
            self._is_midi = True
            self._has_media = True
            if self._midi_player is None:
                import midi_player
                midi_player.USE_BASS_MIDI = USE_BASS_MIDI
                if USE_BASS_MIDI:
                    midi_player.init(DIRECTSHOW_PATH)
                self._midi_player = midi_player.Player(self._window, volume = self._volume)
                if self._loop:
                    self._midi_player.set_loop(True)
            else:
                self._midi_player.set_volume(self._volume)
            return self._midi_player.load_media_file(media_file, on_parsed)

        self.on_parsed = on_parsed
        return _mf.LoadFile(media_file) == 0

    ########################################
    #
    ########################################
    def close_file(self):
        if self._has_media:
            if self._is_midi:
                self._midi_player.close_file()
            else:
                hr = _mf.CloseFile()

            self._frame_step = 0
            self._has_media = False
            self._has_video = False
            self._is_midi = False
            self._is_track_update = False
            self._scrub_pending = False
            self._scrub_state = SCRUB_NONE
            self._state = STATE_CLOSED

    ########################################
    #
    ########################################
    def pause(self):
        if self._is_midi:
            return self._midi_player.pause()
        hr = _mf.Pause()
        if hr == 0:
            self._state = STATE_PAUSED

    ########################################
    #
    ########################################
    def play(self):
        if self._is_midi:
            return self._midi_player.play()
        hr = _mf.Play()
        if hr == 0:
            self._state = STATE_PLAYING

    ########################################
    #
    ########################################
    def stop(self):
        if self._is_midi:
            return self._midi_player.stop()
        _mf.SetTime(0)
        _mf.Stop()
        self._state = STATE_STOPPED

    ########################################
    # -1..1, 0=default
    ########################################
    def set_brightness(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Brightness, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_contrast(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Contrast, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_hue(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Hue, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_saturation(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Saturation, val)

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        self._loop = flag
        if self._midi_player:
            self._midi_player.set_loop(flag)

    ########################################
    #
    ########################################
    def is_fullscreen(self) -> bool:
        return self._fullscreen

    ########################################
    #
    ########################################
    def set_fullscreen(self, flag: bool):
        if self._fullscreen == flag:
            return
        if flag:
            self._rc_parent = RECT()
            user32.GetClientRect(self._window.hwnd, byref(self._rc_parent))
            rc = RECT()
            user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc))
            user32.SetParent(self._window.hwnd, 0)
            user32.SetWindowPos(self._window.hwnd, -1, 0, 0, rc.right, rc.bottom, 0)
        else:
            user32.SetParent(self._window.hwnd, self._window.parent_window.hwnd)
            user32.SetWindowPos(
                self._window.hwnd, 0,
                self._rc_parent.left,
                self._rc_parent.top,
                self._rc_parent.right - self._rc_parent.left,
                self._rc_parent.bottom - self._rc_parent.top,
                0
            )
            self._rc_parent = None
        self._redraw()
        self._fullscreen = flag

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        if self._is_midi:
            return self._midi_player.is_playing()
        return self._state == STATE_PLAYING

    ########################################
    #
    ########################################
    def skip_back(self, secs: float):
        if self._is_midi:
            return self._midi_player.skip_back(secs)
        self.set_time(max(0, self.get_time() - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs: float):
        if self._is_midi:
            return self._midi_player.skip_forward(secs)
        self.set_time(self.get_time() + secs)

    ########################################
    #
    ########################################
    def step_back(self, frames: int = 1):
        if self._is_midi:
            return
        if self._frame_step == 0:
            return
        self.set_time(max(0, self.get_time() - frames * self._frame_step))

    ########################################
    #
    ########################################
    def step_forward(self, frames: int = 1):
        if self._is_midi:
            return
        if self._frame_step == 0:
            return
        self.set_time(self.get_time() + frames * self._frame_step)

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        if self._is_midi:
            return self._midi_player.get_duration()
        d = MFTIME()
        if _mf.GetDuration(byref(d)) != 0:
            raise PlayerException()
        return d.value / MF_UNITS_PER_SEC

    ########################################
    #
    ########################################
    def _get_frame_rate(self) -> float:
        f = FLOAT()
        if _mf.GetFrameRate(byref(f)) != 0:
            raise PlayerException()
        return f.value

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        size = DWORD()
        if _mf.GetSize(byref(size)) != 0:
            raise PlayerException()
        return size.value & 0xFFFF, (size.value >> 16) & 0xFFFF

    ########################################
    #
    ########################################
    def get_audio_tracks(self) -> list:
        if self._is_midi:
            return [(1, 'MIDI', True)]
        cnt = DWORD()
        if _mf.GetStreamCount(byref(cnt)) != 0:
            raise PlayerException()
        stream_type = DWORD()
        four_cc = DWORD()
        selected = BOOL()
        streams = []
        lang = create_unicode_buffer(16)
        for i in range(cnt.value):
            _mf.GetStream(i, byref(stream_type), byref(four_cc), byref(selected), lang, 16)
            if stream_type.value == 1:
                name = 'Audio'
                if four_cc.value and four_cc.value in AUDIO_TYPES:
                    name += ' ' + AUDIO_TYPES[four_cc.value]
                if lang.value:
                    name += f' ({lang.value})'
                streams.append((i, name, selected.value))
        return streams

    ########################################
    #
    ########################################
    def get_video_tracks(self) -> list:
        cnt = DWORD()
        if _mf.GetStreamCount(byref(cnt)) != 0:
            raise PlayerException()
        stream_type = DWORD()
        four_cc = DWORD()
        selected = BOOL()
        streams = []
        lang = create_unicode_buffer(16)
        for i in range(cnt.value):
            _mf.GetStream(i, byref(stream_type), byref(four_cc), byref(selected), lang, 16)
            if stream_type.value == 0:
                name = 'Video'
                if four_cc.value:
                    name += ' ' + _fourcc_to_str(four_cc.value)
                if lang.value:
                    name += f' ({lang.value})'
                streams.append((i, name, selected.value))
        return streams

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        if self._is_midi:
            return self._midi_player.get_time()
        t = MFTIME()
        if _mf.GetTime(byref(t)) != 0:
            raise PlayerException()
        return t.value / MF_UNITS_PER_SEC

    ########################################
    #
    ########################################
    def set_time(self, secs: float):
        if self._is_midi:
            return self._midi_player.set_time(secs)

        if self._scrub_state == SCRUB_ACTIVE:
            if self._scrub_pending:
                ########################################
                # To keep things simple, instead of queuing we just ignore.
                ########################################
                return
            self._scrub_pending = True
            # Dont't allow to scrub beyond duration, otherwise it gets tricky
            hr = _mf.SetTime(int(min(secs * MF_UNITS_PER_SEC, self._duration - MF_UNITS_PER_SEC / 5)))

        else:
            hr = _mf.SetTime(int(secs * MF_UNITS_PER_SEC))

    ########################################
    #
    ########################################
    def scrub_start(self):
        if self._is_midi:
            return

        self._scrub_state = SCRUB_ACTIVE

        self._set_rate(0.0)

        if self._state != STATE_PLAYING and self.has_video():
            _mf.SetVolume(0)

    ########################################
    #
    ########################################
    def scrub_stop(self, secs: float = None):
        if self._is_midi:
            return

        self._scrub_state = SCRUB_CLOSING

        # Dont't allow to scrub beyond duration, otherwise it gets tricky
        hr = _mf.SetTime(int(min(secs * MF_UNITS_PER_SEC, self._duration - MF_UNITS_PER_SEC / 5)))

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id: int):
        self._is_track_update = True
        hr = _mf.SelectAudioStream(track_id)

    ########################################
    #
    ########################################
    def select_video_track(self, track_id: int):
        self._is_track_update = True
        hr = _mf.SelectVideoStream(track_id)

    ########################################
    # E.g. '4:3', '' to reset to default (DAR), None means stretch to window
    ########################################
    def set_aspect_ratio(self, ratio: str | None):
        if ratio is None:
            _mf.SetAspectRatioMode(MFVideoARMode_None)
        else:
            _mf.SetAspectRatioMode(MFVideoARMode_PreservePicture)
        if not self.is_playing():
            self._redraw()

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        v = max(0, min(1, v))
        self._volume = v
        _mf.SetVolume(v)
        if self._is_midi:
            self._midi_player.set_volume(v)

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str, callback):
        bih = BITMAPINFOHEADER()
        pDib = POINTER(BYTE)()
        cbDib = DWORD()
        ts = c_longlong()
        if _mf.GetCurrentImage(byref(bih), byref(pDib), byref(cbDib), byref(ts)) != 0:
            raise PlayerException()
        dib_size = cbDib.value
        dib = cast(pDib, POINTER(BYTE * dib_size))
        header = BMPHEADER(size=sizeof(BMPHEADER) + sizeof(BITMAPINFOHEADER) +  dib_size)
        with open(filename, 'wb') as f:
            f.write(bytes(header))
            f.write(bytes(bih))
            f.write(bytes(dib.contents))
        ole32.CoTaskMemFree(pDib)
        callback('BMP')
