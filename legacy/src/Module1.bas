Attribute VB_Name = "Module1"
Option Explicit
Public Declare Function SetCursorPos Lib "USER32" (ByVal X As Long, ByVal Y As Long) As Long
Public Type POINTAPI
        X As Long
        Y As Long
End Type
Public bRs As Boolean
Public nOutputType As Integer
Public Type GroupData
    ngrps As Integer           '
    fGmean() As Single  '
    member2() As Long   '
End Type
Public Type GroupSetData
    Set As GroupData
End Type

Public Sub GetSaveFile(nFileType As Integer, sFilename As String, sFileTitle As String, bexit As Boolean)
'This subroutine displays the save dialog and checks
'whether a file exists
Dim nResult As Integer
Dim spath$
On Error GoTo ErrHandler
With Form1.cdlg1
    'set filters
    .Filter = "All Files (*.*)|*.*|Entropy Files (*.csv)|*.csv"
    'set Flags
    .FilterIndex = 2
    'set cancel error
    .CancelError = True
    .FileName = "*.csv"
End With
If nFileType = 0 Then
    With Form1.cdlg1
        'set Flags
        .flags = cdlOFNHideReadOnly Or cdlOFNFileMustExist
        .DialogTitle = "Open an Entropy File"
    End With
    nResult = 0
    Do While nResult = 0
        Form1.cdlg1.ShowOpen
        If Dir$(Form1.cdlg1.FileName) <> "" Then
            sFilename = Form1.cdlg1.FileName 'with path
            nResult = 1
        End If
       sFileTitle = Form1.cdlg1.FileTitle 'no path
    Loop
Else
    With Form1.cdlg1
        'Set title
        .DialogTitle = "Save Entropy file as"
        'hide read only box
        .flags = cdlOFNHideReadOnly
    End With
    nResult = 0
    Do While nResult = 0
        Form1.cdlg1.ShowSave
        'check if file exists
        If Dir$(Form1.cdlg1.FileName) <> "" Then
            'MsgBox cdlg1.FileName
            nResult = MsgBox("File exists - overwrite?", vbYesNoCancel + vbExclamation + vbDefaultButton2)
            Select Case nResult
                Case vbNo
                    nResult = 0
                Case vbYes
                    nResult = 1
                Case vbCancel
                    Exit Sub
            End Select
        Else
            nResult = 1
        End If
    Loop
    sFilename = Form1.cdlg1.FileName
    sFileTitle = Form1.cdlg1.FileTitle 'no path

End If
Exit Sub
ErrHandler:
' User pressed Cancel button.
bexit = True
End Sub

