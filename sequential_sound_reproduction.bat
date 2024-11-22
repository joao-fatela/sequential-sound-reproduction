@echo off
title run_experiment

rem Configuration file name and directory
set CONFIG_FILE=config.ini
set CONFIG_DIR=.\lib\

rem Reading python path from configuration file
for /f "tokens=1,2 delims== " %%a in (%CONFIG_DIR%%CONFIG_FILE%) do (
	if %%a==python_path set PYTHON_PATH=%%b
)

rem force dependency install
"%PYTHON_PATH%" "python -m pip install -q -r requirements.txt"

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
set /p MODE="Choose audio routine [T]EST / [c]ustom: "

if [%MODE%]==[] set MODE=test

rem Audio reproduction script with user audio mode flag
"%PYTHON_PATH%" ".\dev\Nspeakers.py" %MODE%
echo.
echo.Audio reproduction is finished. Press any key to close window.
pause >nul