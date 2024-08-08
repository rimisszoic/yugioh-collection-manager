; Script generado por el Asistente de Scripts de Inno Setup.
; CONSULTA LA DOCUMENTACIÓN PARA DETALLES SOBRE LA CREACIÓN DE ARCHIVOS DE SCRIPT DE INNO SETUP

#define MyAppName "Yugioh Collection Manager"
#define MyAppVersion "1.0"
#define MyAppExeName "gui.exe"  ; Archivo principal ejecutable
#define MyAppIconFile "dark-magician-logo-small.ico" ; Archivo de icono

[Setup]
AppId={{57E42E52-2A5A-45B6-ADCC-D8DEFCBC4B34}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=LICENSE.txt
InfoAfterFile=LICENSE.txt
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=compile
OutputBaseFilename=Yugioh_Collection_Manager_Setup
SetupIconFile={#MyAppIconFile}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppIconFile}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconFile}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconFile}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent