@echo off
cd /d "%~dp0"
regsvr32.exe /s LAVSplitter.ax
rundll32.exe LAVSplitter.ax,OpenConfiguration
regsvr32.exe /s /u LAVSplitter.ax
