# SMP (SimpleMediaPlayer)

![](screenshots/smp-win11-dark.png)

SMP is a simple desktop media player for Windows 11 x64 written in Python. What makes it special is that it supports 3 different multimedia engines (or multimedia frameworks) that a user can choose from. Note that changing the active engine restarts the current player instance.

The motivation for creating such a multi-engine media player was that the DirectShow [LAV Splitter Source](https://github.com/Nevcairiel/LAVFilters) filter (that also other media players like [MPC-HC](https://github.com/clsid2/mpc-hc) rely on and that usually does a great job) fails to play recent HLS live streams, e.g. provided by TV stations, that provide multiple separate audio streams. Having such a multi-engine player allows to play such streams with either the VLC or WebView engine, but everything else with DirectShow/LAV engine.

## MultiMedia Engines

### 1. DirectShow

DirectShow playback is based on [LAV Filters](https://github.com/Nevcairiel/LAVFilters) (which are in turn based on [FFmpeg](https://ffmpeg.org/)) and [MPC Video Renderer](https://github.com/Aleksoid1978/VideoRenderer).

Subtitles support is based on [VSFilter](https://github.com/v0lt/VSFilterBE) (DirectVobSub). 
 
 MIDI files are played with [Bass Audio Source](https://github.com/v0lt/BassAudioSource) and [BASSMIDI](https://www.un4seen.com/doc/#bassmidi/bassmidi.html), which allows to use a high-end SoundFont as soundbank (see [MIDI Support](#midi-support) below).

All needed filters are included and loaded directly from .dll, no prior filter registration needed.

### 2. VLC

VLC playback is based on [libVLC](https://images.videolan.org/vlc/libvlc.html) and its Python binding [python-vlc](https://github.com/oaubert/python-vlc).

VLC binaries are not included, therefor by default VLC playback is only available if the [VLC media player](https://www.videolan.org/) for Windows is installed in the system. 

To activate independant VLC support, copy `libvlc.dll`, `libvlccore.dll` and folder `plugins` from a VLC media player 3.x (64 bit) installation folder into the `data` folder next to `SMP.exe` (and restart the player).

### 3. WebView

WebView playback uses [Microsoft Edge WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2), which is based on recent Chrome/Chromium versions and comes preinstalled with Windows 11.

MIDI support is based on [spessasynth_lib](https://github.com/spessasus/spessasynth_lib).

WebView supports less features, container formats and codecs than DirectShow and VLC, but has the benefit of minimum extra file size, since WebView2 is already provided by the OS. If you only need support for common media formats/codecs, you could remove DirectShow support by deleting the `filters` folder (inside `data`), resulting in a media player with rather small file size.

## MIDI Support

All 3 engines support playing MIDI files (.mid, .rmi), for which they use an external [SoundFont](https://en.wikipedia.org/wiki/SoundFont) file as soundbank. To keep the player's download file size small, only a [small SoundFont](https://musical-artifacts.com/artifacts/5190) (3 MB, based on GM.dls that comes with Windows) is included as file `soundbank.sf2` in the `data` folder. For achieving better MIDI sound quality you can replace this file with a high-end SoundFont file like e.g. [FluidR3_GM.sf2](https://musical-artifacts.com/artifacts/738) (141 MB) or [Reality_GMGS_falcomod.sf2](https://www.musical-artifacts.com/artifacts/6003) (34 MB). After downloading such a file, just rename it `soundbank.sf2` and put it into `data`.

If you happen to be a MIDI nerd, the WebView engine is the only one that supports the rather exotic but interesting [SF2 RMIDI](https://github.com/spessasus/sf2-rmidi-specification) file format that allows to combine MIDI and soundbank data in a single `.rmi` file.
