@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 (
    python -X utf8 -B -S "%~dp0start.py" %*
    goto finished
)
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 (
    py -3 -X utf8 -B -S "%~dp0start.py" %*
    goto finished
)
echo Python 3.10 or newer is required. Install Python and run START.cmd again.
pause
exit /b 1
:finished
set "AIDD_START_EXIT=%ERRORLEVEL%"
pause
exit /b %AIDD_START_EXIT%
