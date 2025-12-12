; TradeSensei AI Installer Script
; Generated for NSIS 3.x

!include "MUI2.nsh"
!include "x64.nsh"

; Name and file
Name "TradeSensei AI"
OutFile "TradeSenseiAI-Setup.exe"

; Default installation folder
InstallDir "$PROGRAMFILES\TradeSensei AI"

; Get installation folder from registry if available
InstallDirRegKey HKCU "Software\TradeSensei AI" ""

;--------------------------------
; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer sections

Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy all files from publish folder
  File /r "..\src\csharp_ui\bin\Release\net8.0-windows\win-x64\publish\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\TradeSensei AI"
  CreateShortCut "$SMPROGRAMS\TradeSensei AI\TradeSensei AI.lnk" "$INSTDIR\TradeSensei.UI.exe"
  CreateShortCut "$SMPROGRAMS\TradeSensei AI\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortCut "$DESKTOP\TradeSensei AI.lnk" "$INSTDIR\TradeSensei.UI.exe"
  
  ; Write uninstall information
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI" "DisplayName" "TradeSensei AI"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI" "DisplayIcon" "$INSTDIR\TradeSensei.UI.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI" "DisplayVersion" "1.0.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI" "Publisher" "Zane AI"
  
  ; Create uninstall executable
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

;--------------------------------
; Uninstaller section

Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\TradeSensei AI\TradeSensei AI.lnk"
  Delete "$SMPROGRAMS\TradeSensei AI\Uninstall.lnk"
  Delete "$DESKTOP\TradeSensei AI.lnk"
  RMDir "$SMPROGRAMS\TradeSensei AI"
  
  ; Remove registry entries
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\TradeSensei AI"
  DeleteRegKey HKCU "Software\TradeSensei AI"
SectionEnd
