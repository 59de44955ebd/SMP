@echo off
cd /d "%~dp0"
regsvr32.exe /s VSFilter.ax
rundll32.exe VSFilter.ax,OpenConfiguration
regsvr32.exe /s /u VSFilter.ax
