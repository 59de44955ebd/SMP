import os
#from math import log
from dshow_interfaces import *
from winapp.const import WM_SIZE, WM_APP

FILTER_DIR = os.path.join(os.path.dirname(__file__), 'filters')

ADD_DIRECTVOBSUB = True
USE_LAV_DECODERS = True
USE_LOCAL_FILTERS = True
USE_MASTER_VOLUME = True

# If False, use VMR9 (Windowed) instead
USE_MPC_RENDERER = True

WM_EVENT_NOTIFY = WM_APP + 1

winmm = windll.Winmm

def SUCCEEDED(hr):
    return hr >= 0

def LOWORD(l):
    return WORD(l & 0xFFFF).value

def HIWORD(l):
    return WORD((l >> 16) & 0xFFFF).value

def DXVA2FloatToFixed(_float_):
    v = int(_float_ * 0x10000)
    return DXVA2_Fixed32(LOWORD(v), HIWORD(v))


########################################
#
########################################
class Player():

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window,
        volume = .75,

        width = 0, height = 0
    ):
        self._parent_window = parent_window
        self._width = width
        self._height = height
        self._loop = False

        self._keepaspectratio = True
        self._ratio = None

        self._frame_step = 0

        # Interfaces
        self._basic_audio = None
        self._basic_video = None
        self._direct_vob_sub = None
        self._filter_graph = None
        self._media_control = None
        self._media_event = None
        self._media_seeking = None
        self._mixer_control = None
        self._stream_select = None
        self._video_window = None
        self._vmr_aspect_control = None

        self._has_video = False
        self._has_audio = False
        self._is_midi = False

        self._fullscreen = False

        self.set_volume(volume)

        self._mixer_ranges = None

        self._mixer_items = {
            'Brightness': ProcAmp_Brightness,
            'Contrast': ProcAmp_Contrast,
            'Hue': ProcAmp_Hue,
            'Saturation': ProcAmp_Saturation
        }

        self._image_values = {
            'Brightness': 0,
            'Contrast': 0,
            'Hue': 0,
            'Saturation': 0
        }

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self._resize(width, height)

        parent_window.register_message_callback(WM_SIZE, _on_WM_SIZE)

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

    #            elif evt == EC_VIDEO_SIZE_CHANGED:
    #                print('EC_VIDEO_SIZE_CHANGED', self.get_size())

        parent_window.register_message_callback(WM_EVENT_NOTIFY, _on_WM_EVENT_NOTIFY)

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
        self._media_event.SetNotifyWindow(self._parent_window.hwnd, WM_EVENT_NOTIFY, 0)
        self._media_seeking = self._filter_graph.QueryInterface(IMediaSeeking)

        if self._has_video:
            self._basic_video = self._filter_graph.QueryInterface(IBasicVideo2)
            self._video_window = self._filter_graph.QueryInterface(IVideoWindow)

        if self._has_audio:
            self._basic_audio = self._filter_graph.QueryInterface(IBasicAudio)

    ########################################
    #
    ########################################
    def _reset(self):

        self._basic_audio = None
        self._basic_video = None
        self._direct_vob_sub = None
        self._media_control = None
        self._media_event = None
        self._media_seeking = None
        self._mixer_control = None
        self._stream_select = None
        self._vmr_aspect_control = None

        if self._video_window:
            # Reset the owner to NULL before releasing the Filter Graph Manager
#            self._video_window.Visible = False
            self._video_window.Owner = 0
            self._video_window.MessageDrain = 0
            self._video_window = None

        if self._filter_graph:
            enum = self._filter_graph.EnumFilters()
            while True:
                filt, fetched = enum.Next(1)
                if not fetched:
                    break
                self._filter_graph.RemoveFilter(filt)
                filt.Release()
                enum.Reset()

        self._filter_graph = None

        self._has_video = False
        self._has_audio = False
        self._is_midi = False

    ########################################
    #
    ########################################
    def _get_pin_by_name(self, filt, pin_name):
        enum = filt.EnumPins()
        while True:
            pin, fetched = enum.Next(1)
            if not fetched:
                break
            pinInfo = pin.QueryPinInfo()
            if pin_name in ''.join(map(chr, pinInfo.achName)):
                return pin

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
                    continue
                except:
                    return pin

    ########################################
    #
    ########################################
    def _build_graph_midi(self, src_file):
        file_source_async = CreateObject(CLSID_FileSourceAsync, interface = IBaseFilter)
        self._filter_graph.AddFilter(file_source_async, 'FileSourceAsync')
        file_source_async_src = file_source_async.QueryInterface(IFileSourceFilter)
        file_source_async_src.Load(src_file, None)

        midi_parser = CreateObject(CLSID_MIDIParser, interface = IBaseFilter)
        self._filter_graph.AddFilter(midi_parser, 'MIDIParser')

        midi_renderer = CreateObject(CLSID_MIDIRenderer, interface = IBaseFilter)
        self._filter_graph.AddFilter(midi_renderer, 'MIDIRenderer')

        pin_out_src = self._get_unconnected_pin(file_source_async, PINDIR_OUTPUT)
        pin_in_parser = self._get_unconnected_pin(midi_parser, PINDIR_INPUT)
        self._filter_graph.ConnectDirect(pin_out_src, pin_in_parser, None)

        pin_out_parser = self._get_unconnected_pin(midi_parser, PINDIR_OUTPUT)
        pin_in_renderer = self._get_unconnected_pin(midi_renderer, PINDIR_INPUT)
        self._filter_graph.ConnectDirect(pin_out_parser, pin_in_renderer, None)

        self._has_audio = True
        return True

    ########################################
    #
    ########################################
    def _build_graph(self, src_file):

        # Add LAV Splitter Source
        if USE_LOCAL_FILTERS:
            lav_splitter_source = self._create_object_from_path(CLSID_LAVSplitterSource, os.path.join(FILTER_DIR, 'LAVSplitter.ax'))
        else:
            lav_splitter_source = CreateObject(CLSID_LAVSplitterSource, interface = IBaseFilter)

        self._stream_select = lav_splitter_source.QueryInterface(IAMStreamSelect)

        self._filter_graph.AddFilter(lav_splitter_source, 'LAV Splitter Source')

        # Set source filename
        lav_splitter_source_src = lav_splitter_source.QueryInterface(IFileSourceFilter)
        try:
            lav_splitter_source_src.Load(src_file, None)
        except:
            return False

        # Default to 100 ms
        self._frame_step = 1000000

        try:
            pin_out_src_video = self._get_pin_by_name(lav_splitter_source, 'Video')
        except:
            pin_out_src_video = None

        try:
            pin_out_src_audio = self._get_pin_by_name(lav_splitter_source, 'Audio')
        except:
            pin_out_src_audio = None

        if pin_out_src_video is not None:
            # Add Video Decoder
            if USE_LAV_DECODERS:
                if USE_LOCAL_FILTERS:
                    video_decoder = self._create_object_from_path(CLSID_LAVVideoDecoder, os.path.join(FILTER_DIR, 'LAVVideo.ax'))
                else:
                    video_decoder = CreateObject(CLSID_LAVVideoDecoder, interface = IBaseFilter)
                self._filter_graph.AddFilter(video_decoder, 'LAV Video Decoder')
            else:
                video_decoder = CreateObject(CLSID_MsDTVDVDVideoDecoder, interface = IBaseFilter)
                self._filter_graph.AddFilter(video_decoder, 'MsDTVDVDVideoDecoder')

            # Add Video Renderer
            if USE_MPC_RENDERER:
                if USE_LOCAL_FILTERS:
                    video_mixing_renderer = self._create_object_from_path(CLSID_MPCVideoRenderer, os.path.join(FILTER_DIR, 'MpcVideoRenderer.ax'))
                else:
                    video_mixing_renderer = CreateObject(CLSID_MPCVideoRenderer, interface = IBaseFilter)
            else:
                video_mixing_renderer = CreateObject(CLSID_VideoMixingRenderer9, interface = IBaseFilter)

            if not USE_MPC_RENDERER:
                self._vmr_aspect_control = video_mixing_renderer.QueryInterface(IVMRAspectRatioControl9)

            self._filter_graph.AddFilter(
                video_mixing_renderer,
                'MPC Video Renderer' if USE_MPC_RENDERER else 'Video Mixing Renderer 9'
            )

            # Connect LAV Splitter Source and LAV Video Decoder
            pin_in_video_decoder = self._get_pin_by_name(video_decoder, 'In')
            self._filter_graph.ConnectDirect(pin_out_src_video, pin_in_video_decoder, None)

            if ADD_DIRECTVOBSUB and not src_file.startswith('https:') and not src_file.startswith('http:'):
                if USE_LOCAL_FILTERS:
                    direct_vob_sub = self._create_object_from_path(CLSID_VSFilter_autoload, os.path.join(FILTER_DIR, 'VSFilter.ax'))
                else:
                    direct_vob_sub = CreateObject(CLSID_VSFilter_autoload, interface = IBaseFilter)
                self._filter_graph.AddFilter(direct_vob_sub, 'DirectVobSub (Autoload)')

                pin_out_video_decoder = self._get_pin_by_name(video_decoder, 'Out')

                try:
                    # Connect Video Decoder and DirectVobSub
                    pin_in_directvobsub = self._get_pin_by_name(direct_vob_sub, 'Video')
                    self._filter_graph.ConnectDirect(pin_out_video_decoder, pin_in_directvobsub, None)

                except:
                    self._filter_graph.RemoveFilter(direct_vob_sub)

                    if USE_LOCAL_FILTERS:
                        direct_vob_sub = self._create_object_from_path(CLSID_VSFilter, os.path.join(FILTER_DIR, 'VSFilter.ax'))
                    else:
                        direct_vob_sub = CreateObject(CLSID_VSFilter, interface = IBaseFilter)
                    self._filter_graph.AddFilter(direct_vob_sub, 'DirectVobSub')

                    # Connect Video Decoder and DirectVobSub
                    pin_in_directvobsub = self._get_pin_by_name(direct_vob_sub, 'Video')
                    self._filter_graph.ConnectDirect(pin_out_video_decoder, pin_in_directvobsub, None)

                # Connect DirectVobSub and Video Mixing Renderer
                pin_out_directvobsub = self._get_pin_by_name(direct_vob_sub, 'Out')

                if USE_MPC_RENDERER:
                    pin_in_video_renderer = self._get_pin_by_name(video_mixing_renderer, 'In')
                else:
                    pin_in_video_renderer = self._get_pin_by_name(video_mixing_renderer, 'VMR Input0')

                self._filter_graph.ConnectDirect(pin_out_directvobsub, pin_in_video_renderer, None)

                self._direct_vob_sub = direct_vob_sub.QueryInterface(IDirectVobSub)
            else:
                # Connect LAV Video Decoder and Video Mixing Renderer
                pin_out_video_decoder = self._get_pin_by_name(video_decoder, 'Out')
                if USE_MPC_RENDERER:
                    pin_in_video_renderer = self._get_pin_by_name(video_mixing_renderer, 'In')
                else:
                    pin_in_video_renderer = self._get_pin_by_name(video_mixing_renderer, 'VMR Input0')
                self._filter_graph.ConnectDirect(pin_out_video_decoder, pin_in_video_renderer, None)

            # get framerate
            pmt = pin_out_src_video.ConnectionMediaType()
            formattype = str(pmt.formattype)
            if formattype == FORMAT_VideoInfo2 or formattype == FORMAT_MPEG2_VIDEO:
                vh = cast(pmt.pbFormat, POINTER(VIDEOINFOHEADER2))
                self._frame_step = vh.contents.AvgTimePerFrame

            elif formattype == FORMAT_VideoInfo or formattype == FORMAT_MPEGVideo:
                vh = cast(pmt.pbFormat, POINTER(VIDEOINFOHEADER))
                self._frame_step = vh.contents.AvgTimePerFrame

            if USE_MPC_RENDERER:
                serv = video_mixing_renderer.QueryInterface(IMFGetService)
                self._mixer_control = serv.GetService(GUID(CLSID_MR_VIDEO_MIXER_SERVICE), IMFVideoProcessor._iid_)
            else:
                self._mixer_control = video_mixing_renderer.QueryInterface(IVMRMixerControl9)

            pin_out_src_video.Release() # for some reason only the splitter pins have to be released explicitely!

            self._has_video = True

        if pin_out_src_audio is not None:
            # Add Audio Decoder
            if USE_LAV_DECODERS:
                if USE_LOCAL_FILTERS:
                    audio_decoder = self._create_object_from_path(CLSID_LAVAudioDecoder, os.path.join(FILTER_DIR, 'LAVAudio.ax'))
                else:
                    audio_decoder = CreateObject(CLSID_LAVAudioDecoder, interface = IBaseFilter)
                self._filter_graph.AddFilter(audio_decoder, 'LAV Audio Decoder')
            else:
                audio_decoder = CreateObject(CLSID_MsDTVDVDAudioDecoder, interface = IBaseFilter)
                self._filter_graph.AddFilter(audio_decoder, 'MsDTVDVDAudioDecoder')

            # Add DirectSound Audio Renderer
            directsound_audio_renderer = CreateObject(CLSID_DirectSoundAudioRenderer, interface = IBaseFilter)
            self._filter_graph.AddFilter(directsound_audio_renderer, 'DirectSound Audio Renderer')

            # Connect LAV Splitter Source and Audio Decoder
            pin_in_audio_decoder = self._get_pin_by_name(audio_decoder, 'Input' if USE_LAV_DECODERS else 'XForm In')
            self._filter_graph.ConnectDirect(pin_out_src_audio, pin_in_audio_decoder, None)

            # Connect Audio Decoder and DirectSound Audio Renderer
            pin_out_audio_decoder = self._get_pin_by_name(audio_decoder, 'Output' if USE_LAV_DECODERS else 'XFrom Out')
            pin_in_audio_renderer = self._get_pin_by_name(directsound_audio_renderer, 'Audio Input pin (rendered)')
            self._filter_graph.ConnectDirect(pin_out_audio_decoder, pin_in_audio_renderer, None)

            pin_out_src_audio.Release() # for some reason only the splitter pins have to be released explicitely!

            self._has_audio = True

        return True

    ########################################
    # VMR9ProcAmpControlRange m_VMR9ColorControl[4];
    ########################################
    def _get_mixer_ranges(self):
        if self._mixer_control is None:
            raise Exception('E_NOINTERFACE')
        self._mixer_ranges = {}
        if USE_MPC_RENDERER:
            for val_name, val_id in self._mixer_items.items():
                proc_amp_range = self._mixer_control.GetProcAmpRange(val_id)
                self._mixer_ranges[val_name] = {
                    'MinValue': proc_amp_range.MinValue.Value,
                    'MaxValue': proc_amp_range.MaxValue.Value,
                    'DefaultValue': proc_amp_range.DefaultValue.Value,
                }
        else:
            vmr9_amp_range = VMR9ProcAmpControlRange()
            for val_name, val_id in self._mixer_items.items():
                vmr9_amp_range.dwProperty = val_id
                try:
                    self._mixer_control.GetProcAmpControlRange(0, pointer(vmr9_amp_range))
                    self._mixer_ranges[val_name] = {
                        'MinValue': vmr9_amp_range.MinValue,
                        'MaxValue': vmr9_amp_range.MaxValue,
                        'DefaultValue': vmr9_amp_range.DefaultValue,
                    }
                except:
                    print('dshow._get_mixer_ranges failed')
                    pass

    ########################################
    # No direct return value!
    ########################################
    def load_media_file(self, media_file: str, on_parsed) -> bool:

        self.close_file()

        self._filter_graph = CreateObject(CLSID_FilterGraph, interface=IFilterGraph)

        ext = os.path.splitext(media_file)[1].lower()
        self._is_midi = ext in ('.mid', '.rmi')

        if self._is_midi:
            self._build_graph_midi(media_file)
            self._query_interfaces()

        else:
            if not self._build_graph(media_file):
                self._filter_graph = None
                return on_parsed(False)

            self._query_interfaces()

            if self._has_video:
                self._video_window.Owner = self._parent_window.hwnd
                if not USE_MPC_RENDERER:
                    self._video_window.WindowStyle = WS_CHILD | WS_CLIPCHILDREN | WS_CLIPSIBLINGS
                self._video_window.SetWindowPosition(0, 0, self._width, self._height)
                self._video_window.MessageDrain = self._parent_window.hwnd

                if USE_MPC_RENDERER:
                    w, h = self._basic_video.GetPreferredAspectRatio()
                    self._ratio_org = w / h

                    if not self._ratio and self._keepaspectratio:
                        self._ratio = self._ratio_org

                else:
                    if self._ratio:
                        self._set_keepaspectratio(False)

                self._resize(self._width, self._height)

                for k, value in self._image_values.items():
                    if value != 0:
                        self._adjust_image(k, value)

            if self._has_audio:
                self.set_volume(self._volume)

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
    def _resize(self, w, h):
        self._width, self._height = w, h
        if not self._has_video:
            return
        if self._ratio:
            if h > 0 and (w / h) > self._ratio:
                cy = h
                cx = int(h * self._ratio)
                x = (w - cx) // 2
                y = 0
            else:
                cx = w
                cy = int(w / self._ratio)
                x = 0
                y = (h - cy) // 2

            self._video_window.SetWindowPosition(0, 0, w, h)
            self._basic_video.SetDestinationPosition(x, y, cx, cy)
        else:
            self._video_window.SetWindowPosition(0, 0, w, h)
            self._basic_video.SetDestinationPosition(0, 0, w, h)

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
    def skip_back(self, secs):
        self.set_time(max(0, self.get_time() - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs):
        self.set_time(self.get_time() + secs)

    ########################################
    #
    ########################################
    def step_back(self, frames = 1):
        if self._media_seeking is None or self._frame_step == 0:
            return
        t = max(0, self._media_seeking.GetCurrentPosition() - frames * self._frame_step)
        self._media_seeking.SetPositions(
            t,
            AM_SEEKING_AbsolutePositioning,
            0,
            AM_SEEKING_NoPositioning
        )

    ########################################
    #
    ########################################
    def step_forward(self, frames = 1):
        if self._media_seeking is None or self._frame_step == 0:
            return
        self._media_seeking.SetPositions(
            self._media_seeking.GetCurrentPosition() + int(frames * self._frame_step),
            AM_SEEKING_AbsolutePositioning,
            0,
            AM_SEEKING_NoPositioning
        )

    ########################################
    # returns seconds as float
    ########################################
    def get_duration(self) -> float:
        if self._media_seeking is None:
            return 0
        try:
            return self._media_seeking.getDuration() / 10000000.0
        except:
            return 0

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        if not self._has_video: #self._basic_video is None:
            raise Exception('E_NOINTERFACE')
        return self._basic_video.GetVideoSize()

    ########################################
    #
    ########################################
#    def get_fps(self):
#        if self._has_video:
#            return 10000000 / self._frame_step if self._frame_step > 0 else 0
#        else:
#            return 0

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
        hr, stop_time = self._media_seeking.SetPositions(
            int(secs * 10000000),
            AM_SEEKING_AbsolutePositioning,
            0,
            AM_SEEKING_NoPositioning
        )
        return SUCCEEDED(hr)

    ########################################
    #
    ########################################
    def _reload_frame(self):
        if self._media_seeking is None:
            raise Exception('E_NOINTERFACE')
        self._media_seeking.SetPositions(
            self._media_seeking.GetCurrentPosition(),
            AM_SEEKING_AbsolutePositioning,
            0,
            AM_SEEKING_NoPositioning
        )

    ########################################
    # fail silently?
    ########################################
    def set_fullscreen(self, flag: bool):
        if self._fullscreen == flag:
            return
        if USE_MPC_RENDERER:
            if flag:
                self._rc_parent = RECT()
                user32.GetClientRect(self._parent_window.hwnd, byref(self._rc_parent))
                rc = RECT()
                user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc))
                user32.SetParent(self._parent_window.hwnd, 0)
                user32.SetWindowPos(self._parent_window.hwnd, -1, 0, 0, rc.right, rc.bottom, 0)
            else:
                user32.SetParent(self._parent_window.hwnd, self._parent_window.parent_window.hwnd)
                user32.SetWindowPos(
                    self._parent_window.hwnd, 0,
                    self._rc_parent.left,
                    self._rc_parent.top,
                    self._rc_parent.right - self._rc_parent.left,
                    self._rc_parent.bottom - self._rc_parent.top,
                    0
                )
                self._resize(self._rc_parent.right - self._rc_parent.left, self._rc_parent.bottom - self._rc_parent.top)
                self._rc_parent = None
        else:
            if self._video_window is None:
                raise Exception('E_NOINTERFACE')
            self._video_window.FullScreenMode = -1 if flag else 0
        self._fullscreen = flag

    ########################################
    #
    ########################################
    def is_fullscreen(self) -> bool:
#       if self._video_window is None:
#            raise Exception('E_NOINTERFACE')
#       return self._video_window.FullScreenMode == -1
       return self._fullscreen

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str, callback):
        if not self._has_video:
            return
        if self._basic_video is None:
            raise Exception('E_NOINTERFACE')
        LPLONG = POINTER(LONG)
        buf_size = LONG()
        self._basic_video.GetCurrentImage(byref(buf_size), None)
        buf = create_string_buffer(buf_size.value)
        self._basic_video.GetCurrentImage(byref(buf_size), cast(buf, LPLONG))
        dib = bytes(buf)
        bmph = cast(buf.raw, POINTER(BITMAPINFOHEADER))
        header = BMPHEADER(size=14 + len(dib))
        with open(filename, 'wb') as f:
            f.write(bytes(header))
            f.write(dib)
        callback('BMP')

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        if USE_MASTER_VOLUME or self._is_midi:
            d = DWORD()
            winmm.waveOutGetVolume(0, byref(d))
            self._volume = (d.value & 0xFFFF) / 0xFFFF
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        v = max(0, min(1, v))
        self._volume = v
        if USE_MASTER_VOLUME or self._is_midi:
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

    ########################################
    #
    ########################################
    def is_seekable(self) -> bool:
        return self._frame_step > 0

    ########################################
    #
    ########################################
    def load_sub_file(self, sub_file: str):
        try:
            self._direct_vob_sub.put_FileName(sub_file)
            return True
        except:
            return False

    ########################################
    #
    ########################################
    def get_sub_tracks(self):
        subs_tracks = []
        try:
            stream_select = self._direct_vob_sub.QueryInterface(IAMStreamSelect)
#            cnt = stream_select.Count()
            cnt = self._direct_vob_sub.get_LanguageCount()
            for i in range(1, cnt + 1):
                pmt, dwFlags, lcid, dwGroup, pszName, pObject, punk = stream_select.Info(i)
                subs_tracks.append([i, pszName, dwFlags > 0])
        except:
            pass
        return subs_tracks

    ########################################
    #
    ########################################
    def select_sub_track(self, track_id):
        if track_id == -1:
            self._direct_vob_sub.put_HideSubtitles(1)
        else:
            stream_select = self._direct_vob_sub.QueryInterface(IAMStreamSelect)
            stream_select.Enable(track_id, 1)

    ########################################
    #
    ########################################
    def hide_subtitles(self, flag: bool = True):
        self._direct_vob_sub.put_HideSubtitles(int(flag))

    ########################################
    # -1..1
    ########################################
    def set_brightness(self, value: float):
        self._adjust_image('Brightness', value)

    ########################################
    #
    ########################################
    def set_contrast(self, value: float):
        self._adjust_image('Contrast', value)

    ########################################
    #
    ########################################
    def set_hue(self, value: float):
        self._adjust_image('Hue', value)

    ########################################
    #
    ########################################
    def set_saturation(self, value: float):
        self._adjust_image('Saturation', value)

    ########################################
    #
    ########################################
    def _adjust_image(self, k, value):
        self._image_values[k] = value
        if self._filter_graph is None or self._mixer_control is None:
#            raise Exception('E_NOINTERFACE')
            return

        if self._mixer_ranges is None:
            self._get_mixer_ranges()

        if value < 0:
            value = self._mixer_ranges[k]['DefaultValue'] + value * (self._mixer_ranges[k]['DefaultValue'] - self._mixer_ranges[k]['MinValue'])
        else:
            value = self._mixer_ranges[k]['DefaultValue'] + value * (self._mixer_ranges[k]['MaxValue'] - self._mixer_ranges[k]['DefaultValue'])

        if USE_MPC_RENDERER:
            proc_amp_value = DXVA2_ProcAmpValues()
            setattr(proc_amp_value, k, DXVA2FloatToFixed(value))
            self._mixer_control.SetProcAmpValues(self._mixer_items[k], byref(proc_amp_value))
        else:
            vmr9_amp = VMR9ProcAmpControl()
            vmr9_amp.dwFlags = self._mixer_items[k]
            setattr(vmr9_amp, k, float(value))
            self._mixer_control.SetProcAmpControl(0, byref(vmr9_amp))  # pointer

        if not self.is_playing():
            self._reload_frame()

    ########################################
    #
    ########################################
    def _set_keepaspectratio(self, flag = True):
        self._keepaspectratio = flag

        if self._vmr_aspect_control:
            return SUCCEEDED(self._vmr_aspect_control.SetAspectRatioMode(
                VMR_ARMODE_LETTER_BOX if flag else VMR_ARMODE_NONE
            ))

    ########################################
    # e.g. '4:3', '' to reset to default, None means resize to window
    ########################################
    def set_aspect_ratio(self, ratio):
        if ratio:
            w, h = ratio.split(':')
            self._ratio = int(w) / int(h)
            if not USE_MPC_RENDERER:
                self._set_keepaspectratio(False)

        elif ratio == '':
            if USE_MPC_RENDERER:
                self._ratio = self._ratio_org
            else:
                self._ratio = None
            self._set_keepaspectratio(True)

        else:
            self._ratio = None
            self._set_keepaspectratio(False)

        self._resize(self._width, self._height)

    ########################################
    #
    ########################################
    def get_audio_tracks(self):
        audio_tracks = []
        if self._stream_select:
            cnt = self._stream_select.Count()
            for i in range(cnt):
                pmt, dwFlags, lcid, dwGroup, pszName, pObject, punk = self._stream_select.Info(i)
                if str(pmt.contents.majortype) == MEDIATYPE_Audio:
                    audio_tracks.append([i, pszName, dwFlags > 0])
        return audio_tracks

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id):
        if self._stream_select:
            self._stream_select.Enable(track_id, 1)

    ########################################
    #
    ########################################
    def get_video_tracks(self):
        video_tracks = []
        if self._stream_select:
            cnt = self._stream_select.Count()
            for i in range(cnt):
                pmt, dwFlags, lcid, dwGroup, pszName, pObject, punk = self._stream_select.Info(i)
                if str(pmt.contents.majortype) == MEDIATYPE_Video:
                    video_tracks.append([i, pszName, dwFlags > 0])
        return video_tracks

    ########################################
    #
    ########################################
    def select_video_track(self, track_id):
        if self._stream_select:
            self._stream_select.Enable(track_id, 1)
