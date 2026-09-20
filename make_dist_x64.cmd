@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0

:: config
set "APP_NAME=SMP"
set ICON=NONE
set DIR=%CD%
set APP_DIR=%CD%\dist\%APP_NAME%\
set DATA_DIR=data

call :cleanup
call :check_requirements
call :run_pyinstaller
call :copy_resources
call :optimize
call :create_7z
call :create_installer

echo.
echo ****************************************
echo Done.
echo ****************************************
echo.
pause

endlocal
goto :eof


:cleanup
mkdir dist 2>nul
rmdir /s /q "dist\%APP_NAME%" 2>nul
del "dist\%APP_NAME%-x64-portable.7z" 2>nul
del "dist\%APP_NAME%-x64-setup.exe" 2>nul
exit /B


:check_requirements
echo.
echo ****************************************
echo Checking requirements...
echo ****************************************
pip install -r requirements.txt
exit /B


:run_pyinstaller
echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************
REM "Compile" winapp contants and functions
cd src
python _compile_const.py
python _compile_dlls.py
ren winapp\const.py __const.py
ren winapp\const_c.py const.py
ren winapp\dlls.py __dlls.py
ren winapp\dlls_c.py dlls.py
cd ..

set PYTHONPATH=src
pyinstaller --noupx -w -n "%APP_NAME%" -i %ICON% -r "resources.dll" -D "src/main.py" --contents-directory %DATA_DIR% --hidden-import dshow_player --hidden-import mpv_player --hidden-import vlc_player  --hidden-import webview2_player

ren src\winapp\const.py const_c.py
ren src\winapp\__const.py const.py
ren src\winapp\dlls.py dlls_c.py
ren src\winapp\__dlls.py dlls.py
exit /B


:copy_resources
echo.
echo ****************************************
echo Copying resources...
echo ****************************************
copy "src\webview2\native\win-amd64\loader.dll" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\index.htm" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\soundbank.sf2" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\spessasynth_core.js" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\spessasynth_lib.js" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\spessasynth_processor.min.js" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\srt.js" "dist\%APP_NAME%\%DATA_DIR%\"
copy "resources\stb-vorbis.js" "dist\%APP_NAME%\%DATA_DIR%\"
exit /B


:optimize
echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************
rd /q /s "dist\%APP_NAME%\%DATA_DIR%\pymediainfo-7.0.1.dist-info"
del /q "dist\%APP_NAME%\%DATA_DIR%\api-ms-win-*.dll"
del "dist\%APP_NAME%\%DATA_DIR%\VCRUNTIME140.dll"
del "dist\%APP_NAME%\%DATA_DIR%\VCRUNTIME140_1.dll"
del "dist\%APP_NAME%\%DATA_DIR%\ucrtbase.dll"
del "dist\%APP_NAME%\%DATA_DIR%\_bz2.pyd"
del "dist\%APP_NAME%\%DATA_DIR%\_lzma.pyd"
exit /B


:create_7z
if not exist "C:\Program Files\7-Zip\" (
	echo.
	echo ****************************************
	echo 7z.exe not found at default location, omitting .7z creation...
	echo ****************************************
	exit /B
)
echo.
echo ****************************************
echo Creating .7z archive...
echo ****************************************
cd dist
set PATH=C:\Program Files\7-Zip;%PATH%
7z a "%APP_NAME%-x64-portable.7z" "%APP_NAME%\*"
cd ..
exit /B


:create_installer
if not exist "C:\Program Files (x86)\NSIS\" (
	echo.
	echo ****************************************
	echo NSIS not found at default location, omitting installer creation...
	echo ****************************************
	exit /B
)
echo.
echo ****************************************
echo Creating installer...
echo ****************************************
set PATH=C:\Program Files (x86)\NSIS;%PATH%
makensis make-installer.nsi
exit /B
