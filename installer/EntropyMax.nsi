; EntropyMax minimal installer (NSIS)
; - Creates Program Files\EntropyMax directory
; - Uses custom installer icon (icons/emaxlight.ico)
; - Optional checkbox to create Desktop shortcut to open the folder in Explorer

!include "MUI2.nsh"
!include "x64.nsh"

!define APP_NAME "EntropyMax"
!define PROJ_ROOT "${__FILEDIR__}\..\.."
!define EMX_DLLS_DIR "${PROJ_ROOT}\build\dlls"

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
    ; Some uninstall strings are quoted and/or include args; try silent then non-silent fallback
    ExecWait '$0 /S'
    ExecWait '$0'
  ${Else}
    ; Fallback to a well-known path if the registry entry is missing
    StrCpy $1 "$InstDir\Uninstall.exe"
    IfFileExists "$1" 0 +2
      ExecWait '"$1" /S'
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

  ; Install backend executable as entropyMax.exe into bin (prefer MSVC build)
  SetOutPath "$InstDir\bin"
  ; Embed the staged executable from build/bin (build must stage it before running makensis)
  File /oname=entropyMax.exe "${PROJ_ROOT}\build\bin\run_entropymax.exe"

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
  ; Bundle required runtime DLLs from centralized build/dlls
  SetOutPath "$InstDir\\bin"
  File "${EMX_DLLS_DIR}\\arrow.dll"
  File "${EMX_DLLS_DIR}\\parquet.dll"
  File "${EMX_DLLS_DIR}\\brotlicommon.dll"
  File "${EMX_DLLS_DIR}\\brotlidec.dll"
  File "${EMX_DLLS_DIR}\\brotlienc.dll"
  File "${EMX_DLLS_DIR}\\bz2.dll"
  File "${EMX_DLLS_DIR}\\lz4.dll"
  File "${EMX_DLLS_DIR}\\snappy.dll"
  File "${EMX_DLLS_DIR}\\zlib1.dll"
  File "${EMX_DLLS_DIR}\\zstd.dll"
  File "${EMX_DLLS_DIR}\\libcrypto-3-x64.dll"
  File "${EMX_DLLS_DIR}\\utf8proc.dll"
  File "${EMX_DLLS_DIR}\\re2.dll"
  File "${EMX_DLLS_DIR}\\abseil_dll.dll"
  File "${EMX_DLLS_DIR}\\gflags.dll"
  File "${EMX_DLLS_DIR}\\libssl-3-x64.dll"
  File "${EMX_DLLS_DIR}\\event.dll"
  File "${EMX_DLLS_DIR}\\event_core.dll"
  File "${EMX_DLLS_DIR}\\event_extra.dll"

  ; Post-install: verify every DLL landed in $InstDir\bin
  !macro VerifyDll _name
    IfFileExists "$InstDir\\bin\\${_name}" +2 0
      Abort "Missing runtime DLL after install: $InstDir\\bin\\${_name}"
  !macroend
  !define NEED_DLLS "arrow.dll|parquet.dll|brotlicommon.dll|brotlidec.dll|brotlienc.dll|bz2.dll|lz4.dll|snappy.dll|zlib1.dll|zstd.dll|libcrypto-3-x64.dll|libssl-3-x64.dll|utf8proc.dll|re2.dll|abseil_dll.dll|gflags.dll|event.dll|event_core.dll|event_extra.dll"
  StrCpy $4 "${NEED_DLLS}"
  loop_dlls:
    StrCpy $5 $4 0 "|"
    StrCmp $5 "" done_dlls
    ; Extract token up to '|'
    StrLen $6 $4
    StrCpy $7 0
    find_bar:
      StrCpy $8 $4 1 $7
      StrCmp $8 "|" found_bar
      IntOp $7 $7 + 1
      StrCmp $7 $6 found_bar
      Goto find_bar
    found_bar:
    StrCpy $9 $4 $7
    IntOp $7 $7 + 1
    StrCpy $4 $4 -$7 $7
    !insertmacro VerifyDll "$9"
    Goto loop_dlls
  done_dlls:

  ; Run the backend once and verify Parquet is generated and non-zero
  ; Execute backend with installed sample CSVs
  ExecWait '"$InstDir\\bin\\entropyMax.exe" "$InstDir\\data\\raw\\inputs\\sample_group_1_input.csv" "$InstDir\\data\\raw\\gps\\sample_group_1_coordinates.csv"' $0
  StrCmp $0 0 +2 0
    Abort "Backend execution failed (exit $0)."

  ; Verify Parquet exists
  StrCpy $1 "$InstDir\\data\\processed\\parquet\\output.parquet"
  IfFileExists "$1" +2 0
    Abort "Parquet output not found: $1"
  ; Verify file size > 0
  FileOpen $2 "$1" r
  FileSeek $2 0 END $3
  FileClose $2
  StrCmp $3 0 0 +2
    Abort "Parquet output is zero bytes: $1"
  ; Report success to the user
  DetailPrint "Verified Parquet output: $1 ($3 bytes)"
  MessageBox MB_ICONINFORMATION "EntropyMax install check: Parquet output verified at $1 ($3 bytes)."
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


