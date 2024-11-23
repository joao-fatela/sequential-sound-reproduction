@echo off
title Sequential audio reproduction

rem Configuration file name and directory
set CONFIG_FILE=config.ini
set CONFIG_DIR=.\lib\

rem Reading python path from configuration file
for /f "tokens=1,2 delims== " %%a in (%CONFIG_DIR%%CONFIG_FILE%) do (
	if %%a==python_path set PYTHON_PATH=%%b
)


if exist %PYTHON_PATH% (
	goto :realrun
) else (
	echo ERROR: '%PYTHON_PATH%' is not a valid path.
	echo Please write a valid path to python.exe in the configuration file lib/config.ini
	goto :endmessage
)

:realrun
rem force quiet dependency install
echo|set /p="Checking/installing dependencies..."
"%PYTHON_PATH%" -m pip install -q -r requirements.txt
echo. Done!

rem prompt user to define output device ID list
set /p YN="Set audio device ID list? (Y/[N]): "

rem default no
if [%YN%]==[] set YN=N

rem If yes, run script to write and prompt device list
set YY=false

if %YN%==Y set YY=true 
if %YN%==y set YY=true
if %YN%==yes set YY=true
if %YN%==Yes set YY=true
if %YN%==YES set YY=true
if %YY%==true ( 
	"%PYTHON_PATH%" ".\dev\write_device_list.py"	
)

echo.
rem Prompt user for audio signal / reproduction mode
set /p MODE="Choose audio routine [C]USTOM / [t]est: "

if [%MODE%]==[] set MODE=custom

rem Audio reproduction script with user audio mode flag
"%PYTHON_PATH%" ".\dev\Nspeakers.py" %MODE%
echo.
echo.Audio reproduction is finished. 

:endmessage
echo.Press any key to close window.
pause >nul