import os

from dshow_interfaces import *
from winapp.const import WM_APP

from const import RES_DIR

USE_LOCAL_FILTERS = True
USE_MASTER_VOLUME = False
USE_BASS_MIDI = True

if USE_MASTER_VOLUME or not USE_BASS_MIDI:
    winmm = windll.Winmm
else:
    from math import log

WM_EVENT_NOTIFY = WM_APP + 1

FILTER_DIR = None

def init(filter_dir):
    global FILTER_DIR
    FILTER_DIR = filter_dir


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
        self._loop = False

        # Interfaces
        self._basic_audio = None
        self._filter_graph = None
        self._media_control = None
        self._media_event = None
        self._media_seeking = None

        self._has_audio = False
        self._is_midi = False
        self._duration = 0

        self.set_volume(volume)

        ########################################
        #
        ########################################
        def _on_WM_EVENT_NOTIFY(hwnd, wparam, lparam):
            while True:
                try:
                    # returns (EventCode, Param1, Param2)
                    evt = self._media_event.getEvent(0)[0]
                except:
                    break
                if evt == EC_COMPLETE:
                    if self._loop:
                        self.set_time(0)
                    else:
                        self.pause()
                        self.set_time(0)

        window.register_message_callback(WM_EVENT_NOTIFY, _on_WM_EVENT_NOTIFY)

    ########################################
    #
    ########################################
    def has_video(self) -> bool:
        return False

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
    def _create_object_from_path(self, clsid, dll_filename, interface = IBaseFilter):
        clsid_class = GUID(clsid)  # bytes(GUID(clsid))
        iclassfactory = GUID(IClassFactory._iid_)
        my_dll = oledll.LoadLibrary(dll_filename)
        factory_ptr = c_void_p(0)
        hr = my_dll.DllGetClassObject(clsid_class, iclassfactory, byref(factory_ptr))
        ptr_icf = POINTER(IClassFactory)(factory_ptr.value)
        pUnk = ptr_icf.CreateInstance()
        return pUnk.QueryInterface(interface)

    ########################################
    #
    ########################################
    def _query_interfaces(self):
        self._media_control = self._filter_graph.QueryInterface(IMediaControl)
        self._media_event = self._filter_graph.QueryInterface(IMediaEventEx)
        self._media_event.SetNotifyWindow(self._window.hwnd, WM_EVENT_NOTIFY, 0)
        self._media_seeking = self._filter_graph.QueryInterface(IMediaSeeking)
        if self._has_audio:
            self._basic_audio = self._filter_graph.QueryInterface(IBasicAudio)

    ########################################
    #
    ########################################
    def _reset(self):
        self._basic_audio = None
        self._media_control = None
        self._media_event = None
        self._media_seeking = None

        if self._filter_graph:
            enum = self._filter_graph.EnumFilters()
            while True:
                filt, fetched = enum.Next(1)
                if not fetched:
                    break
                self._filter_graph.RemoveFilter(filt)
                enum.Reset()
            self._filter_graph = None

        self._has_audio = False
        self._is_midi = False
        self._duration = 0

    ########################################
    #
    ########################################
    def _get_unconnected_pin(self, filt, direction):
        enum = filt.EnumPins()
        while True:
            pin, fetched = enum.Next(1)
            if not fetched:
                break
            d = pin.QueryDirection()
            if d == direction:
                try:
                    tmp = pin.ConnectedTo()
                    # Already connected - not the pin we want
                    pin.Release()
                    continue
                except:
                    return pin

    ########################################
    #
    ########################################
    def _build_graph_midi(self, src_file):
        if USE_BASS_MIDI:
            if USE_LOCAL_FILTERS:
                bass_audio_source = self._create_object_from_path(CLSID_BassAudioSource, os.path.join(FILTER_DIR, 'BassAudioSource.ax'))
            else:
                bass_audio_source = CreateObject(CLSID_BassAudioSource, interface = IBaseFilter)
            self._filter_graph.AddFilter(bass_audio_source, 'Base Audio Source')
            bass_audio_source.QueryInterface(IBassSource2).SetSoundfont(os.path.join(RES_DIR, 'soundbank.sf2'))
            bass_audio_source.QueryInterface(IFileSourceFilter).Load(src_file, None)

            # Add DirectSound Audio Renderer
            directsound_audio_renderer = CreateObject(CLSID_DirectSoundAudioRenderer, interface = IBaseFilter)
            self._filter_graph.AddFilter(directsound_audio_renderer, 'DirectSound Audio Renderer')

            # Connect Audio Decoder and DirectSound Audio Renderer
            self._filter_graph.ConnectDirect(
                self._get_unconnected_pin(bass_audio_source, PINDIR_OUTPUT),
                self._get_unconnected_pin(directsound_audio_renderer, PINDIR_INPUT),
                None
            )
        else:
            file_source_async = CreateObject(CLSID_FileSourceAsync, interface = IBaseFilter)
            self._filter_graph.AddFilter(file_source_async, 'FileSourceAsync')
            file_source_async.QueryInterface(IFileSourceFilter).Load(src_file, None)

            midi_parser = CreateObject(CLSID_MIDIParser, interface = IBaseFilter)
            self._filter_graph.AddFilter(midi_parser, 'MIDIParser')

            midi_renderer = CreateObject(CLSID_MIDIRenderer, interface = IBaseFilter)
            self._filter_graph.AddFilter(midi_renderer, 'MIDIRenderer')

            self._filter_graph.ConnectDirect(
                self._get_unconnected_pin(file_source_async, PINDIR_OUTPUT),
                self._get_unconnected_pin(midi_parser, PINDIR_INPUT),
                None
            )

            self._filter_graph.ConnectDirect(
                self._get_unconnected_pin(midi_parser, PINDIR_OUTPUT),
                self._get_unconnected_pin(midi_renderer, PINDIR_INPUT),
                None
            )

        self._has_audio = True
        return True

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str, on_parsed) -> bool:
        self.close_file()

        self._filter_graph = CreateObject(CLSID_FilterGraph, interface=IFilterGraph)
        self._is_midi = True
        self._build_graph_midi(media_file)
        self._query_interfaces()

        self.set_volume(self._volume)

        if self._media_seeking:
            try:
                self._duration = self._media_seeking.getDuration()
            except:
                pass

        on_parsed(True)

    ########################################
    #
    ########################################
    def close_file(self):
        if self._media_control is not None:
            self._media_control.Stop()
        self._reset()

    ########################################
    #
    ########################################
    def pause(self):
        if self._media_control is None:
            raise Exception('E_NOINTERFACE')
        self._media_control.Pause()

    ########################################
    #
    ########################################
    def play(self):
        if self._media_control is None:
            raise Exception('E_NOINTERFACE')
        self._media_control.Run()

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        if self._media_control is None:
            return False
        return self._media_control.getState(10000) == State_Running

    ########################################
    #
    ########################################
    def stop(self):
        if self._media_control is None:
            return False
        #self._media_control.Stop()
        self._media_control.Pause()
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
        t = self.get_time() + secs
        if self._duration:
            t = min(self._duration / 10000000.0, t)
        self.set_time(t)

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
        return self._duration / 10000000.0

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        if self._media_seeking is None:
            raise Exception('E_NOINTERFACE')
        return self._media_seeking.GetCurrentPosition() / 10000000.0

    ########################################
    #
    ########################################
    def set_time(self, secs: float):
        if self._media_seeking is None:
            raise Exception('E_NOINTERFACE')
        self._media_seeking.SetPositions(
            int(secs * 10000000), AM_SEEKING_AbsolutePositioning,
            0,AM_SEEKING_NoPositioning
        )

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
        if USE_MASTER_VOLUME or (self._is_midi and not USE_BASS_MIDI):
            v = int(0xFFFF * v)
            winmm.waveOutSetVolume(0, v | v << 16)
        else:
            if self._has_audio:
                # 0..1 => -10000..0
                if self._volume == 0:
                    self._basic_audio.Volume = -10000
                else:
                    self._basic_audio.Volume = int(1442.6950 * log(v))

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        self._loop = flag
