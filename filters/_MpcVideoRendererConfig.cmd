@echo off
cd /d "%~dp0"
regsvr32.exe /s MpcVideoRenderer.ax
rundll32.exe MpcVideoRenderer.ax,OpenConfiguration
regsvr32.exe /s /u MpcVideoRenderer.ax
