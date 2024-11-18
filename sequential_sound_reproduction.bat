@echo off
title run_experiment

rem Configuration file name and directory
set CONFIG_FILE=config.ini
set CONFIG_DIR=.\lib\

rem Reading python path from configuration file
for /f "tokens=1,2 delims== " %%a in (%CONFIG_DIR%%CONFIG_FILE%) do (
	if %%a==python_path set PYTHON_PATH=%%b
)

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
	"%PYTHON_PATH%python.exe" ".\dev\write_device_list.py"	
)

rem Prompt user for audio signal / reproduction mode
set /p MODE="Enter audio signal ([test], [w]hite, [p]ink, [b]rown, [a]ll): "

if [%MODE%]==[] set MODE=test

echo.   
echo.!READY FOR REPRODUCTION!
echo.Press any key to begin
pause >nul

rem Audio reproduction script with user audio mode flag
"%PYTHON_PATH%python.exe" ".\dev\Nspeakers.py" %MODE%

echo. Audio reproduction is finished. Press any key to close window.
pause >nul