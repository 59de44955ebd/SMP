@echo off
cd /d "%~dp0"
regsvr32.exe /s LAVAudio.ax
rundll32.exe LAVAudio.ax,OpenConfiguration
regsvr32.exe /s /u LAVAudio.ax
