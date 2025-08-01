VERSION 5.00
Begin VB.Form frmSplash 
   BorderStyle     =   3  'Fixed Dialog
   Caption         =   "EntropyMax"
   ClientHeight    =   4665
   ClientLeft      =   3060
   ClientTop       =   3585
   ClientWidth     =   6075
   ClipControls    =   0   'False
   LinkTopic       =   "Form2"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   3219.865
   ScaleMode       =   0  'User
   ScaleWidth      =   5704.74
   ShowInTaskbar   =   0   'False
   Begin VB.Timer Timer1 
      Interval        =   4000
      Left            =   120
      Top             =   15
   End
   Begin VB.CommandButton cmdOK 
      Cancel          =   -1  'True
      Caption         =   "OK"
      Default         =   -1  'True
      Height          =   345
      Left            =   4620
      TabIndex        =   0
      Top             =   4305
      Width           =   1260
   End
   Begin VB.Label lblTitle 
      Alignment       =   2  'Center
      BackStyle       =   0  'Transparent
      Caption         =   "EntropyMax"
      BeginProperty Font 
         Name            =   "Comic Sans MS"
         Size            =   18
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      ForeColor       =   &H00FF0000&
      Height          =   555
      Left            =   105
      TabIndex        =   1
      Top             =   -30
      Width           =   5895
   End
   Begin VB.Image Image1 
      Height          =   4035
      Left            =   -15
      Picture         =   "frmSplash.frx":0000
      Stretch         =   -1  'True
      Top             =   645
      Width           =   6060
   End
   Begin VB.Label lblVersion 
      Caption         =   "Version 1.0 for Windows"
      ForeColor       =   &H00FF0000&
      Height          =   225
      Left            =   4065
      TabIndex        =   2
      Top             =   465
      Width           =   1935
   End
End
Attribute VB_Name = "frmSplash"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Declare Function SetWindowPos Lib "USER32" (ByVal hWnd As Long, ByVal hWndInsertAfter As Long, ByVal X As Long, ByVal Y As Long, ByVal cx As Long, ByVal cY As Long, ByVal wFlags As Long) As Long

'Private Sub cmdSysInfo_Click()
'  Call StartSysInfo
'End Sub

Private Sub cmdOK_Click()
  frmSplash.Timer1.Enabled = True
  Unload Me
End Sub

Private Sub Form_Load()
    Dim ontop
    Const SWP_NOMOVE = 2
    Const SWP_NOSIZE = 1
    Const flags = SWP_NOMOVE Or SWP_NOSIZE
    Const HWND_TOPMOST = -1
    Const HWND_NOTOPMOST = -2
    Me.Move (Screen.Width / 2) - (Me.Width / 2), (Screen.Height / 2) - (Me.Width / 2)
    Show
    DoEvents
    ontop = SetWindowPos(Me.hWnd, HWND_TOPMOST, 0, 0, 0, 0, flags)
    
End Sub

Private Sub Timer1_Timer()
    'Unload the form when the timer fires
    Unload Me
End Sub
