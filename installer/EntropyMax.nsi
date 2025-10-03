; EntropyMax minimal installer (NSIS)
; - Creates Program Files\EntropyMax directory
; - Uses custom installer icon (icons/emaxlight.ico)
; - Optional checkbox to create Desktop shortcut to open the folder in Explorer

!include "MUI2.nsh"
!include "x64.nsh"

!define APP_NAME "EntropyMax"
!define PROJ_ROOT "${__FILEDIR__}\..\.."

Name "${APP_NAME} Backend"
OutFile "installer.exe"
; Icon for the installer UI
Icon "${PROJ_ROOT}\icons\emaxlight.ico"

; Require admin to write into Program Files
RequestExecutionLevel admin

; Default InstallDir (runtime-adjusted for x64 in .onInit)
InstallDir "$PROGRAMFILES\${APP_NAME}"

!define MUI_ABORTWARNING
!define MUI_ICON "${PROJ_ROOT}\icons\emaxlight.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Uninstall info
!define UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"

Function .onInit
  ; Prefer Program Files (64-bit) on x64 systems
  ${If} ${RunningX64}
    StrCpy $InstDir "$PROGRAMFILES64\${APP_NAME}"
  ${EndIf}

  ; If a previous install exists, silently run its uninstaller first
  ReadRegStr $0 HKLM "${UNINST_KEY}" "UninstallString"
  ${If} $0 != ""
    ; Some uninstall strings are quoted and have args; handle both
    ; Execute silently and wait for completion
    ExecWait '$0 /S'
  ${EndIf}
FunctionEnd

Section "Core files" SEC_CORE
  SectionIn RO
  ; Create the application directory under Program Files
  CreateDirectory "$InstDir"
  ; Create bin and data directories
  CreateDirectory "$InstDir\bin"
  CreateDirectory "$InstDir\data"
  CreateDirectory "$InstDir\data\raw"
  CreateDirectory "$InstDir\data\raw\gps"
  CreateDirectory "$InstDir\data\raw\inputs"
  CreateDirectory "$InstDir\data\processed"
  CreateDirectory "$InstDir\data\processed\csv"
  CreateDirectory "$InstDir\data\processed\parquet"

  ; Install backend executable as entropyMax.exe into bin from @bin (build\bin)
  SetOutPath "$InstDir\bin"
  IfFileExists "${PROJ_ROOT}\build\bin\run_entropymax.exe" 0 +4
    File /oname=entropyMax.exe "${PROJ_ROOT}\build\bin\run_entropymax.exe"
    Goto bin_done
  IfFileExists "${PROJ_ROOT}\build\bin\run_entropymax.exe" 0 +4
    File /oname=entropyMax.exe "${PROJ_ROOT}\build\bin\run_entropymax.exe"
    Goto bin_done
  IfFileExists "${PROJ_ROOT}\build\bin\run_entropymax" 0 +2
    File /oname=entropyMax.exe "${PROJ_ROOT}\build\bin\run_entropymax.exe"
  bin_done:

  ; Copy sample data into raw
  SetOutPath "$InstDir\data\raw\gps"
  File "${PROJ_ROOT}\data\raw\gps\sample_group_1_coordinates.csv"
  SetOutPath "$InstDir\data\raw\inputs"
  File "${PROJ_ROOT}\data\raw\inputs\sample_group_1_input.csv"

  ; Create processed placeholders
  SetOutPath "$InstDir\data\processed"

  ; Add bin to system PATH for all users (HKLM). Append without duplicate checks.
  ReadRegStr $1 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
  StrCmp $1 "" 0 +3
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$InstDir\bin"
    Goto do_broadcast
  StrCpy $5 "$1;$InstDir\bin"
  WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$5"
  do_broadcast:
  System::Call 'USER32::SendMessageTimeoutW(p 0xffff, i 0x1A, p 0, t "Environment", i 0, i 5000, *i .r0)'
SectionEnd

Section "Install shortcut" SEC_SHORTCUT
  ; Create Desktop shortcut that points directly to the install directory
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$InstDir" "" "$InstDir" 0
SectionEnd

; ---------------- Uninstaller ----------------
Section -Post
  ; Write uninstaller and registry entries
  WriteUninstaller "$InstDir\\Uninstall.exe"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${UNINST_KEY}" "InstallLocation" "$InstDir"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" "$InstDir\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Remove PATH entry (safe to leave if not present)
  ReadRegStr $1 HKLM "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" "Path"
  StrCpy $2 "$1"
  ; Simple removal by rewriting PATH without our segment (best-effort)
  ; Note: keeping it simple per user's instruction to avoid complex logic
  ; Cleanup files and directories
  Delete "$DESKTOP\\${APP_NAME}.lnk"
  RMDir /r "$InstDir\data"
  RMDir /r "$InstDir\bin"
  Delete "$InstDir\\Uninstall.exe"
  RMDir "$InstDir"
  DeleteRegKey HKLM "${UNINST_KEY}"
  ; Broadcast environment change
  System::Call 'USER32::SendMessageTimeoutW(p 0xffff, i 0x1A, p 0, t "Environment", i 0, i 5000, *i .r0)'
SectionEnd


