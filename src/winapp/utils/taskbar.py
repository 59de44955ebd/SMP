__all__ = ('TBPF', 'taskbar')
from ctypes import *
from winapp.comtypes import *

class TBPF:
    NOPROGRESS = 0
    INDETERMINATE = 1
    NORMAL = 2  # green
    ERROR = 4  # red
    PAUSED = 8  # yellow

class ITaskBarList3(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}')
    _idlflags_ = []

ITaskBarList3._methods_ = [COMMETHOD([], HRESULT, '_')] * 6 + [
    COMMETHOD([], HRESULT, 'SetProgressValue',
              ( ['in'], c_void_p, 'hwnd' ),
              ( ['in'], c_ulonglong, 'ullCompleted' ),
              ( ['in'], c_ulonglong, 'ullTotal' )),

    COMMETHOD([], HRESULT, 'SetProgressState',
              ( ['in'], c_void_p, 'hwnd' ),
              ( ['in'], c_int, 'tbpFlags' )),
]

CLSID_TaskbarList = "{56FDF344-FD6D-11d0-958A-006097C9A090}"

taskbar = CoCreateInstance(GUID(CLSID_TaskbarList), ITaskBarList3, clsctx=CLSCTX_INPROC_SERVER)
