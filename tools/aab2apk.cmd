@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM =========================================
REM Resolve script directory (PATH-safe)
REM =========================================
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM =========================================
REM Tools
REM =========================================
set BUNDLETOOL=%SCRIPT_DIR%\bundletool-all.jar
set UBER_SIGNER=%SCRIPT_DIR%\uber-apk-signer.jar

REM =========================================
REM Input validation
REM =========================================
if "%~1"=="" (
    echo Usage: aab2apk app.aab
    exit /b 1
)

set AAB_FILE=%~f1
set AAB_DIR=%~dp1
set BASENAME=%~n1

if not exist "%AAB_FILE%" (
    echo ERROR: AAB file not found
    exit /b 1
)

if not exist "%BUNDLETOOL%" (
    echo ERROR: bundletool not found
    exit /b 1
)

if not exist "%UBER_SIGNER%" (
    echo ERROR: uber-apk-signer not found
    exit /b 1
)

REM =========================================
REM Work in input directory
REM =========================================
pushd "%AAB_DIR%"

REM =========================================
REM Build universal APK (unsigned)
REM =========================================
echo Building universal APK (unsigned)...

java -jar "%BUNDLETOOL%" build-apks ^
  --bundle="%AAB_FILE%" ^
  --output="%BASENAME%.apks" ^
  --mode=universal

if errorlevel 1 (
    echo ERROR: bundletool failed
    popd
    exit /b 1
)

REM =========================================
REM Extract universal.apk
REM =========================================
echo Extracting universal.apk...

tar -xf "%BASENAME%.apks"

if not exist "universal.apk" (
    echo ERROR: universal.apk not found
    popd
    exit /b 1
)

REM =========================================
REM Sign APK (Uber APK Signer)
REM =========================================
echo Signing APK with Uber APK Signer...

java -jar "%UBER_SIGNER%" -a "universal.apk" --overwrite

if errorlevel 1 (
    echo ERROR: APK signing failed
    popd
    exit /b 1
)

REM =========================================
REM Finalize output
REM =========================================
rename "universal.apk" "%BASENAME%-signed.apk"

REM Cleanup
del "%BASENAME%.apks" >nul 2>&1
del "%BASENAME%.apks.idsig" >nul 2>&1
del "universal.apk.idsig" >nul 2>&1
del "toc.pb" >nul 2>&1
rmdir /s /q META-INF >nul 2>&1

echo.
echo SUCCESS
echo Output APK:
echo %AAB_DIR%%BASENAME%-signed.apk
echo.

popd
endlocal
