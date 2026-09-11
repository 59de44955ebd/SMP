@echo off
cd /d "%~dp0"

reg query HKCR\CLSID | find /i "{B98D13E7-55DB-4385-A33D-09FD1BA26338}" > nul
if %errorlevel% EQU 0 (
	rundll32.exe LAVSplitter.ax,OpenConfiguration
	exit /b
)

whoami /groups | find "S-1-16-12288" > nul
if %errorlevel% NEQ 0 (
	start /min powershell start -verb runas '%0'
	exit /b
)

regsvr32.exe /s LAVSplitter.ax
rundll32.exe LAVSplitter.ax,OpenConfiguration
regsvr32.exe /s /u LAVSplitter.ax
