@echo off
REM Setup script: Install .NET 6 SDK and build TradeSensei WPF app

echo.
echo ================================================
echo TradeSensei AI - Setup & Build Script
echo ================================================
echo.

REM Check if dotnet is already installed
where dotnet >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] .NET SDK already installed
    dotnet --version
    goto BUILD
)

echo [INFO] .NET SDK not found. Downloading...
echo.

REM Download .NET 6 SDK installer
echo Downloading .NET 6 SDK (this may take a few minutes)...
powershell -Command ^
  "if (-not (Test-Path 'C:\dotnet-install.exe')) { ^
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile 'dotnet-install.ps1'; ^
  }"

REM Run .NET installer
echo Installing .NET 6 SDK...
powershell -ExecutionPolicy Bypass -File dotnet-install.ps1 -Channel 6.0 -InstallDir "C:\Program Files\dotnet"

REM Add .NET to PATH for this session
set PATH=C:\Program Files\dotnet;%PATH%

echo.
echo [OK] .NET SDK installed
dotnet --version

:BUILD
echo.
echo ================================================
echo Building TradeSensei WPF Application
echo ================================================
echo.

cd /d "C:\Users\ISREAL\Desktop\trade master ai\TradeSenseiAI\src\csharp_ui"

echo [1/2] Restoring NuGet packages...
dotnet restore

echo.
echo [2/2] Building application...
dotnet build -c Release

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo The app is ready at:
    echo   bin\Release\net6.0-windows\TradeSensei.UI.exe
    echo.
    echo To run the app:
    echo   dotnet run
    echo.
    pause
) else (
    echo.
    echo ================================================
    echo BUILD FAILED
    echo ================================================
    echo.
    pause
)
