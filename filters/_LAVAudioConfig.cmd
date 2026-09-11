@echo off
cd /d "%~dp0"

reg query HKCR\CLSID | find /i "{E8E73B6B-4CB3-44A4-BE99-4F7BCB96E491}" > nul
if %errorlevel% EQU 0 (
	rundll32.exe LAVAudio.ax,OpenConfiguration
	exit /b
)

whoami /groups | find "S-1-16-12288" > nul
if %errorlevel% NEQ 0 (
	start /min powershell start -verb runas '%0'
	exit /b
)

regsvr32.exe /s LAVAudio.ax
rundll32.exe LAVAudio.ax,OpenConfiguration
regsvr32.exe /s /u LAVAudio.ax
