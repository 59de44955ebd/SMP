# SMP (SimpleMediaPlayer)

![](screenshots/smp-win11-dark.png)

SMP is a simple desktop media player for Windows 11 x64 written in Python. What makes it special is that it supports 3 different multimedia engines (or multimedia frameworks) that a user can choose from. Note that changing the active engine restarts the current player instance.

The motivation for creating such a multi-engine media player was that the DirectShow [LAV Splitter Source](https://github.com/Nevcairiel/LAVFilters) filter (that also other media players like [MPC-HC](https://github.com/clsid2/mpc-hc) rely on and that usually does a great job) fails to play recent HLS live streams, e.g. provided by TV stations, that provide multiple separate audio streams. Having such a multi-engine player allows to play such streams with either the VLC or WebView engine, but everything else with DirectShow/LAV engine.

## MultiMedia Engines

### 1. DirectShow

DirectShow playback is based on [LAV Filters](https://github.com/Nevcairiel/LAVFilters) (which are in turn based on [FFmpeg](https://ffmpeg.org/)), [MPC Video Renderer](https://github.com/Aleksoid1978/VideoRenderer) and [VSFilter](https://github.com/v0lt/VSFilterBE) (DirectVobSub) for subtitles support.

All needed filters are included and loaded directly from .dll, no prior filter registration needed.

### 2. VLC

VLC playback is based on [libVLC](https://images.videolan.org/vlc/libvlc.html) and its Python binding [python-vlc](https://github.com/oaubert/python-vlc).

VLC binaries are not included, therefor by default VLC playback is only available if the [VLC media player](https://www.videolan.org/) for Windows is installed in the system. 

To activate independant VLC support, copy `libvlc.dll`, `libvlccore.dll` and folder `plugins` from a VLC media player installation folder into the `data` folder next to `SMP.exe` (and restart the player).

MIDI support depends on an external [SoundFont](https://en.wikipedia.org/wiki/SoundFont) file. To keep the download file size small, only a [rather small SoundFont](https://musical-artifacts.com/artifacts/5190) (based on GM.dls that comes with Windows) is included as file `soundbank.sf2` in the `data` folder. For achieving better MIDI sound quality you can replace this file with a high-end SoundFont file like e.g. [FluidR3_GM.sf2](https://musical-artifacts.com/artifacts/738) or [Reality_GMGS_falcomod.sf2](https://www.musical-artifacts.com/artifacts/6003). After downloading such a file, just rename it `soundbank.sf2` and put it into `data`.

### 3. WebView

WebView playback is based on [Microsoft Edge WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2) (based on recent Chrome/Chromium versions) which comes preinstalled with Windows 11.

MIDI support is based on the same `soundbank.sf2` as the VLC engine, so replacing this file would also increase the MIDI sound quality of the WebView engine.

WebView supports less features, container formats and codecs than DirectShow and VLC, but has the benefit of minimum extra file size, since WebView2 is already provides by the OS. If you only need support for common media formats/codecs, you could remove DirectShow support by deleting the `filters` folder (inside `data`), resulting in a media player with rather small file size.