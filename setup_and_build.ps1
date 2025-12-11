$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "TradeSensei AI - Complete Setup & Build Script" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if dotnet is installed
Write-Host "[1/4] Checking .NET SDK..." -ForegroundColor Yellow

$dotnetFound = $false

try {
    $dotnetVersion = & dotnet --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK .NET SDK found: $dotnetVersion" -ForegroundColor Green
        $dotnetFound = $true
    }
} catch {
    # dotnet not in PATH
}

if (-not $dotnetFound) {
    Write-Host "INFO .NET SDK not found, will attempt to install" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Downloading .NET 6 SDK installer..." -ForegroundColor Cyan
    $installerUrl = "https://dot.net/v1/dotnet-install.ps1"
    $installerPath = "$env:TEMP\dotnet-install.ps1"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "OK Installer downloaded" -ForegroundColor Green
        
        Write-Host "Running installer (this may take 2-5 minutes)..." -ForegroundColor Cyan
        & powershell.exe -ExecutionPolicy Bypass -File $installerPath -Channel 6.0 -InstallDir "$env:ProgramFiles\dotnet"
        
        $env:PATH = "$env:ProgramFiles\dotnet;$env:PATH"
        
        Write-Host "OK .NET SDK installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR Failed to install .NET SDK: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "[2/4] Navigating to project directory..." -ForegroundColor Yellow

$projectDir = "C:\Users\ISREAL\Desktop\trade master ai\TradeSenseiAI\src\csharp_ui"
if (-not (Test-Path $projectDir)) {
    Write-Host "ERROR Project directory not found: $projectDir" -ForegroundColor Red
    exit 1
}

Push-Location $projectDir
Write-Host "OK Working directory: $projectDir" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Restoring NuGet packages..." -ForegroundColor Yellow

try {
    & dotnet restore
    Write-Host "OK Packages restored" -ForegroundColor Green
} catch {
    Write-Host "ERROR Restore failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[4/4] Building application (Release mode)..." -ForegroundColor Yellow

try {
    & dotnet build --configuration Release
    Write-Host "OK Build successful" -ForegroundColor Green
} catch {
    Write-Host "ERROR Build failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "Executable location:" -ForegroundColor Cyan
Write-Host "$projectDir\bin\Release\net6.0-windows\TradeSensei.UI.exe" -ForegroundColor Yellow
Write-Host ""
