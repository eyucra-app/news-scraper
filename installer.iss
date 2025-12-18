; Script Inno Setup para News Scraper Backend
; Crea un instalador profesional para Windows

#define MyAppName "News Scraper"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "Eyucra"
#define MyAppURL "https://news-scraper-v1.vercel.app"
#define MyAppExeName "NewsScraperBackend.exe"

[Setup]
; Información básica de la aplicación
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer_output
OutputBaseFilename=NewsScraperSetup
SetupIconFile=icon.png
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Iniciar automáticamente con Windows"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
; Archivo ejecutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Icono
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
; Script de instalación de Playwright (Python)
Source: "setup_playwright.py"; DestDir: "{app}"; Flags: ignoreversion
; Script de instalación de Playwright (Batch)
Source: "install_playwright.bat"; DestDir: "{app}"; Flags: ignoreversion
; README u otros archivos opcionales
Source: "BUILD_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README.txt"

[Icons]
; Acceso directo en menú inicio - abre la aplicación
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.png"; Comment: "Abrir News Scraper"
; Acceso directo para instalar Playwright
Name: "{group}\Instalar Playwright"; Filename: "{app}\install_playwright.bat"; Comment: "Instalar Playwright (requerido para scraping avanzado)"
; Acceso directo para desinstalar
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
; Acceso directo en escritorio (opcional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.png"; Tasks: desktopicon; Comment: "Abrir News Scraper"
; Quick Launch (opcional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.png"; Tasks: quicklaunchicon

[Registry]
; Auto-inicio de Windows (si el usuario lo seleccionó)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "NewsScraperBackend"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autostart; Flags: uninsdeletevalue

[Run]
; Instalar Playwright automáticamente después de instalar
Filename: "{app}\install_playwright.bat"; Description: "Instalar Playwright (requerido para scraping avanzado)"; Flags: postinstall skipifsilent
; Ejecutar después de instalar (opcional)
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Detener el proceso antes de desinstalar
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "StopBackend"

[UninstallDelete]
; Eliminar datos del usuario (base de datos, logs, configuraciones)
Type: filesandordirs; Name: "{userappdata}\NewsScraper"
Type: files; Name: "{userdocs}\news_scraper.log"
Type: files; Name: "{userdocs}\news_scraper_debug.log"

[Code]
// Script Pascal para funciones personalizadas

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Acciones después de la instalación
  end;
end;

[Messages]
WelcomeLabel2=Esto instalará [name/ver] en tu computadora.%n%nNews Scraper es una aplicación 100% local que se ejecuta en una ventana nativa.%n%nEl backend y frontend funcionan completamente offline desde tu PC.%n%nSe recomienda cerrar todas las demás aplicaciones antes de continuar.
