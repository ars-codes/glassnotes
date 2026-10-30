; Inno Setup Script for FloatNote
#define MyAppName "FloatNote"
#define MyAppVersion "2.0.2"
#define MyAppPublisher "FloatNote"
#define MyAppExeName "FloatNote.exe"
#define MyAppId "{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}"

[Setup]
; Permanently fixed AppId matching v1 so upgrades cleanly replace existing installs without duplicate side-by-side installations
AppId={{#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=FloatNoteSetup-{#MyAppVersion}
OutputDir=dist
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no
SetupIconFile=assets\floatnote_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Only replaces application executable in {app} ({localappdata}\FloatNote).
; NEVER touches, modifies, or deletes the user's notes in Documents\FloatNote.
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'FloatNote');
  end;
end;
