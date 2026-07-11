; Inno Setup script for Lazy Comments — Voice Input
; Builds a Windows installer with optional desktop shortcut and autostart.
;
; Paths are resolved relative to this .iss file (SourcePath), so the script
; works from any ASCII-only build directory. Expected layout next to lazy_comments.iss:
;   ./lazy_comments.ico
;   ./dist/lazy_comments/lazy_comments.exe
;   ./dist/lazy_comments/_internal/...
; Output:
;   ./installer/lazy_comments-setup.exe

#define MyAppName "Lazy Comments"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Lazy Comments"
#define MyAppExeName "lazy_comments.exe"

[Setup]
AppId={{8D2A1B3F-4E5C-4D7A-9F8B-1E2C3D4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline dialog
OutputDir={#SourcePath}\installer
OutputBaseFilename=lazy_comments-setup
SetupIconFile={#SourcePath}\lazy_comments.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Запускать Lazy Comments при старте Windows"; GroupDescription: "Дополнительно:"; Flags: unchecked

[Files]
Source: "{#SourcePath}\dist\lazy_comments\lazy_comments.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\dist\lazy_comments\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Autostart entry (only if user checked the autostart task)
; HKA = HKLM for admin install (all users), HKCU for per-user install
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Lazy Comments"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName} сейчас"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Kill any running lazy_comments.exe before uninstalling
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM lazy_comments.exe"; Flags: runhidden; RunOnceId: "KillLazy Comments"
