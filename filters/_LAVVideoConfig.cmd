@echo off
cd /d "%~dp0"
regsvr32.exe /s LAVVideo.ax
rundll32.exe LAVVideo.ax,OpenConfiguration
regsvr32.exe /s /u LAVVideo.ax
