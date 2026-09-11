@echo off
cd /d "%~dp0"

reg query HKCR\CLSID | find /i "{71F080AA-8661-4093-B15E-4F6903E77D0A}" > nul
if %errorlevel% EQU 0 (
	rundll32.exe MpcVideoRenderer.ax,OpenConfiguration
	exit /b
)

whoami /groups | find "S-1-16-12288" > nul
if %errorlevel% NEQ 0 (
	start /min powershell start -verb runas '%0'
	exit /b
)

regsvr32.exe /s MpcVideoRenderer.ax
rundll32.exe MpcVideoRenderer.ax,OpenConfiguration
regsvr32.exe /s /u MpcVideoRenderer.ax
