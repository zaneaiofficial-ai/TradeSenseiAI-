# TradeSensei AI - Installation Guide

## System Requirements

- **Windows 10 or later** (x64)
- **Processor**: Intel/AMD x64 processor (1.4 GHz or faster)
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Disk Space**: 500 MB free space
- **Internet Connection**: Required for backend connectivity

## Download

Download the latest version: **TradeSenseiAI-Setup.exe**

Current Version: 1.0.0 (December 2025)

## Installation Steps

### Method 1: Automated Installer (Recommended)

1. **Download the installer**
   - Download `TradeSenseiAI-Setup.exe` from the releases page

2. **Run the installer**
   - Double-click `TradeSenseiAI-Setup.exe`
   - Click "Next" on the welcome screen

3. **Accept License**
   - Read the license agreement
   - Click "I Agree"

4. **Choose Installation Folder**
   - Default: `C:\Program Files\TradeSensei AI`
   - Click "Install" to proceed

5. **Wait for Installation**
   - The installer will copy all files (this takes 1-2 minutes)
   - Click "Finish" when complete

6. **Launch the Application**
   - Shortcuts created on Desktop and Start Menu
   - Double-click the "TradeSensei AI" shortcut to launch

### Method 2: Manual Installation

1. **Extract Files**
   - Download the release zip file
   - Extract to your desired location (e.g., `C:\TradeSensei AI`)

2. **Run the Application**
   - Navigate to the extracted folder
   - Double-click `TradeSensei.UI.exe`

3. **Create Shortcuts (Optional)**
   - Right-click `TradeSensei.UI.exe`
   - Send To → Desktop (create shortcut)

## First Launch Configuration

### 1. API Configuration

**Backend URL**:
- The app connects to: `https://tradesenseiai-production.up.railway.app`
- This is pre-configured in `App.config`

### 2. User Authentication

- Click **"Login"** button on main dashboard
- Sign in or create a new account
- Choose your subscription tier (Free/Pro/Master)

### 3. API Keys (Optional - For Advanced Features)

Go to **Settings** and enter:
- **OpenAI API Key** (for custom mentor AI)
- **ElevenLabs API Key** (for custom voice synthesis)

These are optional; default values are provided.

## Features Overview

### 🎤 Voice Chat
- Click "🎤 Voice Chat" on the main dashboard
- Hold the microphone button to record your question
- AI mentor will respond with trading advice

### 📊 Price Alerts
- Click "📊 Price Alerts" to set price alerts
- Create alerts for cryptocurrencies and forex pairs
- Get notified when prices hit your targets

### 💼 Portfolio
- Click "💼 Portfolio" to track your trades
- Add open positions with entry price, SL, TP
- Track P&L and win rate statistics

### 🎥 Overlay & Streaming
- **Open Overlay**: Real-time chart analysis with desktop capture
- **Start Streaming**: Stream your analysis to OBS for content creation
- **Start Webcam**: Integrate webcam vision into your trading

## Uninstallation

### Method 1: Automated Uninstaller
1. Go to **Control Panel** → **Programs** → **Programs and Features**
2. Find "TradeSensei AI" in the list
3. Click "Uninstall"
4. Follow the uninstaller prompts

### Method 2: Manual Uninstall
1. Delete the installation folder (e.g., `C:\Program Files\TradeSensei AI`)
2. Delete shortcuts from Desktop and Start Menu
3. No registry cleanup needed (installer handles this)

## Troubleshooting

### Application Won't Start

**Issue**: "The application failed to start"

**Solutions**:
1. Ensure you have Windows 10 or later (64-bit)
2. Install .NET 8 Runtime: https://dotnet.microsoft.com/download
3. Right-click installer and select "Run as Administrator"

### Can't Connect to Backend

**Issue**: "Failed to connect to trading backend"

**Solutions**:
1. Check internet connection
2. Verify the backend URL in Settings is correct
3. Contact support if the server is down

### Missing Dependencies

**Issue**: "Unable to find required library"

**Solutions**:
1. Reinstall the application
2. Download latest version from releases page
3. Contact support with error details

### Voice Features Not Working

**Issue**: "Microphone not detected" or "No audio output"

**Solutions**:
1. Check Windows audio settings
2. Ensure microphone is not muted
3. Test microphone in Windows Settings
4. Restart the application

## File Locations

| File/Folder | Location |
|---|---|
| Installation | `C:\Program Files\TradeSensei AI` |
| Config | `%APPDATA%\Local\TradeSensei AI` |
| Logs | `%TEMP%\TradeSenseiAI` |
| Desktop Shortcut | `C:\Users\[UserName]\Desktop` |

## Updates

The application checks for updates automatically. To manually check:
1. Click Settings → Check for Updates
2. Or download latest version from releases page

## Support

- **Documentation**: https://github.com/zaneaiofficial-ai/TradeSenseiAI-
- **GitHub Issues**: Report bugs on GitHub
- **Email**: support@tradesensei.ai

## System Administration

### Silent Installation

For IT administrators, perform silent installation:

```cmd
TradeSenseiAI-Setup.exe /S /D=C:\Custom\Path
```

### Enterprise Deployment

For enterprise deployments:
1. Extract portable version to network share
2. Create group policy shortcuts
3. No elevation required for end users

## Security Notes

- ✅ All traffic to backend uses HTTPS
- ✅ API keys stored locally in `App.config`
- ✅ No telemetry or tracking
- ✅ Open source codebase
- ✅ No admin rights required (except initial install)

## License

TradeSensei AI is licensed under the MIT License. See LICENSE.txt for details.

## Version History

**v1.0.0** (December 12, 2025)
- Initial release
- Voice chat with AI mentor
- Price alerts system
- Portfolio tracking
- Trading overlay
- WebSocket streaming

---

**Last Updated**: December 12, 2025
**Installer Version**: 1.0.0
