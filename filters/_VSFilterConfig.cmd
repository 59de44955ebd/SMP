@echo off
cd /d "%~dp0"

reg query HKCR\CLSID | find /i "{9852A670-F845-491B-9BE6-EBD841B8A613}" > nul
if %errorlevel% EQU 0 (
	rundll32.exe VSFilter.ax,OpenConfiguration
	exit /b
)

whoami /groups | find "S-1-16-12288" > nul
if %errorlevel% NEQ 0 (
	start /min powershell start -verb runas '%0'
	exit /b
)

regsvr32.exe /s VSFilter.ax
rundll32.exe VSFilter.ax,OpenConfiguration
regsvr32.exe /s /u VSFilter.ax
