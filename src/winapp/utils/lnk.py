''' Minimal script for handling .LNK files in Windows '''

__all__ = ["get_lnk_infos"]

from ..comtypes import GUID, CreateObject,  COMMETHOD, HRESULT, BSTR, POINTER
from ..comtypes.automation import IDispatch

from ctypes.wintypes import INT, LPINT

class IWshShell(IDispatch):
    """Shell Object Interface"""
    _case_insensitive_ = True
    _iid_ = GUID('{F935DC21-1CF0-11D0-ADB9-00C04FD58A0B}')
    _idlflags_ = ['hidden', 'dual', 'oleautomation']

class IWshShortcut(IDispatch):
    """Shortcut Object"""
    _case_insensitive_ = True
    _iid_ = GUID('{F935DC23-1CF0-11D0-ADB9-00C04FD58A0B}')
    _idlflags_ = ['dual', 'oleautomation']

IWshShell._methods_ = [COMMETHOD([], HRESULT, '_')] * 4 + [
    COMMETHOD([], HRESULT, 'CreateShortcut',
        (['in'], BSTR, 'PathLink'),
        (['out', 'retval'], POINTER(POINTER(IDispatch)), 'Shortcut')
    ),
]

#IWshShortcut._methods_ = [COMMETHOD([], HRESULT, '_')] * 10 + [
#    COMMETHOD(['propget'], HRESULT, 'TargetPath', (['out', 'retval'], POINTER(BSTR), 'out_Path')),
#]

IWshShortcut._methods_ = [
    COMMETHOD(['propget'], HRESULT, 'FullName', (['out', 'retval'], POINTER(BSTR), 'name')),

    COMMETHOD(['propget'], HRESULT, 'Arguments', (['out', 'retval'], POINTER(BSTR), 'Arguments')),
    COMMETHOD(['propput'], HRESULT, 'Arguments', (['in'], BSTR, 'Arguments')),

    COMMETHOD(['propget'], HRESULT, 'Description', (['out', 'retval'], POINTER(BSTR), 'Description')),
    COMMETHOD(['propput'], HRESULT, 'Description', (['in'], BSTR, 'Description')),

    COMMETHOD(['propget'], HRESULT, 'Hotkey', (['out', 'retval'], POINTER(BSTR), 'HotKey')),
    COMMETHOD(['propput'], HRESULT, 'Hotkey', (['in'], BSTR, 'HotKey')),

    COMMETHOD(['propget'], HRESULT, 'IconLocation', (['out', 'retval'], POINTER(BSTR), 'IconPath')),
    COMMETHOD(['propput'], HRESULT, 'IconLocation', (['in'], BSTR, 'IconPath')),

    COMMETHOD(['propput'], HRESULT, 'RelativePath', (['in'], BSTR, 'rhs')),

    COMMETHOD(['propget'], HRESULT, 'TargetPath', (['out', 'retval'], POINTER(BSTR), 'Path')),
    COMMETHOD(['propput'], HRESULT, 'TargetPath', (['in'], BSTR, 'Path')),

    COMMETHOD(['propget'], HRESULT, 'WindowStyle', (['out', 'retval'], LPINT, 'ShowCmd')),
    COMMETHOD(['propput'], HRESULT, 'WindowStyle', (['in'], INT, 'ShowCmd')),

    COMMETHOD(['propget'], HRESULT, 'WorkingDirectory', (['out', 'retval'], POINTER(BSTR), 'WorkingDirectory')),
    COMMETHOD(['propput'], HRESULT, 'WorkingDirectory', (['in'], BSTR, 'WorkingDirectory')),

    COMMETHOD(['hidden'], HRESULT, 'Load', (['in'], BSTR, 'PathLink')),

    COMMETHOD([], HRESULT, 'Save'),
]

########################################
#
########################################
def get_lnk_infos(lnk_path):
    shortcut = CreateObject("WScript.Shell", interface=IWshShell).CreateShortCut(lnk_path)
    iws = shortcut.QueryInterface(IWshShortcut)
    return iws.TargetPath, iws.Arguments, iws.IconLocation  # icon index, NOT id
