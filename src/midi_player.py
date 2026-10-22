import os
from ctypes import *
from ctypes.wintypes import *

from const import RES_DIR

winmm = windll.Winmm

HSOUNDFONT = c_ulong
HSTREAM = c_ulong
HPLUGIN = c_ulong
QWORD = c_int64

BASS_UNICODE = -2147483648
BASS_POS_BYTE = 0

# BASS_ChannelIsActive return values
BASS_ACTIVE_STOPPED = 0
BASS_ACTIVE_PLAYING = 1
BASS_ACTIVE_STALLED = 2
BASS_ACTIVE_PAUSED = 3

BASS_SAMPLE_LOOP = 4

class BASS_MIDI_FONT(Structure):
	_fields_ = [('font', HSOUNDFONT),
				('preset', c_int), # preset number (-1=all)
				('bank', c_int)
				]

bass = CDLL(os.path.join(RES_DIR, 'bass.dll'))

#BOOL BASSDEF(BASS_Init)(int device, DWORD freq, DWORD flags, void *win, void *dsguid);
bass.BASS_Init.argtypes = (INT, DWORD, DWORD, LPVOID, LPVOID)

#HPLUGIN BASSDEF(BASS_PluginLoad)(const char *file, DWORD flags);
bass.BASS_PluginLoad.argtypes = (LPVOID, DWORD)

#BOOL BASSDEF(BASS_SetVolume)(float volume);
bass.BASS_SetVolume.argtypes = (FLOAT,)

#float BASSDEF(BASS_GetVolume)();
bass.BASS_GetVolume.restype = FLOAT

#QWORD BASSDEF(BASS_ChannelGetLength)(DWORD handle, DWORD mode);
bass.BASS_ChannelGetLength.argtypes = (DWORD, DWORD)
bass.BASS_ChannelGetLength.restype = QWORD

#QWORD BASSDEF(BASS_ChannelGetPosition)(DWORD handle, DWORD mode);
bass.BASS_ChannelGetPosition.argtypes = (DWORD, DWORD)
bass.BASS_ChannelGetPosition.restype = QWORD

#BOOL BASSDEF(BASS_ChannelSetPosition)(DWORD handle, QWORD pos, DWORD mode);
bass.BASS_ChannelSetPosition.argtypes = (DWORD, QWORD, DWORD)

#BOOL BASSDEF(BASS_ChannelPlay)(DWORD handle, BOOL restart);
bass.BASS_ChannelPlay.argtypes = (DWORD, BOOL)

#BOOL BASSDEF(BASS_ChannelStop)(DWORD handle);
bass.BASS_ChannelStop.argtypes = (DWORD,)

#BOOL BASSDEF(BASS_ChannelPause)(DWORD handle);
bass.BASS_ChannelPause.argtypes = (DWORD,)

#DWORD BASS_ChannelIsActive(DWORD handle);
bass.BASS_ChannelIsActive.argtypes = (DWORD,)

#BOOL BASSDEF(BASS_StreamFree)(HSTREAM handle);
bass.BASS_StreamFree.argtypes = (HSTREAM,)

#double BASS_ChannelBytes2Seconds(DWORD handle, QWORD pos);
bass.BASS_ChannelBytes2Seconds.argtypes = (DWORD, QWORD)
bass.BASS_ChannelBytes2Seconds.restype = DOUBLE

#QWORD BASS_ChannelSeconds2Bytes(DWORD handle, double pos);
bass.BASS_ChannelSeconds2Bytes.argtypes = (DWORD, DOUBLE)
bass.BASS_ChannelSeconds2Bytes.restype = QWORD

#DWORD BASS_ChannelFlags(DWORD handle, DWORD flags, DWORD mask);
bass.BASS_ChannelFlags.argtypes = (DWORD, DWORD, DWORD)

bassmidi_dll = os.path.join(RES_DIR, 'bassmidi.dll')
bassmidi = CDLL(bassmidi_dll)

#HSTREAM BASSMIDIDEF(BASS_MIDI_StreamCreateFile)(BOOL mem, const void *file, QWORD offset, QWORD length, DWORD flags, DWORD freq);
bassmidi.BASS_MIDI_StreamCreateFile.argtypes = (BOOL, LPVOID, QWORD, QWORD, DWORD, DWORD)
bassmidi.BASS_MIDI_StreamCreateFile.restype = HSTREAM

#HSOUNDFONT BASSMIDIDEF(BASS_MIDI_FontInit)(const void *file, DWORD flags);
bassmidi.BASS_MIDI_FontInit.argtypes = (LPVOID, DWORD)
bassmidi.BASS_MIDI_FontInit.restype = HSOUNDFONT

#BOOL BASSMIDIDEF(BASS_MIDI_StreamSetFonts)(HSTREAM handle, const BASS_MIDI_FONT *fonts, DWORD count);
bassmidi.BASS_MIDI_StreamSetFonts.argtypes = (HSTREAM, LPVOID, DWORD)
bassmidi.BASS_MIDI_StreamSetFonts.restype = BOOL

bass.BASS_PluginLoad(bassmidi_dll, BASS_UNICODE)


########################################
#
########################################
class MidiPlayer():

    ########################################
    #
    ########################################
    def __init__(self, volume: float = .75):
        self._loop = False
        self._hstream = None

        bass.BASS_Init(-1, 44100, 0, 0, 0)
        self.set_volume(volume)

        self._hsoundfont = bassmidi.BASS_MIDI_FontInit(os.path.join(RES_DIR, 'soundbank.sf2'), BASS_UNICODE)

    ########################################
    #
    ########################################
    def has_audio(self) -> bool:
        return self._hstream is None

    ########################################
    #
    ########################################
    def has_video(self) -> bool:
        return False

    ########################################
    #
    ########################################
    def is_fullscreen(self):
        return False

    ########################################
    #
    ########################################
    def get_audio_tracks(self) -> list:
        return [(1, 'MIDI', True)] if self._hstream else []

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed) -> bool:
        self.close_file()

        hstream = bassmidi.BASS_MIDI_StreamCreateFile(0, media_file, 0, 0, BASS_UNICODE, 44100)
        if hstream:
            self._hstream = hstream
            self._is_midi = True

            soundfont = BASS_MIDI_FONT(self._hsoundfont, -1, 0)
            ok = bassmidi.BASS_MIDI_StreamSetFonts(self._hstream, byref(soundfont), 1)

            if self._loop:
                bass.BASS_ChannelFlags(self._hstream, BASS_SAMPLE_LOOP, BASS_SAMPLE_LOOP)

            on_parsed(True)
        else:
            on_parsed(False)

    ########################################
    #
    ########################################
    def close_file(self):
        if self._hstream is not None:
            bass.BASS_ChannelStop(self._hstream)
            bass.BASS_StreamFree(self._hstream)
            self._hstream = None

    ########################################
    #
    ########################################
    def pause(self):
        if self._hstream is None:
            raise Exception('E_NOINTERFACE')

        ok = bass.BASS_ChannelPause(self._hstream)

    ########################################
    #
    ########################################
    def play(self):
        if self._hstream is None:
            raise Exception('E_NOINTERFACE')

        ok = bass.BASS_ChannelPlay(self._hstream, 0)

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        if self._hstream is None:
            return False

        return bass.BASS_ChannelIsActive(self._hstream) == BASS_ACTIVE_PLAYING

    ########################################
    #
    ########################################
    def stop(self):
        if self._hstream is None:
            #raise Exception('E_NOINTERFACE')
            return

        ok = bass.BASS_ChannelStop(self._hstream)
        self.set_time(0)

    ########################################
    #
    ########################################
    def skip_back(self, secs: float):
        self.set_time(max(0, self.get_time() - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs: float):
        self.set_time(self.get_time() + secs)

    ########################################
    #
    ########################################
    def step_back(self, frames: int = 1):
        pass

    ########################################
    #
    ########################################
    def step_forward(self, frames: int = 1):
        pass

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        if self._hstream is None:
            raise Exception('E_NOINTERFACE')

        total = bass.BASS_ChannelGetLength(self._hstream, BASS_POS_BYTE)
        return bass.BASS_ChannelBytes2Seconds(self._hstream, total)

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        if self._hstream is None:
            raise Exception('E_NOINTERFACE')

        pos = bass.BASS_ChannelGetPosition(self._hstream, BASS_POS_BYTE)
        return bass.BASS_ChannelBytes2Seconds(self._hstream, pos)

    ########################################
    #
    ########################################
    def set_time(self, secs: float):
        if self._hstream is None:
            raise Exception('E_NOINTERFACE')

        pos = bass.BASS_ChannelSeconds2Bytes(self._hstream, secs)
        ok = bass.BASS_ChannelSetPosition(self._hstream, pos, BASS_POS_BYTE)

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        self._volume = v
        v = int(0xFFFF * v)
        winmm.waveOutSetVolume(0, v | v << 16)

    ########################################
    #
    ########################################
    def set_loop(self, loop: bool):
        self._loop = loop
        if self._hstream:
            bass.BASS_ChannelFlags(self._hstream, BASS_SAMPLE_LOOP if loop else 0, BASS_SAMPLE_LOOP)
