; Inno Setup script for the Tab Transfer native helper.
; Build the helper first (from the project root):  pyinstaller --onedir app\tab_transfer.py
; Then compile this file in the Inno Setup Compiler.

#define AppName "Tab Transfer Helper"
#define AppVersion "1.2"

[Setup]
; Unique ID for this app. Keep it the same in every version so upgrades replace the old install.
AppId={{652DD9CA-4A31-400B-B636-7D510FA8BAE6}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=David Zhang
; Per-user install: no admin prompt, and {autopf} becomes %LOCALAPPDATA%\Programs
PrivilegesRequired=lowest
DefaultDirName={autopf}\TabTransfer
DisableDirPage=yes
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=TabTransferSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#AppName}

[Files]
; One-folder PyInstaller build: tab_transfer.exe plus its _internal\ folder
Source: "..\dist\tab_transfer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tab_transfer_chrome.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "tab_transfer_firefox.json"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Tell each browser where its host manifest is. uninsdeletekey removes the key on uninstall.
Root: HKCU; Subkey: "Software\Google\Chrome\NativeMessagingHosts\tab_transfer"; ValueType: string; ValueName: ""; ValueData: "{app}\tab_transfer_chrome.json"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Mozilla\NativeMessagingHosts\tab_transfer"; ValueType: string; ValueName: ""; ValueData: "{app}\tab_transfer_firefox.json"; Flags: uninsdeletekey
