@echo off
cd /d "%~dp0"

reg query HKCR\CLSID | find /i "{EE30215D-164F-4A92-A4EB-9D4C13390F9F}" > nul
if %errorlevel% EQU 0 (
	rundll32.exe LAVVideo.ax,OpenConfiguration
	exit /b
)

whoami /groups | find "S-1-16-12288" > nul
if %errorlevel% NEQ 0 (
	start /min powershell start -verb runas '%0'
	exit /b
)

regsvr32.exe /s LAVVideo.ax
rundll32.exe LAVVideo.ax,OpenConfiguration
regsvr32.exe /s /u LAVVideo.ax
