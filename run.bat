@echo off
REM ---------------------------------------------------------------
REM  Fake Data Prevention with Conventional Cryptotools
REM  Project: SEC-PRJ-7E_25
REM
REM  How to use:
REM    Double-click this file, or open a terminal in this folder
REM    and type:   run
REM
REM  What it does:
REM    1. Finds a Python 3.8+ installation on this machine.
REM    2. Installs Flask and cryptography if missing.
REM    3. Starts the Flask web server on http://127.0.0.1:5000/
REM    4. Opens the page in the default browser.
REM    Press Ctrl+C in this window to stop the server.
REM ---------------------------------------------------------------

setlocal
cd /d "%~dp0"

echo.
echo  Fake Data Prevention with Conventional Cryptotools  (SEC-PRJ-7E_25)
echo  ---------------------------------------------------------------

REM --- Find a Python 3.8+ interpreter -------------------------------
REM Try the Python launcher first (py -3) because it lets us request a
REM minimum version explicitly. Then fall back to plain "python" /
REM "python3", checking the version of each one before using it.
set "PY="

py -3 --version >nul 2>&1
if not errorlevel 1 (
  for /f "tokens=*" %%v in ('py -3 -c "import sys; print(1 if sys.version_info>=(3,8) else 0)" 2^>nul') do (
    if "%%v"=="1" set "PY=py -3"
  )
)

if not defined PY (
  for %%C in (python python3) do (
    if not defined PY (
      %%C --version >nul 2>&1
      if not errorlevel 1 (
        for /f "tokens=*" %%v in ('%%C -c "import sys; print(1 if sys.version_info>=(3,8) else 0)" 2^>nul') do (
          if "%%v"=="1" set "PY=%%C"
        )
      )
    )
  )
)

if not defined PY (
  echo.
  echo  ERROR: a Python 3.8 or newer installation is required.
  echo.
  echo  Please install Python 3.10+ from https://www.python.org/downloads/
  echo  and make sure to tick "Add Python to PATH" during installation.
  echo  Then double-click run.bat again.
  echo.
  pause
  exit /b 1
)

echo  Using Python: %PY%
for /f "tokens=*" %%v in ('%PY% --version 2^>^&1') do echo  Version:      %%v

REM --- Install dependencies (silent if already installed) -----------
REM We try a normal install first. If that fails with a permission
REM error (locked global site-packages, no admin rights, antivirus
REM holding a file open, etc.) we retry with --user, which installs
REM into the current user's own folder and never needs admin.
echo  Checking dependencies (flask, cryptography) ...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo  Standard install failed. Retrying with --user ...
  %PY% -m pip install --quiet --disable-pip-version-check --user -r requirements.txt
  if errorlevel 1 (
    echo.
    echo  ERROR: failed to install Python dependencies.
    echo  Try running, in this folder, one of:
    echo      %PY% -m pip install --user -r requirements.txt
    echo      %PY% -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
  )
)

REM --- Open the browser shortly after the server starts -------------
start "" /b cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5000/"

REM --- Run the server in the foreground -----------------------------
echo  Starting server on http://127.0.0.1:5000/  (press Ctrl+C to stop)
echo.
%PY% app.py

endlocal
