; ==============================================================================
; DEPRECATED: This installer script is retained for reference only.
; The canonical and official Inno Setup script is located at the project root:
;   ..\floatnote.iss (compiled via: iscc floatnote.iss)
; ==============================================================================
; Inno Setup script for FloatNote (Legacy / Reference Only)

#define MyAppName "FloatNote"
#define MyAppVersion "2.0.2"
#define MyAppPublisher "FloatNote"
#define MyAppExeName "FloatNote.exe"
#define MyAppId "{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}"

[Setup]
AppId={{#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\FloatNote
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=FloatNoteSetup-{#MyAppVersion}
SetupIconFile=..\assets\floatnote_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: none; ValueName: "FloatNote"; Flags: uninsdeletevalue

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  RunKey: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RunKey := 'Software\Microsoft\Windows\CurrentVersion\Run';
    if RegValueExists(HKCU, RunKey, 'FloatNote') then
      RegDeleteValue(HKCU, RunKey, 'FloatNote');
  end;
end;
