@echo off
REM Build script for Lazy Comments: PyInstaller + Inno Setup.
REM
REM Builds in %TEMP%\Lazy CommentsBuild because PyInstaller fails on paths with non-ASCII
REM characters (this project's source folder contains Cyrillic).
REM
REM Result: lazy_comments-setup.exe is copied next to this script.

setlocal EnableDelayedExpansion

set "SRC=%~dp0"
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"
set "BUILDDIR=%TEMP%\Lazy CommentsBuild"

REM --- Locate ISCC ---------------------------------------------------------
REM Honor an explicit ISCC env var; otherwise probe common install locations.
if defined ISCC if exist "%ISCC%" goto :iscc_found
for %%P in (
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
) do (
    if exist "%%~P" (
        set "ISCC=%%~P"
        goto :iscc_found
    )
)
where iscc.exe >nul 2>&1 && for /f "delims=" %%P in ('where iscc.exe') do (
    set "ISCC=%%P"
    goto :iscc_found
)
echo [ERROR] Inno Setup compiler (ISCC.exe) not found.
echo         Install Inno Setup 6 from https://jrsoftware.org/isdl.php
echo         Or set the ISCC env var to ISCC.exe path.
exit /b 1
:iscc_found

echo ============================================
echo  Lazy Comments build
echo ============================================
echo  Source:    %SRC%
echo  Build dir: %BUILDDIR%
echo  ISCC:      %ISCC%
echo ============================================
echo.

REM --- Sanity checks --------------------------------------------------------
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pyinstaller not found in PATH.
    echo         Install with: pip install -r requirements.txt pyinstaller
    exit /b 1
)

REM --- Reset build dir ------------------------------------------------------
if exist "%BUILDDIR%" (
    echo [1/4] Cleaning %BUILDDIR% ...
    rmdir /s /q "%BUILDDIR%"
)
mkdir "%BUILDDIR%" || (echo [ERROR] Cannot create %BUILDDIR% & exit /b 1)

REM --- Stage sources --------------------------------------------------------
echo [2/4] Staging sources ...
copy /y "%SRC%\lazy_comments.py"   "%BUILDDIR%\" >nul || (echo [ERROR] copy lazy_comments.py & exit /b 1)
copy /y "%SRC%\lazy_comments.ico"  "%BUILDDIR%\" >nul || (echo [ERROR] copy lazy_comments.ico & exit /b 1)
copy /y "%SRC%\lazy_comments.iss"  "%BUILDDIR%\" >nul || (echo [ERROR] copy lazy_comments.iss & exit /b 1)
copy /y "%SRC%\lazy_comments.spec" "%BUILDDIR%\" >nul || (echo [ERROR] copy lazy_comments.spec & exit /b 1)
xcopy /e /i /y /q "%SRC%\lazy_commentsapp" "%BUILDDIR%\lazy_commentsapp" >nul || (echo [ERROR] copy lazy_commentsapp & exit /b 1)

REM --- PyInstaller ----------------------------------------------------------
echo [3/4] Running PyInstaller ...
pushd "%BUILDDIR%"
pyinstaller --noconfirm lazy_comments.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller failed.
    popd
    exit /b 1
)
popd

REM --- Inno Setup -----------------------------------------------------------
echo [4/4] Running Inno Setup ...
"%ISCC%" "%BUILDDIR%\lazy_comments.iss"
if errorlevel 1 (
    echo [ERROR] Inno Setup failed.
    exit /b 1
)

REM --- Copy artifact back ---------------------------------------------------
copy /y "%BUILDDIR%\installer\lazy_comments-setup.exe" "%SRC%\lazy_comments-setup.exe" >nul || (
    echo [ERROR] Cannot copy lazy_comments-setup.exe back to project.
    exit /b 1
)

echo.
echo ============================================
echo  Build OK
echo ============================================
for %%I in ("%SRC%\lazy_comments-setup.exe") do echo   %%~fI  ^(%%~zI bytes^)
echo.
echo  Build dir kept at: %BUILDDIR%
echo  Run "rmdir /s /q %%TEMP%%\Lazy CommentsBuild" to clean.
echo ============================================

endlocal
exit /b 0
