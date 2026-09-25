import os
import sys

from ctypes import *
from ctypes.wintypes import *

from winapp.comtypes import *
from winapp.comtypes.automation import VARIANT, IDispatch
from winapp.comtypes.persist import IPropertyBag, IErrorLog
from winapp.comtypes.hresult import *

from winapp.const import WS_CHILD, WS_CLIPSIBLINGS, WS_CLIPCHILDREN
from winapp.dlls import user32
from winapp.types import LONG_PTR, ULONG_PTR

########################################
# CONSTANTS
########################################

# values for enumeration 'AM_SEEKING_SeekingFlags'
AM_SEEKING_NoPositioning = 0
AM_SEEKING_AbsolutePositioning = 1
AM_SEEKING_RelativePositioning = 2
AM_SEEKING_IncrementalPositioning = 3
AM_SEEKING_PositioningBitsMask = 3
AM_SEEKING_SeekToKeyFrame = 4
AM_SEEKING_ReturnTime = 8
AM_SEEKING_Segment = 16
AM_SEEKING_NoFlush = 32
AM_SEEKING_SeekingFlags = c_int # enum

# values for enumeration '_FilterState'
State_Stopped = 0
State_Paused = 1
State_Running = 2
_FilterState = c_int # enum

# values for enumeration '_PinDirection'
PINDIR_INPUT = 0
PINDIR_OUTPUT = 1
_PinDirection = c_int # enum

FORMAT_VideoInfo = '{05589f80-c356-11ce-bf01-00aa0055595a}'
FORMAT_VideoInfo2 = '{F72A76A0-EB0A-11d0-ACE4-0000C0CC16BA}'
FORMAT_MPEGVideo = '{05589f82-c356-11ce-bf01-00aa0055595a}'
FORMAT_MPEG2_VIDEO = '{E06D80E3-DB46-11CF-B4D1-00805F6CBBEA}'

MEDIATYPE_Video = '{73646976-0000-0010-8000-00AA00389B71}'
MEDIATYPE_Audio = '{73647561-0000-0010-8000-00AA00389B71}'

# VMR9
VMR9Mode_Windowed = 0x1
VMR9Mode_Windowless = 0x2

# values for enumeration _VMR_ASPECT_RATIO_MODE
VMR_ARMODE_NONE = 0
VMR_ARMODE_LETTER_BOX = 1
_VMR_ASPECT_RATIO_MODE = DWORD

ProcAmp_Brightness = 0x1
ProcAmp_Contrast = 0x2
ProcAmp_Hue = 0x4
ProcAmp_Saturation = 0x8

# Windows
CLSID_DirectSoundAudioRenderer  = '{79376820-07D0-11CF-A24D-0020AFD79767}'
CLSID_FileSourceAsync		    = '{E436EBB5-524F-11CE-9F53-0020AF0BA770}'
CLSID_FilterGraph			    = '{E436EBB3-524F-11CE-9F53-0020AF0BA770}'
CLSID_MIDIParser			    = '{D51BD5A2-7548-11CF-A520-0080C77EF58A}'
CLSID_MIDIRenderer			    = '{07B65360-C445-11CE-AFDE-00AA006C14F4}'
CLSID_MsDTVDVDAudioDecoder	    = '{E1F1A0B8-BEEE-490D-BA7C-066C40B5E2B9}'
CLSID_MsDTVDVDVideoDecoder	    = '{212690FB-83E5-4526-8FD7-74478B7939CD}'
CLSID_VideoMixingRenderer9	    = '{51B4ABF3-748F-4E3B-A276-C828330E926A}'
CLSID_MR_VIDEO_MIXER_SERVICE    = '{073cd2fc-6cf4-40b7-8859-e89552c841f8}'

# LAV filters
CLSID_LAVSplitterSource		    = '{B98D13E7-55DB-4385-A33D-09FD1BA26338}'
CLSID_LAVSplitter		        = '{171252A0-8820-4AFE-9DF8-5C92B2D66B04}'
CLSID_LAVVideoDecoder		    = '{EE30215D-164F-4A92-A4EB-9D4C13390F9F}'
CLSID_LAVAudioDecoder		    = '{E8E73B6B-4CB3-44A4-BE99-4F7BCB96E491}'

# VSFilter/DirectVobSub/DirectVobSubXy
CLSID_VSFilter				    = '{93A22E7A-5091-45EF-BA61-6DA26156A5D0}'
CLSID_VSFilter_autoload		    = '{9852A670-F845-491B-9BE6-EBD841B8A613}'

# MPC Video Renderer
CLSID_MPCVideoRenderer	        = '{71F080AA-8661-4093-B15E-4F6903E77D0A}'

# Bass Audio Source
CLSID_BassAudioSource           = '{A351970E-4601-4BEC-93DE-CEE7AF64C636}'

CLSID_MIDIParser			    = '{D51BD5A2-7548-11CF-A520-0080C77EF58A}'
CLSID_MIDIRenderer			    = '{07B65360-C445-11CE-AFDE-00AA006C14F4}'

# IMediaEvent constants
#EC_ACTIVATE = 19
#EC_BUFFERING_DATA = 17
#EC_BUILT = 768
#EC_CLOCK_CHANGED = 13
#EC_CLOCK_UNSET = 81
#EC_CODECAPI_EVENT = 87
EC_COMPLETE = 1
#EC_DEVICE_LOST = 31
#EC_DISPLAY_CHANGED = 22
#EC_END_OF_SEGMENT = 28
#EC_ERRORABORT = 3
#EC_ERROR_STILLPLAYING = 8
#EC_EXTDEVICE_MODE_CHANGE = 49
#EC_FULLSCREEN_LOST = 18
#EC_GRAPH_CHANGED = 80
#EC_LENGTH_CHANGED = 30
#EC_NEED_RESTART = 20
#EC_NOTIFY_WINDOW = 25
#EC_OLE_EVENT = 24
#EC_OPENING_FILE = 16
#EC_PALETTE_CHANGED = 9
#EC_PAUSED = 14
#EC_PREPROCESS_COMPLETE = 86
#EC_QUALITY_CHANGE = 11
#EC_REPAINT = 5
#EC_SEGMENT_STARTED = 29
#EC_SHUTTING_DOWN = 12
#EC_SNDDEV_IN_ERROR = 512
#EC_SNDDEV_OUT_ERROR = 513
#EC_STARVATION = 23
#EC_STATE_CHANGE = 50
#EC_STEP_COMPLETE = 36
#EC_STREAM_CONTROL_STARTED = 27
#EC_STREAM_CONTROL_STOPPED = 26
#EC_STREAM_ERROR_STILLPLAYING = 7
#EC_STREAM_ERROR_STOPPED = 6
#EC_SYSTEMBASE = 0
#EC_TIME = 4
#EC_TIMECODE_AVAILABLE = 48
#EC_UNBUILT = 769
#EC_USER = 32768
#EC_USERABORT = 2
#EC_VIDEO_SIZE_CHANGED = 10
#EC_VMR_RECONNECTION_FAILED = 85
#EC_VMR_RENDERDEVICE_SET = 83
#EC_VMR_SURFACE_FLIPPED = 84
#EC_WINDOW_DESTROYED = 21
#EC_WMT_EVENT = 594
#EC_WMT_INDEX_EVENT = 593

########################################
# INTERFACE DECLARATIONS
########################################

class IMediaFilter(IPersist):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86899-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IPersistStream(IPersist):
    _case_insensitive_ = True
    _iid_ = GUID('{00000109-0000-0000-C000-000000000046}')
    _idlflags_ = []

class IAMStreamConfig(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{C6E13340-30AC-11D0-A18C-00A0C9118956}')
    _idlflags_ = []

class IAMStreamSelect(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{C1960960-17F5-11D1-ABE1-00A0C905F375}')
    _idlflags_ = []

class IBaseFilter(IMediaFilter):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86895-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IBasicAudio(IDispatch):
    _case_insensitive_ = True
    'IBasicAudio interface'
    _iid_ = GUID('{56A868B3-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IBasicVideo(IDispatch):
    _case_insensitive_ = True
    'IBasicVideo interface'
    _iid_ = GUID('{56A868B5-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IBasicVideo2(IBasicVideo):
    _case_insensitive_ = True
    'IBasicVideo2'
    _iid_ = GUID('{329BB360-F6EA-11D1-9038-00A0C9697298}')
    _idlflags_ = []

class IBindCtx(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{0000000E-0000-0000-C000-000000000046}')
    _idlflags_ = []

#class ID3DFullscreenControl(IUnknown):
#	_case_insensitive_ = True
#	_iid_ = GUID('{8EA1E899-B77D-4777-9F0E-66421BEA50F8}')
#	_idlflags_ = []

class IDirectVobSub(IUnknown):
	_case_insensitive_ = True
	_iid_ = GUID('{EBE1FB08-3957-47CA-AF13-5827E5442E56}')
	_idlflags_ = []

class IEnumFilters(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86893-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError(index)

class IEnumPins(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86892-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError(index)

class IEnumMediaTypes(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{89C31040-846B-11CE-97D3-00AA0055595A}')
    _idlflags_ = []
    def __iter__(self):
        return self

    def next(self):
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise StopIteration

    def __getitem__(self, index):
        self.Reset()
        self.Skip(index)
        item, fetched = self.Next(1)
        if fetched:
            return item
        raise IndexError(index)

class IEnumMoniker(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{00000102-0000-0000-C000-000000000046}')
    _idlflags_ = []

class IEnumString(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{00000101-0000-0000-C000-000000000046}')
    _idlflags_ = []

class IFileSourceFilter(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A868A6-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IFilterGraph(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A8689F-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IMediaControl(IDispatch):
    _case_insensitive_ = True
    'IMediaControl interface'
    _iid_ = GUID('{56A868B1-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IMediaEvent(IDispatch):
    _case_insensitive_ = True
    'IMediaEvent interface'
    _iid_ = GUID('{56A868B6-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IMediaEventEx(IMediaEvent):
    _case_insensitive_ = True
    'IMediaEventEx interface'
    _iid_ = GUID('{56A868C0-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IMediaSeeking(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{36B73880-C2C8-11CF-8B46-00805F6CEF60}')
    _idlflags_ = []

class IMediaEventSink(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A868A2-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IMoniker(IPersistStream):
    _case_insensitive_ = True
    _iid_ = GUID('{0000000F-0000-0000-C000-000000000046}')
    _idlflags_ = []

class IPin(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86891-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IPinInfo(IDispatch):
    _case_insensitive_ = True
    'Pin Info'
    _iid_ = GUID('{56A868BD-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IRunningObjectTable(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{00000010-0000-0000-C000-000000000046}')
    _idlflags_ = []

class IReferenceClock(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{56A86897-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = []

class IVideoWindow(IDispatch):
    _case_insensitive_ = True
    'IVideoWindow interface'
    _iid_ = GUID('{56A868B4-0AD4-11CE-B03A-0020AF0BA770}')
    _idlflags_ = ['dual', 'oleautomation']

class IVMRAspectRatioControl(IUnknown):
    _case_insensitive_ = True
    'IVMRAspectRatioControl Interface'
    _iid_ = GUID('{EDE80B5C-BAD6-4623-B537-65586C9F8DFD}')
    _idlflags_ = []

class IVMRAspectRatioControl9(IUnknown):
	_case_insensitive_ = True
	_iid_ = GUID('{00D96C29-BBDE-4EFC-9901-BB5036392146}')
	_idlflags_ = []

class IVMRFilterConfig(IUnknown):
    _case_insensitive_ = True
    'IVMRFilterConfig Interface'
    _iid_ = GUID('{9E5530C5-7034-48B4-BB46-0B8A6EFC8E36}')
    _idlflags_ = []

class IVMRFilterConfig9(IUnknown):
	_case_insensitive_ = False
	_iid_ = GUID('{5a804648-4f66-4867-9c43-4f5c822cf1b8}')
	_idlflags_ = []

class IVMRImageCompositor(IUnknown):
    _case_insensitive_ = True
    'IVMRImageCompositor Interface'
    _iid_ = GUID('{7A4FB5AF-479F-4074-BB40-CE6722E43C82}')
    _idlflags_ = []

class IVMRMixerControl9(IUnknown):
	_case_insensitive_ = True
	_iid_ = GUID('{1A777EAA-47C8-4930-B2C9-8FEE1C1B0F3B}')
	_idlflags_ = []

class IVMRWindowlessControl9(IUnknown):
	_case_insensitive_ = False
	_iid_ = GUID('{8f537d09-f85e-4414-b23b-502e54c79927}')
	_idlflags_ = []

########################################
# STRUCTS
########################################
REFERENCE_TIME = c_longlong

class _AMMediaType(Structure):
    _fields_ = [
        ('majortype', GUID),
        ('subtype', GUID),
        ('bFixedSizeSamples', c_int),
        ('bTemporalCompression', c_int),
        ('lSampleSize', c_ulong),
        ('formattype', GUID),
        ('punk', POINTER(IUnknown)),
        ('cbFormat', c_ulong),
        ('pbFormat', POINTER(c_ubyte)),
    ]

class BITMAPINFOHEADER(Structure):
    _fields_ = [
            ('biSize', DWORD),
            ('biWidth', LONG),
            ('biHeight', LONG),
            ('biPlanes', WORD),
            ('biBitCount', WORD),
            ('biCompression', DWORD),
            ('biSizeImage', DWORD),
            ('biXPelsPerMeter', LONG),
            ('biYPelsPerMeter', LONG),
            ('biClrUsed', DWORD),
            ('biClrImportant', DWORD)
    ]

# Custom struct for writing BMP files
class BMPHEADER(Structure):
    _pack_ = 2
    _fields_ = [
        ('magic', SHORT),
        ('size', DWORD),
        ('reserved', DWORD),
        ('offset', DWORD),
    ]
    def __init__(self, *args, **kwargs):
        super(BMPHEADER, self).__init__(*args, **kwargs)
        self.magic = 0x4D42  # BM
        self.offset = sizeof(self) + sizeof(BITMAPINFOHEADER)

class _FilterInfo(Structure):
    _fields_ = [
        ('achName', c_ushort * 128),
        ('pGraph', POINTER(IFilterGraph)),
    ]

class _PinInfo(Structure):
    _fields_ = [
        ('pFilter', POINTER(IBaseFilter)),
        ('dir', _PinDirection),
        ('achName', c_ushort * 128),
    ]

class VIDEOINFOHEADER(Structure):
	_fields_ = (
		('rcSource', RECT),
		('rcTarget', RECT),
		('dwBitRate', DWORD),
		('dwBitErrorRate', DWORD),
		('AvgTimePerFrame', REFERENCE_TIME),
	)

class VIDEOINFOHEADER2(Structure):
	_fields_ = (
		('rcSource', RECT),
		('rcTarget', RECT),
		('dwBitRate', DWORD),
		('dwBitErrorRate', DWORD),
		('AvgTimePerFrame', REFERENCE_TIME),
	)

class VMR9NormalizedRect(Structure):
	_fields_ = (
		('left', FLOAT),
		('top', FLOAT),
		('right', FLOAT),
		('bottom', FLOAT)
	)

class VMR9ProcAmpControl(Structure):
	_fields_ = (
		('dwSize', DWORD),
		('dwFlags', DWORD),
		('Brightness', FLOAT),
		('Contrast', FLOAT),
		('Hue', FLOAT),
		('Saturation', FLOAT)
	)
	def __init__(self):
		self.dwSize = sizeof(VMR9ProcAmpControl)

class VMR9ProcAmpControlRange(Structure):
	_fields_ = (
		('dwSize', DWORD),
		('dwProperty', DWORD),
		('MinValue', FLOAT),
		('MaxValue', FLOAT),
		('DefaultValue', FLOAT),
		('StepSize', FLOAT)
	)
	def __init__(self):
		self.dwSize = sizeof(self)

class DXVA2_Fixed32(Structure):
	_fields_ = (
		('Fraction', USHORT),
		('Value', SHORT),
	)

class DXVA2_ValueRange(Structure):
	_fields_ = (
		('MinValue', DXVA2_Fixed32),
		('MaxValue', DXVA2_Fixed32),
		('DefaultValue', DXVA2_Fixed32),
		('StepSize', DXVA2_Fixed32)
	)

class DXVA2_ProcAmpValues(Structure):
	_fields_ = (
		('Brightness', DXVA2_Fixed32),
		('Contrast', DXVA2_Fixed32),
		('Hue', DXVA2_Fixed32),
		('Saturation', DXVA2_Fixed32)
	)

class DDCOLORKEY(Structure):
    _fields_ = [
        ('dw1', c_ulong),
        ('dw2', c_ulong),
    ]

class _NORMALIZEDRECT(Structure):
    _fields_ = [
        ('left', c_float),
        ('top', c_float),
        ('right', c_float),
        ('bottom', c_float),
    ]

class _VMRVIDEOSTREAMINFO(Structure):
    _fields_ = [
        ('pddsVideoSurface', POINTER(c_ulong)),
        ('dwWidth', c_ulong),
        ('dwHeight', c_ulong),
        ('dwStrmID', c_ulong),
        ('fAlpha', c_float),
        ('ddClrKey', DDCOLORKEY),
        ('rNormal', _NORMALIZEDRECT),
    ]

########################################
# INTERFACE IMPLEMENTATIONS
########################################

IMediaFilter._methods_ = [
    COMMETHOD([], HRESULT, 'Stop'),
    COMMETHOD([], HRESULT, 'Pause'),
    COMMETHOD([], HRESULT, 'Run',
              ( [], c_longlong, 'tStart' )),
    COMMETHOD([], HRESULT, 'GetState',
              ( ['in'], c_ulong, 'dwMilliSecsTimeout' ),
              ( ['out'], POINTER(_FilterState), 'State' )),
    COMMETHOD([], HRESULT, 'SetSyncSource',
              ( ['in'], POINTER(IReferenceClock), 'pClock' )),
    COMMETHOD([], HRESULT, 'GetSyncSource',
              ( ['out'], POINTER(POINTER(IReferenceClock)), 'pClock' )),
]

IPersistStream._methods_ = [
    COMMETHOD([], HRESULT, 'IsDirty'),
    COMMETHOD([], HRESULT, 'Load',
              ( ['in'], POINTER(IStream), 'pstm' )),
    COMMETHOD([], HRESULT, 'Save',
              ( ['in'], POINTER(IStream), 'pstm' ),
              ( ['in'], c_int, 'fClearDirty' )),
    COMMETHOD([], HRESULT, 'GetSizeMax',
              ( ['out'], POINTER(ULARGE_INTEGER), 'pcbSize' )),
]

IAMStreamConfig._methods_ = [
    COMMETHOD([], HRESULT, 'SetFormat',
              ( ['in'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'GetFormat',
              ( ['out'], POINTER(POINTER(_AMMediaType)), 'ppmt' )),
    COMMETHOD([], HRESULT, 'GetNumberOfCapabilities',
              ( ['out'], POINTER(c_int), 'piCount' ),
              ( ['out'], POINTER(c_int), 'piSize' )),
    COMMETHOD([], HRESULT, 'GetStreamCaps',
              ( ['in'], c_int, 'iIndex' ),
              ( ['out'], POINTER(POINTER(_AMMediaType)), 'ppmt' ),
              ( ['out'], POINTER(c_ubyte), 'pSCC' )),
]

IAMStreamSelect._methods_ = [
    COMMETHOD([], HRESULT, 'Count',
              ( ['out'], POINTER(c_ulong), 'pcStreams' )),
    COMMETHOD([], HRESULT, 'Info',
              ( ['in'], c_int, 'lIndex' ),
              ( ['out'], POINTER(POINTER(_AMMediaType)), 'ppmt' ),
              ( ['out'], POINTER(c_ulong), 'pdwFlags' ),
              ( ['out'], POINTER(c_ulong), 'plcid' ),
              ( ['out'], POINTER(DWORD), 'pdwGroup' ),
              ( ['out'], POINTER(LPWSTR), 'ppszName' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppObject' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppunk' )),
    COMMETHOD([], HRESULT, 'Enable',
              ( ['in'], c_int, 'lIndex' ),
              ( ['in'], c_ulong, 'dwFlags' )),
]

IBaseFilter._methods_ = [
    COMMETHOD([], HRESULT, 'EnumPins',
              ( ['out', 'retval'], POINTER(POINTER(IEnumPins)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'FindPin',
              ( ['in'], c_wchar_p, 'Id' ),
              ( ['out', 'retval'], POINTER(POINTER(IPin)), 'ppPin' )),
    COMMETHOD([], HRESULT, 'QueryFilterInfo',
              ( ['out', 'retval'], POINTER(_FilterInfo), 'pInfo' )),
    COMMETHOD([], HRESULT, 'JoinFilterGraph',
              ( ['in'], POINTER(IFilterGraph), 'pGraph' ),
              ( ['in'], c_wchar_p, 'pName' )),
    COMMETHOD([], HRESULT, 'QueryVendorInfo',
              ( ['out', 'retval'], POINTER(c_wchar_p), 'pVendorInfo' )),
]

IBasicAudio._methods_ = [
    COMMETHOD([dispid(1610743808), 'propput'], HRESULT, 'Volume',
              ( ['in'], c_int, 'plVolume' )),
    COMMETHOD([dispid(1610743808), 'propget'], HRESULT, 'Volume',
              ( ['out', 'retval'], POINTER(c_int), 'plVolume' )),
    COMMETHOD([dispid(1610743810), 'propput'], HRESULT, 'Balance',
              ( ['in'], c_int, 'plBalance' )),
    COMMETHOD([dispid(1610743810), 'propget'], HRESULT, 'Balance',
              ( ['out', 'retval'], POINTER(c_int), 'plBalance' )),
]

IBasicVideo._methods_ = [
    COMMETHOD([dispid(1610743808), 'propget'], HRESULT, 'AvgTimePerFrame',
              ( ['out', 'retval'], POINTER(c_double), 'pAvgTimePerFrame' )),
    COMMETHOD([dispid(1610743809), 'propget'], HRESULT, 'BitRate',
              ( ['out', 'retval'], POINTER(c_int), 'pBitRate' )),
    COMMETHOD([dispid(1610743810), 'propget'], HRESULT, 'BitErrorRate',
              ( ['out', 'retval'], POINTER(c_int), 'pBitErrorRate' )),
    COMMETHOD([dispid(1610743811), 'propget'], HRESULT, 'VideoWidth',
              ( ['out', 'retval'], POINTER(c_int), 'pVideoWidth' )),
    COMMETHOD([dispid(1610743812), 'propget'], HRESULT, 'VideoHeight',
              ( ['out', 'retval'], POINTER(c_int), 'pVideoHeight' )),
    COMMETHOD([dispid(1610743813), 'propput'], HRESULT, 'SourceLeft',
              ( ['in'], c_int, 'pSourceLeft' )),
    COMMETHOD([dispid(1610743813), 'propget'], HRESULT, 'SourceLeft',
              ( ['out', 'retval'], POINTER(c_int), 'pSourceLeft' )),
    COMMETHOD([dispid(1610743815), 'propput'], HRESULT, 'SourceWidth',
              ( ['in'], c_int, 'pSourceWidth' )),
    COMMETHOD([dispid(1610743815), 'propget'], HRESULT, 'SourceWidth',
              ( ['out', 'retval'], POINTER(c_int), 'pSourceWidth' )),
    COMMETHOD([dispid(1610743817), 'propput'], HRESULT, 'SourceTop',
              ( ['in'], c_int, 'pSourceTop' )),
    COMMETHOD([dispid(1610743817), 'propget'], HRESULT, 'SourceTop',
              ( ['out', 'retval'], POINTER(c_int), 'pSourceTop' )),
    COMMETHOD([dispid(1610743819), 'propput'], HRESULT, 'SourceHeight',
              ( ['in'], c_int, 'pSourceHeight' )),
    COMMETHOD([dispid(1610743819), 'propget'], HRESULT, 'SourceHeight',
              ( ['out', 'retval'], POINTER(c_int), 'pSourceHeight' )),
    COMMETHOD([dispid(1610743821), 'propput'], HRESULT, 'DestinationLeft',
              ( ['in'], c_int, 'pDestinationLeft' )),
    COMMETHOD([dispid(1610743821), 'propget'], HRESULT, 'DestinationLeft',
              ( ['out', 'retval'], POINTER(c_int), 'pDestinationLeft' )),
    COMMETHOD([dispid(1610743823), 'propput'], HRESULT, 'DestinationWidth',
              ( ['in'], c_int, 'pDestinationWidth' )),
    COMMETHOD([dispid(1610743823), 'propget'], HRESULT, 'DestinationWidth',
              ( ['out', 'retval'], POINTER(c_int), 'pDestinationWidth' )),
    COMMETHOD([dispid(1610743825), 'propput'], HRESULT, 'DestinationTop',
              ( ['in'], c_int, 'pDestinationTop' )),
    COMMETHOD([dispid(1610743825), 'propget'], HRESULT, 'DestinationTop',
              ( ['out', 'retval'], POINTER(c_int), 'pDestinationTop' )),
    COMMETHOD([dispid(1610743827), 'propput'], HRESULT, 'DestinationHeight',
              ( ['in'], c_int, 'pDestinationHeight' )),
    COMMETHOD([dispid(1610743827), 'propget'], HRESULT, 'DestinationHeight',
              ( ['out', 'retval'], POINTER(c_int), 'pDestinationHeight' )),
    COMMETHOD([dispid(1610743829)], HRESULT, 'SetSourcePosition',
              ( ['in'], c_int, 'Left' ),
              ( ['in'], c_int, 'Top' ),
              ( ['in'], c_int, 'Width' ),
              ( ['in'], c_int, 'Height' )),
    COMMETHOD([dispid(1610743830)], HRESULT, 'GetSourcePosition',
              ( ['out'], POINTER(c_int), 'pLeft' ),
              ( ['out'], POINTER(c_int), 'pTop' ),
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743831)], HRESULT, 'SetDefaultSourcePosition'),
    COMMETHOD([dispid(1610743832)], HRESULT, 'SetDestinationPosition',
              ( ['in'], c_int, 'Left' ),
              ( ['in'], c_int, 'Top' ),
              ( ['in'], c_int, 'Width' ),
              ( ['in'], c_int, 'Height' )),
    COMMETHOD([dispid(1610743833)], HRESULT, 'GetDestinationPosition',
              ( ['out'], POINTER(c_int), 'pLeft' ),
              ( ['out'], POINTER(c_int), 'pTop' ),
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743834)], HRESULT, 'SetDefaultDestinationPosition'),
    COMMETHOD([dispid(1610743835)], HRESULT, 'GetVideoSize',
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743836)], HRESULT, 'GetVideoPaletteEntries',
              ( ['in'], c_int, 'StartIndex' ),
              ( ['in'], c_int, 'Entries' ),
              ( ['out'], POINTER(c_int), 'pRetrieved' ),
              ( ['out'], POINTER(c_int), 'pPalette' )),
    COMMETHOD([dispid(1610743837)], HRESULT, 'GetCurrentImage',
              ( ['in'], LPLONG, 'pBufferSize' ), # 'in', 'out'
              ( ['in'], LPLONG, 'pDIBImage' )),  # out
    COMMETHOD([dispid(1610743838)], HRESULT, 'IsUsingDefaultSource'),
    COMMETHOD([dispid(1610743839)], HRESULT, 'IsUsingDefaultDestination'),
]

IBasicVideo2._methods_ = [
    COMMETHOD([], HRESULT, 'GetPreferredAspectRatio',
              ( ['out'], POINTER(c_int), 'plAspectX' ),
              ( ['out'], POINTER(c_int), 'plAspectY' )),
]

IBindCtx._methods_ = [
    COMMETHOD([], HRESULT, 'RegisterObjectBound',
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'RevokeObjectBound',
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'ReleaseBoundObjects'),
    COMMETHOD([], HRESULT, 'RemoteSetBindOptions',
              ( ['in'], POINTER(tagBIND_OPTS2), 'pbindopts' )),
    COMMETHOD([], HRESULT, 'RemoteGetBindOptions',
              ( ['in', 'out'], POINTER(tagBIND_OPTS2), 'pbindopts' )),
    COMMETHOD([], HRESULT, 'GetRunningObjectTable',
              ( ['out'], POINTER(POINTER(IRunningObjectTable)), 'pprot' )),
    COMMETHOD([], HRESULT, 'RegisterObjectParam',
              ( ['in'], c_wchar_p, 'pszKey' ),
              ( ['in'], POINTER(IUnknown), 'punk' )),
    COMMETHOD([], HRESULT, 'GetObjectParam',
              ( ['in'], c_wchar_p, 'pszKey' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppunk' )),
    COMMETHOD([], HRESULT, 'EnumObjectParam',
              ( ['out'], POINTER(POINTER(IEnumString)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'RevokeObjectParam',
              ( ['in'], c_wchar_p, 'pszKey' )),
]

#ID3DFullscreenControl._methods_ = [
#	COMMETHOD([], HRESULT, 'SetD3DFullscreen',
#			(['in'], BOOL, 'fEnabled')),
#	COMMETHOD([], HRESULT, 'GetD3DFullscreen',
#			(['in'], LPBOOL, 'pfEnabled'))
#]

IDirectVobSub._methods_ = [
	COMMETHOD([], HRESULT, 'get_FileName',
			(['in'], POINTER(BSTR), 'fn')),
	COMMETHOD([], HRESULT, 'put_FileName',
			(['in'], BSTR, 'fn')),
	COMMETHOD([], HRESULT, 'get_LanguageCount',
			(['retval', 'out'], POINTER(INT), 'nLangs')),
	COMMETHOD([], HRESULT, 'get_LanguageName',
			(['in'], BSTR, 'iLanguage'),
			(['retval', 'out'], POINTER(POINTER(BSTR)), 'ppName')),
	COMMETHOD([], HRESULT, 'get_SelectedLanguage',
			(['retval', 'out'], POINTER(INT), 'iSelected')),
	COMMETHOD([], HRESULT, 'put_SelectedLanguage',
			(['in'], INT, 'iSelected')),
	COMMETHOD([], HRESULT, 'get_HideSubtitles',
			(['retval', 'out'], POINTER(BOOL), 'fHideSubtitles')),
	COMMETHOD([], HRESULT, 'put_HideSubtitles',
			(['in'], BOOL, 'fHideSubtitles')),
]

IEnumFilters._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'cFilters' ),
              ( ['out'], POINTER(POINTER(IBaseFilter)), 'ppFilter' ),
              ( ['out'], POINTER(c_ulong), 'pcFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'cFilters' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumFilters)), 'ppenum' )),
]

IEnumMoniker._methods_ = [
    COMMETHOD([], HRESULT, 'RemoteNext',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenum' )),
]

IEnumPins._methods_ = [
    COMMETHOD([], HRESULT, 'Next',
              ( ['in'], c_ulong, 'cPins' ),
              ( ['out'], POINTER(POINTER(IPin)), 'ppPins' ),
              ( ['out'], POINTER(c_ulong), 'pcFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'cPins' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out', 'retval'], POINTER(POINTER(IEnumPins)), 'ppenum' )),
]

IEnumString._methods_ = [
    COMMETHOD([], HRESULT, 'RemoteNext',
              ( ['in'], c_ulong, 'celt' ),
              ( ['out'], POINTER(c_wchar_p), 'rgelt' ),
              ( ['out'], POINTER(c_ulong), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
              ( ['in'], c_ulong, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
              ( ['out'], POINTER(POINTER(IEnumString)), 'ppenum' )),
]

IFileSourceFilter._methods_ = [
    COMMETHOD([], HRESULT, 'Load',
              ( ['in'], c_wchar_p, 'pszFileName' ),
              ( ['in'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'GetCurFile',
              ( ['out'], POINTER(c_wchar_p), 'ppszFileName' ),
              ( ['out'], POINTER(_AMMediaType), 'pmt' )),
]

IFilterGraph._methods_ = [
    COMMETHOD([], HRESULT, 'AddFilter',
              ( ['in'], POINTER(IBaseFilter), 'pFilter' ),
              ( ['in'], c_wchar_p, 'pName' )),
    COMMETHOD([], HRESULT, 'RemoveFilter',
              ( ['in'], POINTER(IBaseFilter), 'pFilter' )),
    COMMETHOD([], HRESULT, 'EnumFilters',
              ( ['out'], POINTER(POINTER(IEnumFilters)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'FindFilterByName',
              ( ['in'], c_wchar_p, 'pName' ),
              ( ['out'], POINTER(POINTER(IBaseFilter)), 'ppFilter' )),
    COMMETHOD([], HRESULT, 'ConnectDirect',
              ( ['in'], POINTER(IPin), 'ppinOut' ),
              ( ['in'], POINTER(IPin), 'ppinIn' ),
              ( ['in'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'Reconnect',
              ( ['in'], POINTER(IPin), 'pPin' )),
    COMMETHOD([], HRESULT, 'Disconnect',
              ( ['in'], POINTER(IPin), 'pPin' )),
    COMMETHOD([], HRESULT, 'SetDefaultSyncSource'),
]

IMediaControl._methods_ = [
    COMMETHOD([dispid(1610743808)], HRESULT, 'Run'),
    COMMETHOD([dispid(1610743809)], HRESULT, 'Pause'),
    COMMETHOD([dispid(1610743810)], HRESULT, 'Stop'),
    COMMETHOD([dispid(1610743811)], HRESULT, 'GetState',
              ( ['in'], c_int, 'msTimeout' ),
              ( ['out'], POINTER(c_int), 'pfs' )),
    COMMETHOD([dispid(1610743812)], HRESULT, 'RenderFile',
              ( ['in'], BSTR, 'strFilename' )),
    COMMETHOD([dispid(1610743813)], HRESULT, 'AddSourceFilter',
              ( ['in'], BSTR, 'strFilename' ),
              ( ['out'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743814), 'propget'], HRESULT, 'FilterCollection',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743815), 'propget'], HRESULT, 'RegFilterCollection',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743816)], HRESULT, 'StopWhenReady'),
]

IMediaEvent._methods_ = [
    COMMETHOD([dispid(1610743808)], HRESULT, 'GetEventHandle',
              ( ['out'], POINTER(LONG_PTR), 'hEvent' )),
    COMMETHOD([dispid(1610743809)], HRESULT, 'GetEvent',
              ( ['out'], POINTER(c_int), 'lEventCode' ),
              ( ['out'], POINTER(LONG_PTR), 'lParam1' ),
              ( ['out'], POINTER(LONG_PTR), 'lParam2' ),
              ( ['in'], c_int, 'msTimeout' )),
    COMMETHOD([dispid(1610743810)], HRESULT, 'WaitForCompletion',
              ( ['in'], c_int, 'msTimeout' ),
              ( ['out'], POINTER(c_int), 'pEvCode' )),
    COMMETHOD([dispid(1610743811)], HRESULT, 'CancelDefaultHandling',
              ( ['in'], c_int, 'lEvCode' )),
    COMMETHOD([dispid(1610743812)], HRESULT, 'RestoreDefaultHandling',
              ( ['in'], c_int, 'lEvCode' )),
    COMMETHOD([dispid(1610743813)], HRESULT, 'FreeEventParams',
              ( ['in'], c_int, 'lEvCode' ),
              ( ['in'], LONG_PTR, 'lParam1' ),
              ( ['in'], LONG_PTR, 'lParam2' )),
]

IMediaEventEx._methods_ = [
    COMMETHOD([], HRESULT, 'SetNotifyWindow',
              ( ['in'], LONG_PTR, 'hwnd' ),
              ( ['in'], c_int, 'lMsg' ),
              ( ['in'], LONG_PTR, 'lInstanceData' )),
    COMMETHOD([], HRESULT, 'SetNotifyFlags',
              ( ['in'], c_int, 'lNoNotifyFlags' )),
    COMMETHOD([], HRESULT, 'GetNotifyFlags',
              ( ['out'], POINTER(c_int), 'lplNoNotifyFlags' )),
]

IMediaEventSink._methods_ = [
    COMMETHOD([], HRESULT, 'Notify',
              ( ['in'], c_int, 'EventCode' ),
              ( ['in'], LONG_PTR, 'EventParam1' ),
              ( ['in'], LONG_PTR, 'EventParam2' )),
]

IMediaSeeking._methods_ = [
    COMMETHOD([], HRESULT, 'GetCapabilities',
              ( ['out'], POINTER(c_ulong), 'pCapabilities' )),
    COMMETHOD([], HRESULT, 'CheckCapabilities',
              ( ['in', 'out'], POINTER(c_ulong), 'pCapabilities' )),
    COMMETHOD([], HRESULT, 'IsFormatSupported',
              ( ['in'], POINTER(GUID), 'pFormat' )),
    COMMETHOD([], HRESULT, 'QueryPreferredFormat',
              ( ['out'], POINTER(GUID), 'pFormat' )),
    COMMETHOD([], HRESULT, 'GetTimeFormat',
              ( ['out'], POINTER(GUID), 'pFormat' )),
    COMMETHOD([], HRESULT, 'IsUsingTimeFormat',
              ( ['in'], POINTER(GUID), 'pFormat' )),
    COMMETHOD([], HRESULT, 'SetTimeFormat',
              ( ['in'], POINTER(GUID), 'pFormat' )),
    COMMETHOD([], HRESULT, 'GetDuration',
              ( ['out'], POINTER(c_longlong), 'pDuration' )),
    COMMETHOD([], HRESULT, 'GetStopPosition',
              ( ['out'], POINTER(c_longlong), 'pStop' )),
    COMMETHOD([], HRESULT, 'GetCurrentPosition',
              ( ['out'], POINTER(c_longlong), 'pCurrent' )),
    COMMETHOD([], HRESULT, 'ConvertTimeFormat',
              ( ['out'], POINTER(c_longlong), 'pTarget' ),
              ( ['in'], POINTER(GUID), 'pTargetFormat' ),
              ( ['in'], c_longlong, 'Source' ),
              ( ['in'], POINTER(GUID), 'pSourceFormat' )),
    COMMETHOD([], HRESULT, 'SetPositions',
              ( ['in', 'out'], POINTER(c_longlong), 'pCurrent' ),
              ( ['in'], c_ulong, 'dwCurrentFlags' ),
              ( ['in', 'out'], POINTER(c_longlong), 'pStop' ),
              ( ['in'], c_ulong, 'dwStopFlags' )),
    COMMETHOD([], HRESULT, 'GetPositions',
              ( ['out'], POINTER(c_longlong), 'pCurrent' ),
              ( ['out'], POINTER(c_longlong), 'pStop' )),
    COMMETHOD([], HRESULT, 'GetAvailable',
              ( ['out'], POINTER(c_longlong), 'pEarliest' ),
              ( ['out'], POINTER(c_longlong), 'pLatest' )),
    COMMETHOD([], HRESULT, 'SetRate',
              ( ['in'], c_double, 'dRate' )),
    COMMETHOD([], HRESULT, 'GetRate',
              ( ['out'], POINTER(c_double), 'pdRate' )),
    COMMETHOD([], HRESULT, 'GetPreroll',
              ( ['out'], POINTER(c_longlong), 'pllPreroll' )),
]

IMoniker._methods_ = [
    COMMETHOD([], HRESULT, 'RemoteBindToObject',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(GUID), 'riidResult' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppvResult' )),
    COMMETHOD([], HRESULT, 'RemoteBindToStorage',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(GUID), 'riid' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppvObj' )),
    COMMETHOD([], HRESULT, 'Reduce',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], c_ulong, 'dwReduceHowFar' ),
              ( ['in', 'out'], POINTER(POINTER(IMoniker)), 'ppmkToLeft' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkReduced' )),
    COMMETHOD([], HRESULT, 'ComposeWith',
              ( ['in'], POINTER(IMoniker), 'pmkRight' ),
              ( ['in'], c_int, 'fOnlyIfNotGeneric' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkComposite' )),
    COMMETHOD([], HRESULT, 'Enum',
              ( ['in'], c_int, 'fForward' ),
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenumMoniker' )),
    COMMETHOD([], HRESULT, 'IsEqual',
              ( ['in'], POINTER(IMoniker), 'pmkOtherMoniker' )),
    COMMETHOD([], HRESULT, 'Hash',
              ( ['out'], POINTER(c_ulong), 'pdwHash' )),
    COMMETHOD([], HRESULT, 'IsRunning',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], POINTER(IMoniker), 'pmkNewlyRunning' )),
    COMMETHOD([], HRESULT, 'GetTimeOfLastChange',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['out'], POINTER(FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'Inverse',
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmk' )),
    COMMETHOD([], HRESULT, 'CommonPrefixWith',
              ( ['in'], POINTER(IMoniker), 'pmkOther' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkPrefix' )),
    COMMETHOD([], HRESULT, 'RelativePathTo',
              ( ['in'], POINTER(IMoniker), 'pmkOther' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkRelPath' )),
    COMMETHOD([], HRESULT, 'GetDisplayName',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['out'], POINTER(c_wchar_p), 'ppszDisplayName' )),
    COMMETHOD([], HRESULT, 'ParseDisplayName',
              ( ['in'], POINTER(IBindCtx), 'pbc' ),
              ( ['in'], POINTER(IMoniker), 'pmkToLeft' ),
              ( ['in'], c_wchar_p, 'pszDisplayName' ),
              ( ['out'], POINTER(c_ulong), 'pchEaten' ),
              ( ['out'], POINTER(POINTER(IMoniker)), 'ppmkOut' )),
    COMMETHOD([], HRESULT, 'IsSystemMoniker',
              ( ['out'], POINTER(c_ulong), 'pdwMksys' )),
]

IPin._methods_ = [
    COMMETHOD([], HRESULT, 'Connect',
              ( ['in'], POINTER(IPin), 'pReceivePin' ),
              ( ['in'], c_ulong, 'pmt' )),
    COMMETHOD([], HRESULT, 'ReceiveConnection',
              ( ['in'], POINTER(IPin), 'pConnector' ),
              ( ['in'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'Disconnect'),
    COMMETHOD([], HRESULT, 'ConnectedTo',
              ( ['out', 'retval'], POINTER(POINTER(IPin)), 'pPin' )),
    COMMETHOD([], HRESULT, 'ConnectionMediaType',
              ( ['out'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'QueryPinInfo',
              ( ['out', 'retval'], POINTER(_PinInfo), 'pInfo' )),
    COMMETHOD([], HRESULT, 'QueryDirection',
              ( ['out', 'retval'], POINTER(_PinDirection), 'pPinDir' )),
    COMMETHOD([], HRESULT, 'QueryId',
              ( ['out', 'retval'], POINTER(c_wchar_p), 'Id' )),
    COMMETHOD([], HRESULT, 'QueryAccept',
              ( ['in'], POINTER(_AMMediaType), 'pmt' )),
    COMMETHOD([], HRESULT, 'EnumMediaTypes',
              ( ['out', 'retval'], POINTER(POINTER(IEnumMediaTypes)), 'ppenum' )),
    COMMETHOD([], HRESULT, 'QueryInternalConnections',
              ( ['out'], POINTER(POINTER(IPin)), 'apPin' ),
              ( ['in', 'out'], POINTER(c_ulong), 'nPin' )),
    COMMETHOD([], HRESULT, 'EndOfStream'),
    COMMETHOD([], HRESULT, 'BeginFlush'),
    COMMETHOD([], HRESULT, 'EndFlush'),
    COMMETHOD([], HRESULT, 'NewSegment',
              ( ['in'], c_longlong, 'tStart' ),
              ( ['in'], c_longlong, 'tStop' ),
              ( ['in'], c_double, 'dRate' )),
]

IPinInfo._methods_ = [
    COMMETHOD([dispid(1610743808), 'propget'], HRESULT, 'Pin',
              ( ['out', 'retval'], POINTER(POINTER(IUnknown)), 'ppUnk' )),
    COMMETHOD([dispid(1610743809), 'propget'], HRESULT, 'ConnectedTo',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743810), 'propget'], HRESULT, 'ConnectionMediaType',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743811), 'propget'], HRESULT, 'FilterInfo',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743812), 'propget'], HRESULT, 'Name',
              ( ['out', 'retval'], POINTER(BSTR), 'ppUnk' )),
    COMMETHOD([dispid(1610743813), 'propget'], HRESULT, 'Direction',
              ( ['out', 'retval'], POINTER(c_int), 'ppDirection' )),
    COMMETHOD([dispid(1610743814), 'propget'], HRESULT, 'PinID',
              ( ['out', 'retval'], POINTER(BSTR), 'strPinID' )),
    COMMETHOD([dispid(1610743815), 'propget'], HRESULT, 'MediaTypes',
              ( ['out', 'retval'], POINTER(POINTER(IDispatch)), 'ppUnk' )),
    COMMETHOD([dispid(1610743816)], HRESULT, 'Connect',
              ( ['in'], POINTER(IUnknown), 'pPin' )),
    COMMETHOD([dispid(1610743817)], HRESULT, 'ConnectDirect',
              ( ['in'], POINTER(IUnknown), 'pPin' )),
    COMMETHOD([dispid(1610743818)], HRESULT, 'ConnectWithType',
              ( ['in'], POINTER(IUnknown), 'pPin' ),
              ( ['in'], POINTER(IDispatch), 'pMediaType' )),
    COMMETHOD([dispid(1610743819)], HRESULT, 'Disconnect'),
    COMMETHOD([dispid(1610743820)], HRESULT, 'Render'),
]

IReferenceClock._methods_ = [
    COMMETHOD([], HRESULT, 'GetTime',
              ( ['out'], POINTER(c_longlong), 'pTime' )),
    COMMETHOD([], HRESULT, 'AdviseTime',
              ( ['in'], c_longlong, 'baseTime' ),
              ( ['in'], c_longlong, 'streamTime' ),
              ( ['in'], ULONG_PTR, 'hEvent' ),
              ( ['out'], POINTER(ULONG_PTR), 'pdwAdviseCookie' )),
    COMMETHOD([], HRESULT, 'AdvisePeriodic',
              ( ['in'], c_longlong, 'startTime' ),
              ( ['in'], c_longlong, 'periodTime' ),
              ( ['in'], ULONG_PTR, 'hSemaphore' ),
              ( ['out'], POINTER(ULONG_PTR), 'pdwAdviseCookie' )),
    COMMETHOD([], HRESULT, 'Unadvise',
              ( ['in'], ULONG_PTR, 'dwAdviseCookie' )),
]

IRunningObjectTable._methods_ = [
    COMMETHOD([], HRESULT, 'Register',
              ( ['in'], c_ulong, 'grfFlags' ),
              ( ['in'], POINTER(IUnknown), 'punkObject' ),
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(c_ulong), 'pdwRegister' )),
    COMMETHOD([], HRESULT, 'Revoke',
              ( ['in'], c_ulong, 'dwRegister' )),
    COMMETHOD([], HRESULT, 'IsRunning',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' )),
    COMMETHOD([], HRESULT, 'GetObject',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(POINTER(IUnknown)), 'ppunkObject' )),
    COMMETHOD([], HRESULT, 'NoteChangeTime',
              ( ['in'], c_ulong, 'dwRegister' ),
              ( ['in'], POINTER(FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'GetTimeOfLastChange',
              ( ['in'], POINTER(IMoniker), 'pmkObjectName' ),
              ( ['out'], POINTER(FILETIME), 'pfiletime' )),
    COMMETHOD([], HRESULT, 'EnumRunning',
              ( ['out'], POINTER(POINTER(IEnumMoniker)), 'ppenumMoniker' )),
]

IVideoWindow._methods_ = [
    COMMETHOD([dispid(1610743808), 'propput'], HRESULT, 'Caption',
              ( ['in'], BSTR, 'strCaption' )),
    COMMETHOD([dispid(1610743808), 'propget'], HRESULT, 'Caption',
              ( ['out', 'retval'], POINTER(BSTR), 'strCaption' )),
    COMMETHOD([dispid(1610743810), 'propput'], HRESULT, 'WindowStyle',
              ( ['in'], c_int, 'WindowStyle' )),
    COMMETHOD([dispid(1610743810), 'propget'], HRESULT, 'WindowStyle',
              ( ['out', 'retval'], POINTER(c_int), 'WindowStyle' )),
    COMMETHOD([dispid(1610743812), 'propput'], HRESULT, 'WindowStyleEx',
              ( ['in'], c_int, 'WindowStyleEx' )),
    COMMETHOD([dispid(1610743812), 'propget'], HRESULT, 'WindowStyleEx',
              ( ['out', 'retval'], POINTER(c_int), 'WindowStyleEx' )),
    COMMETHOD([dispid(1610743814), 'propput'], HRESULT, 'AutoShow',
              ( ['in'], c_int, 'AutoShow' )),
    COMMETHOD([dispid(1610743814), 'propget'], HRESULT, 'AutoShow',
              ( ['out', 'retval'], POINTER(c_int), 'AutoShow' )),
    COMMETHOD([dispid(1610743816), 'propput'], HRESULT, 'WindowState',
              ( ['in'], c_int, 'WindowState' )),
    COMMETHOD([dispid(1610743816), 'propget'], HRESULT, 'WindowState',
              ( ['out', 'retval'], POINTER(c_int), 'WindowState' )),
    COMMETHOD([dispid(1610743818), 'propput'], HRESULT, 'BackgroundPalette',
              ( ['in'], c_int, 'pBackgroundPalette' )),
    COMMETHOD([dispid(1610743818), 'propget'], HRESULT, 'BackgroundPalette',
              ( ['out', 'retval'], POINTER(c_int), 'pBackgroundPalette' )),
    COMMETHOD([dispid(1610743820), 'propput'], HRESULT, 'Visible',
              ( ['in'], c_int, 'pVisible' )),
    COMMETHOD([dispid(1610743820), 'propget'], HRESULT, 'Visible',
              ( ['out', 'retval'], POINTER(c_int), 'pVisible' )),
    COMMETHOD([dispid(1610743822), 'propput'], HRESULT, 'Left',
              ( ['in'], c_int, 'pLeft' )),
    COMMETHOD([dispid(1610743822), 'propget'], HRESULT, 'Left',
              ( ['out', 'retval'], POINTER(c_int), 'pLeft' )),
    COMMETHOD([dispid(1610743824), 'propput'], HRESULT, 'Width',
              ( ['in'], c_int, 'pWidth' )),
    COMMETHOD([dispid(1610743824), 'propget'], HRESULT, 'Width',
              ( ['out', 'retval'], POINTER(c_int), 'pWidth' )),
    COMMETHOD([dispid(1610743826), 'propput'], HRESULT, 'Top',
              ( ['in'], c_int, 'pTop' )),
    COMMETHOD([dispid(1610743826), 'propget'], HRESULT, 'Top',
              ( ['out', 'retval'], POINTER(c_int), 'pTop' )),
    COMMETHOD([dispid(1610743828), 'propput'], HRESULT, 'Height',
              ( ['in'], c_int, 'pHeight' )),
    COMMETHOD([dispid(1610743828), 'propget'], HRESULT, 'Height',
              ( ['out', 'retval'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743830), 'propput'], HRESULT, 'Owner',
              ( ['in'], LONG_PTR, 'Owner' )),
    COMMETHOD([dispid(1610743830), 'propget'], HRESULT, 'Owner',
              ( ['out', 'retval'], POINTER(LONG_PTR), 'Owner' )),
    COMMETHOD([dispid(1610743832), 'propput'], HRESULT, 'MessageDrain',
              ( ['in'], LONG_PTR, 'Drain' )),
    COMMETHOD([dispid(1610743832), 'propget'], HRESULT, 'MessageDrain',
              ( ['out', 'retval'], POINTER(LONG_PTR), 'Drain' )),
    COMMETHOD([dispid(1610743834), 'propget'], HRESULT, 'BorderColor',
              ( ['out', 'retval'], POINTER(c_int), 'Color' )),
    COMMETHOD([dispid(1610743834), 'propput'], HRESULT, 'BorderColor',
              ( ['in'], c_int, 'Color' )),
    COMMETHOD([dispid(1610743836), 'propget'], HRESULT, 'FullScreenMode',
              ( ['out', 'retval'], POINTER(c_int), 'FullScreenMode' )),
    COMMETHOD([dispid(1610743836), 'propput'], HRESULT, 'FullScreenMode',
              ( ['in'], c_int, 'FullScreenMode' )),
    COMMETHOD([dispid(1610743838)], HRESULT, 'SetWindowForeground',
              ( ['in'], c_int, 'Focus' )),
    COMMETHOD([dispid(1610743839)], HRESULT, 'NotifyOwnerMessage',
              ( ['in'], LONG_PTR, 'hwnd' ),
              ( ['in'], c_int, 'uMsg' ),
              ( ['in'], LONG_PTR, 'wParam' ),
              ( ['in'], LONG_PTR, 'lParam' )),
    COMMETHOD([dispid(1610743840)], HRESULT, 'SetWindowPosition',
              ( ['in'], c_int, 'Left' ),
              ( ['in'], c_int, 'Top' ),
              ( ['in'], c_int, 'Width' ),
              ( ['in'], c_int, 'Height' )),
    COMMETHOD([dispid(1610743841)], HRESULT, 'GetWindowPosition',
              ( ['out'], POINTER(c_int), 'pLeft' ),
              ( ['out'], POINTER(c_int), 'pTop' ),
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743842)], HRESULT, 'GetMinIdealImageSize',
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743843)], HRESULT, 'GetMaxIdealImageSize',
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743844)], HRESULT, 'GetRestorePosition',
              ( ['out'], POINTER(c_int), 'pLeft' ),
              ( ['out'], POINTER(c_int), 'pTop' ),
              ( ['out'], POINTER(c_int), 'pWidth' ),
              ( ['out'], POINTER(c_int), 'pHeight' )),
    COMMETHOD([dispid(1610743845)], HRESULT, 'HideCursor',
              ( ['in'], c_int, 'HideCursor' )),
    COMMETHOD([dispid(1610743846)], HRESULT, 'IsCursorHidden',
              ( ['out'], POINTER(c_int), 'CursorHidden' )),
]

IVMRAspectRatioControl._methods_ = [
    COMMETHOD([], HRESULT, 'GetAspectRatioMode',
              ( ['out'], POINTER(_VMR_ASPECT_RATIO_MODE), 'lpdwARMode' )),
    COMMETHOD([], HRESULT, 'SetAspectRatioMode',
              ( ['in'], _VMR_ASPECT_RATIO_MODE, 'dwARMode' )),
]

IVMRAspectRatioControl9._methods_ = [
	COMMETHOD([], HRESULT, 'GetAspectRatioMode',
			(['retval', 'out'], POINTER(DWORD), 'lpdwARMode')),
	COMMETHOD([], HRESULT, 'SetAspectRatioMode',
			(['in'], DWORD, 'dwARMode')),
]

IVMRFilterConfig._methods_ = [
    COMMETHOD([], HRESULT, 'SetImageCompositor',
              ( ['in'], POINTER(IVMRImageCompositor), 'lpVMRImgCompositor' )),
    COMMETHOD([], HRESULT, 'SetNumberOfStreams',
              ( ['in'], c_ulong, 'dwMaxStreams' )),
    COMMETHOD([], HRESULT, 'GetNumberOfStreams',
              ( ['out'], POINTER(c_ulong), 'pdwMaxStreams' )),
    COMMETHOD([], HRESULT, 'SetRenderingPrefs',
              ( ['in'], c_ulong, 'dwRenderFlags' )),
    COMMETHOD([], HRESULT, 'GetRenderingPrefs',
              ( ['out'], POINTER(c_ulong), 'pdwRenderFlags' )),
    COMMETHOD([], HRESULT, 'SetRenderingMode',
              ( ['in'], c_ulong, 'mode' )),
    COMMETHOD([], HRESULT, 'GetRenderingMode',
              ( ['out'], POINTER(c_ulong), 'pMode' )),
]

IVMRFilterConfig9._methods_ = [
    COMMETHOD([], HRESULT, 'SetImageCompositor',
              ( ['in'], c_void_p, 'lpVMRImgCompositor' )),
    COMMETHOD([], HRESULT, 'SetNumberOfStreams',
              ( ['in'], DWORD, 'dwMaxStreams' )),
    COMMETHOD([], HRESULT, 'GetNumberOfStreams',
              ( ['out'], POINTER(DWORD), 'pdwMaxStreams' )),
    COMMETHOD([], HRESULT, 'SetRenderingPrefs',
              ( ['in'], DWORD, 'dwRenderFlags' )),
    COMMETHOD([], HRESULT, 'GetRenderingPrefs',
              ( ['out'], POINTER(DWORD), 'pdwRenderFlags' )),
    COMMETHOD([], HRESULT, 'SetRenderingMode',
              ( ['in'], DWORD, 'Mode' )),
    COMMETHOD([], HRESULT, 'GetRenderingMode',
              ( ['out'], POINTER(DWORD), 'pMode' )),
]

# IVMRImageCompositor
IVMRImageCompositor._methods_ = [
    COMMETHOD([], HRESULT, 'InitCompositionTarget',
              ( ['in'], POINTER(IUnknown), 'pD3DDevice' ),
              ( ['in'], POINTER(c_ulong), 'pddsRenderTarget' )),
    COMMETHOD([], HRESULT, 'TermCompositionTarget',
              ( ['in'], POINTER(IUnknown), 'pD3DDevice' ),
              ( ['in'], POINTER(c_ulong), 'pddsRenderTarget' )),
    COMMETHOD([], HRESULT, 'SetStreamMediaType',
              ( ['in'], c_ulong, 'dwStrmID' ),
              ( ['in'], POINTER(_AMMediaType), 'pmt' ),
              ( ['in'], c_int, 'fTexture' )),
    COMMETHOD([], HRESULT, 'CompositeImage',
              ( ['in'], POINTER(IUnknown), 'pD3DDevice' ),
              ( ['in'], POINTER(c_ulong), 'pddsRenderTarget' ),
              ( ['in'], POINTER(_AMMediaType), 'pmtRenderTarget' ),
              ( ['in'], c_longlong, 'rtStart' ),
              ( ['in'], c_longlong, 'rtEnd' ),
              ( ['in'], c_ulong, 'dwClrBkGnd' ),
              ( ['in'], POINTER(_VMRVIDEOSTREAMINFO), 'pVideoStreamInfo' ),
              ( ['in'], c_uint, 'cStreams' )),
]

IVMRMixerControl9._methods_ = [
	COMMETHOD([], HRESULT, 'SetAlpha',
			(['in'], DWORD, 'dwStreamID'),
			(['in'], FLOAT, 'Alpha')),
	COMMETHOD([], HRESULT, 'GetAlpha',
			(['in'], DWORD, 'dwStreamID'),
			(['out'], POINTER(FLOAT), 'pAlpha')),
	COMMETHOD([], HRESULT, 'SetZOrder',
			(['in'], DWORD, 'dwStreamID'),
			(['in'], DWORD, 'dwZ')),
	COMMETHOD([], HRESULT, 'GetZOrder',
			(['in'], DWORD, 'dwStreamID'),
			(['out'], POINTER(DWORD), 'pZ')),
	COMMETHOD([], HRESULT, 'SetOutputRect',
			(['in'], DWORD, 'dwStreamID'),
			(['in'], POINTER(VMR9NormalizedRect), 'pRect')),
	COMMETHOD([], HRESULT, 'GetOutputRect',
			(['in'], DWORD, 'dwStreamID'),
			(['in'], POINTER(VMR9NormalizedRect), 'pRect')),
	COMMETHOD([], HRESULT, 'SetBackgroundClr',
			(['in'], COLORREF, 'ClrBkg')),
	COMMETHOD([], HRESULT, 'GetBackgroundClr',
			(['in'], POINTER(COLORREF), 'lpClrBkg')),
	COMMETHOD([], HRESULT, 'SetMixingPrefs',
			(['in'], DWORD, 'dwMixerPrefs')),
	COMMETHOD([], HRESULT, 'GetMixingPrefs',
			(['out'], POINTER(DWORD), 'pdwMixerPrefs')),
	COMMETHOD([], HRESULT, 'SetProcAmpControl',
			(['in'], DWORD, 'dwStreamID'),
			(['in'], POINTER(VMR9ProcAmpControl), 'lpClrControl')),
	COMMETHOD([], HRESULT, 'GetProcAmpControl',
			(['in'], DWORD, 'dwStreamID'),
			(['in', 'out'], POINTER(VMR9ProcAmpControl), 'lpClrControl')),
	COMMETHOD([], HRESULT, 'GetProcAmpControlRange',
			(['in'], DWORD, 'dwStreamID'),
			(['in', 'out'], POINTER(VMR9ProcAmpControlRange), 'lpClrControl'))
]

IVMRWindowlessControl9._methods_ = [
    COMMETHOD([], HRESULT, 'GetNativeVideoSize',
              ( ['out'], POINTER(LONG), 'lpWidth' ),
              ( ['out'], POINTER(LONG), 'lpHeight' ),
              ( ['out'], POINTER(LONG), 'lpARWidth' ),
              ( ['out'], POINTER(LONG), 'lpARHeight' )),
    COMMETHOD([], HRESULT, 'GetMinIdealVideoSize',
              ( ['out'], POINTER(LONG), 'lpWidth' ),
              ( ['out'], POINTER(LONG), 'lpHeight' )),
    COMMETHOD([], HRESULT, 'GetMaxIdealVideoSize',
              ( ['out'], POINTER(LONG), 'lpWidth' ),
              ( ['out'], POINTER(LONG), 'lpHeight' )),
    COMMETHOD([], HRESULT, 'SetVideoPosition',
              ( ['in'], POINTER(RECT), 'lpSRCRect' ),
              ( ['in'], POINTER(RECT), 'lpDSTRect' )),
    COMMETHOD([], HRESULT, 'GetVideoPosition',
              ( ['out'], POINTER(RECT), 'lpSRCRect' ),
              ( ['out'], POINTER(RECT), 'lpDSTRect' )),
    COMMETHOD([], HRESULT, 'GetAspectRatioMode',
              ( ['out'], POINTER(DWORD), 'lpAspectRatioMode' )),
    COMMETHOD([], HRESULT, 'SetAspectRatioMode',
              ( ['in'], DWORD, 'AspectRatioMode' )),
    COMMETHOD([], HRESULT, 'SetVideoClippingWindow',
              ( ['in'], HWND, 'hwnd' )),
    COMMETHOD([], HRESULT, 'RepaintVideo',
              ( ['in'], HWND, 'hwnd' ),
              ( ['in'], HDC, 'hdc' )),
    COMMETHOD([], HRESULT, 'DisplayModeChanged'),
    COMMETHOD([], HRESULT, 'GetCurrentImage',
              #( ['in'], POINTER(POINTER(BYTE)), 'lpDib' )),
              ( ['out'], POINTER(LPBYTE), 'lpDib' )),
    COMMETHOD([], HRESULT, 'SetBorderColor',
              ( ['in'], COLORREF, 'Clr' )),
    COMMETHOD([], HRESULT, 'GetBorderColor',
              ( ['out'], POINTER(COLORREF), 'lpClr' )),
]

class IMFVideoProcessor(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{6AB0000C-FECE-4d1f-A2AC-A9573530656E}')
    _idlflags_ = []

IMFVideoProcessor._methods_ = [

    COMMETHOD([], HRESULT, 'GetAvailableVideoProcessorModes',
              ( ['in'], POINTER(UINT), 'lpdwNumProcessingModes' ),
              ( ['out'], POINTER(POINTER(GUID)), 'ppVideoProcessingModes' )),

    COMMETHOD([], HRESULT, 'GetVideoProcessorCaps',
              ( ['in'], POINTER(GUID), 'lpVideoProcessorMode' ),
              ( ['out'], POINTER(LPVOID), 'lpVideoProcessorCaps' )),

    COMMETHOD([], HRESULT, 'GetVideoProcessorMode',
              ( ['out'], POINTER(GUID), 'lpMode' )),

    COMMETHOD([], HRESULT, 'SetVideoProcessorMode',
              ( ['in'], POINTER(GUID), 'lpMode' )),

    COMMETHOD([], HRESULT, 'GetProcAmpRange',
              ( ['in'], DWORD, 'dwProperty' ),
              ( ['out'], POINTER(DXVA2_ValueRange), 'pPropRange' )),

    COMMETHOD([], HRESULT, 'GetProcAmpValues',
              ( ['in'], DWORD, 'dwFlags' ),
              ( ['out'], POINTER(DXVA2_ProcAmpValues), 'Values' )),

    COMMETHOD([], HRESULT, 'SetProcAmpValues',
              ( ['in'], DWORD, 'dwFlags' ),
              ( ['in'], POINTER(DXVA2_ProcAmpValues), 'pValues' )),
    # ...
]

class IMFGetService(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{fa993888-4383-415a-a930-dd472a8cf6f7}')
    _idlflags_ = []

IMFGetService._methods_ = [
    COMMETHOD([], HRESULT, 'GetService',
              ( ['in'], GUID, 'guidService' ),
              ( ['in'], GUID, 'riid' ),
              ( ['out'], POINTER(POINTER(IMFVideoProcessor)), 'ppvObject' )),
]

class IBassSource2(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{6295DA1C-BE2B-4D8B-9A31-CF811EAADA4B}')
    _idlflags_ = []

IBassSource2._methods_ = [
    COMMETHOD([], HRESULT, 'SetSoundfont',
              ( ['in'], LPCWSTR, 'pSFont' )),
]
