VERSION 5.00
Object = "{65E121D4-0C60-11D2-A9FC-0000F8754DA1}#2.0#0"; "MSCHRT20.OCX"
Object = "{F9043C88-F6F2-101A-A3C9-08002B2F49FB}#1.2#0"; "comdlg32.ocx"
Begin VB.Form Form1 
   AutoRedraw      =   -1  'True
   BorderStyle     =   3  'Fixed Dialog
   Caption         =   "EntropyMax"
   ClientHeight    =   7575
   ClientLeft      =   150
   ClientTop       =   540
   ClientWidth     =   8910
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   7575
   ScaleWidth      =   8910
   StartUpPosition =   2  'CenterScreen
   Begin VB.Frame Frame2 
      Caption         =   "Chart"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   8.25
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   5340
      Left            =   135
      TabIndex        =   11
      Top             =   2145
      Width           =   8685
      Begin MSChart20Lib.MSChart MSChart1 
         Height          =   5010
         Left            =   75
         OleObjectBlob   =   "Form1.frx":0000
         TabIndex        =   12
         Top             =   255
         Width           =   8460
      End
   End
   Begin VB.Frame Frame1 
      Caption         =   "Processing Options"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   8.25
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   690
      Left            =   135
      TabIndex        =   9
      Top             =   1365
      Width           =   5775
      Begin VB.CheckBox chkProp 
         Caption         =   "Take row proportions"
         Height          =   195
         Left            =   1912
         TabIndex        =   13
         Top             =   330
         Width           =   1815
      End
      Begin VB.CheckBox chkLog 
         Caption         =   "Create Log File"
         Enabled         =   0   'False
         Height          =   240
         Left            =   1710
         TabIndex        =   15
         Top             =   165
         Visible         =   0   'False
         Width           =   1530
      End
      Begin VB.CheckBox chkGrps 
         Caption         =   "Do 2 to 20 Groups"
         Height          =   195
         Left            =   3855
         TabIndex        =   14
         Top             =   330
         Value           =   1  'Checked
         Width           =   1785
      End
      Begin VB.CheckBox chkPerm 
         Caption         =   "Do Permutations"
         Height          =   195
         Left            =   270
         TabIndex        =   10
         Top             =   330
         Value           =   1  'Checked
         Width           =   1515
      End
   End
   Begin VB.CommandButton cmdExit 
      Caption         =   "Exit"
      Height          =   510
      Left            =   6075
      TabIndex        =   8
      Top             =   1485
      Width           =   1320
   End
   Begin VB.Frame Frame4 
      Caption         =   "Input"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   8.25
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   1110
      Left            =   150
      TabIndex        =   6
      Top             =   165
      Width           =   1890
      Begin VB.CommandButton Command2 
         Caption         =   "Select Input File"
         Height          =   495
         Left            =   240
         TabIndex        =   7
         Top             =   360
         Width           =   1410
      End
   End
   Begin VB.Frame fraOutput 
      Caption         =   "Output"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   8.25
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   1110
      Left            =   2235
      TabIndex        =   1
      Top             =   165
      Width           =   6570
      Begin VB.CommandButton cmdSavFile 
         Caption         =   "Define Output Filename"
         Height          =   480
         Left            =   330
         TabIndex        =   5
         Top             =   375
         Width           =   1860
      End
      Begin VB.OptionButton Option1 
         Caption         =   "Both"
         Height          =   360
         Index           =   2
         Left            =   5475
         TabIndex        =   4
         Top             =   435
         Width           =   630
      End
      Begin VB.OptionButton Option1 
         Caption         =   "Individual"
         Height          =   360
         Index           =   1
         Left            =   3975
         TabIndex        =   3
         Top             =   435
         Width           =   1200
      End
      Begin VB.OptionButton Option1 
         Caption         =   "Composite"
         Height          =   360
         Index           =   0
         Left            =   2490
         TabIndex        =   2
         Top             =   435
         Value           =   -1  'True
         Width           =   1200
      End
   End
   Begin MSComDlg.CommonDialog cdlg1 
      Left            =   30
      Top             =   90
      _ExtentX        =   847
      _ExtentY        =   847
      _Version        =   393216
   End
   Begin VB.CommandButton cmdProceed 
      Caption         =   "Proceed"
      Height          =   525
      Left            =   7545
      TabIndex        =   0
      Top             =   1470
      Width           =   1245
   End
   Begin VB.Menu mnuFile 
      Caption         =   "&File"
      Begin VB.Menu mnuOpen 
         Caption         =   "&Open"
         Shortcut        =   ^O
      End
      Begin VB.Menu mnuExit 
         Caption         =   "&Exit"
         Shortcut        =   ^X
      End
   End
   Begin VB.Menu mnuChrtOpt 
      Caption         =   "&ChartOptions"
      Begin VB.Menu mnuCopy 
         Caption         =   "&Copy"
         Shortcut        =   ^C
      End
   End
   Begin VB.Menu mnuHelp1 
      Caption         =   "&Help"
      Begin VB.Menu mnuContents 
         Caption         =   "&Contents"
         Shortcut        =   ^H
      End
      Begin VB.Menu mnuAbout 
         Caption         =   "&About"
      End
   End
End
Attribute VB_Name = "Form1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit
Private Prvsstt
Private Prvsset
Private PrvfCHpermF
Private PrvfCHPermP
Private Prvstatmx
Private PrvCounter

Private sInFilename$
Private sinFileTitle$
Private sOutFilename$
Private sOutFileTitle$
Private RsGraph() As Variant
Private Const HH_DISPLAY_TOPIC As Long = 0
Private Const HH_HELP_CONTEXT As Long = &HF
Private Declare Function HtmlHelp Lib "HHCtrl.ocx" Alias "HtmlHelpA" _
(ByVal hWndCaller As Long, _
     ByVal pszFile As String, _
     ByVal uCommand As Long, _
     dwData As Any) As Long

Private Sub calculate()
DoEvents
'
'       INFORMATION CLASSIFICATION
'       Q BASIC CODE WRITTEN BY K MICHIBAYASHI
'       MODIFICATIONS BY J H LALLY
'       CONVERSION TO VISUAL BASIC 6 AND ADDITIONAL MODIFICATIONS BY L K STEWART
'       This proftware employs sections of code obtained via Microsoft Knowledge Base
'       and other publicly avaialble sources.
'       This program is written for ASCII input files.
 Dim Title$
 Dim jobs%
 Dim nvar%
 Dim CLtitle$()
 Dim RWTitle$()
 Dim result()
 Dim sData()
 Dim RWtotal()
 Dim CLtotal()
 Dim SD()
 Dim TM()
 Dim Y()
 Dim tineq
Dim i%, lxPoint&, lyPoint&
Dim Point As POINTAPI
Dim bexit As Boolean
bexit = False
 '
 'PARAMETERS ARE
 '   TITLE   ALPHANUMERIC TITLE
 '   JOBS    NUMBER OF OBSERVATIONS (ROW): SAMPLES (INTEGER)
 '   NVAR    NUMBER OF VARIABLES (COLUMN) (INTEGER)
 '   MINGRP  MINIMUM NUMBER OF GROUPS (INTEGER: DEFAULT 1)
 '   MAXGRP  MAXIMUM NUMBER OF GROUPS (INTEGER: DEFAULT JOBS)
 '   GDTOTAL THE GRAND TOTAL (IF OMITTED, DATA ARE SUMMED IN PROGRAM)
 '
 '*main program

'  "++++++++++++++++++++++++++++++++"
'  " ENTROPY ANALYSIS (Version 4.2)"
'  "++++++++++++++++++++++++++++++++"
'  "This program is written based on"
'  "R. J. Johnson and R. K. Semple (1983)"
'  "CLASSIFICATION USING INFORMATION STATISTICS"
'  "Geobooks, Norwich"
'  "Original QBasic code by Katsu Michibayashi"
'  "Modifications by James Lally"
'  "Department of Earth Sciences"
'  "James Cook University of North Queensland"
'  "(15th February 1995)"
'Conversion to Visual Basic 6 and further modifications by L K Stewart
'CSIRO Land and Water, and
'  "Department of Earth Sciences"
'  "James Cook University of North Queensland"
'  "(2005)"
'

        Form1.MousePointer = vbHourglass
        'ACT 1: assemble data matrix
        'get the nvar and jobs
        Form1.Caption = "EntropyMax - preprocessing..."
1       Call FileK3(Title, jobs, nvar, CLtitle(), RWTitle(), result(), sData(), bexit)
        If bexit Then Exit Sub
        'transform data
        DoEvents
        Call Proportion(Title, jobs, nvar, CLtitle(), RWTitle(), result(), sData())
        DoEvents
        Call GDTLproportion(Title, jobs, nvar, CLtitle(), RWTitle(), result(), sData())
          'ACT 2: find total inequality
        ReDim SD(nvar), TM(nvar), Y(nvar)
            DoEvents
        Call MeansSTdev(CLtitle(), jobs, nvar, result(), sData(), TM(), SD())
            DoEvents
        Call TOTALinequality(jobs, nvar, result(), sData(), Y(), tineq)
            DoEvents
        'ACT 3: identify best grouping
        Call LOOPgroupsize(Title, CLtitle(), RWTitle(), jobs, nvar, result(), sData(), Y(), tineq, TM(), SD())
        'move the mouse pointer over the form to reset the mouse pointer - needed for quirky
        'thing happening with ActiveX control
        With Form1
            lyPoint = ScaleY(.Top + .cmdExit.Top + cmdExit.Height / 2 + 500, vbTwips, vbPixels)
            lxPoint = ScaleX(.Left + .cmdExit.Left + .cmdExit.Width / 2, vbTwips, vbPixels)
        End With
        SetCursorPos lxPoint, lyPoint
        cmdExit.SetFocus
        Form1.MousePointer = vbDefault
        Form1.Caption = "EntropyMax"
    End Sub

Sub BESTgroup(statmx, ng%, jobs%, member1%())
Dim i%
Dim j%
If chkLog.Value = Checked Then
        For i = 1 To ng
                Print #2, "Group"; i; "{";
                For j = 1 To jobs
                        If member1(j) = i Then Print #2, j;
                Next j
                Print #2, "}"
        Next i
        '
        If statmx > 0 Then Print #2, statmx; "% explained"
End If
End Sub

Sub BETWEENinquality(jobs%, nvar%, ng%, member1%(), result(), sData(), Y(), bineq)
'
'calculate between-region inequality
'
        Dim k%
        Dim II%
        Dim JJ%
        Dim bineq2
        Dim yr()
        Dim nr()
        ReDim yr(jobs, nvar)
        ReDim nr(ng)
        For II = 1 To ng
                For k = 1 To nvar
                        yr(II, k) = 0#
                Next k
                nr(II) = 0
                'calculate for each sample along row
                For JJ = 1 To jobs
                        If member1(JJ) <> II Then GoTo 27 'error trap ?
                        For k = 1 To nvar
                                yr(II, k) = yr(II, k) + result(JJ, k)
                        Next k
                        nr(II) = nr(II) + 1 'counts number of  times through
27              Next JJ
            'upgrade yr()
                For JJ = 1 To nvar
                    If Y(JJ) > 0 Then
                        yr(II, JJ) = yr(II, JJ) / Y(JJ)
                    Else
                   End If
                Next JJ
          Next II
          bineq = 0#
          'cycle through yr for each group for bineq
          For JJ = 1 To nvar
            bineq2 = 0#
            For II = 1 To ng
              If nr(II) = 0 Then GoTo 30
              If yr(II, JJ) = 0 Then GoTo 30
              bineq2 = bineq2 + yr(II, JJ) * Log(yr(II, JJ) * CSng(jobs) / nr(II)) / Log(2)
30          Next II
            bineq = bineq + Y(JJ) * bineq2
          Next JJ
End Sub

Sub FileK3(Title$, jobs%, nvar%, CLtitle$(), RWTitle$(), result(), sData(), bexit As Boolean)
Dim i%
Dim j%
Dim chk$
Dim head$
        Open sInFilename For Input As #1
        Open "c:\column" For Output As #2
'        'check data matrix
linein:
        If EOF(1) Then GoTo colchk
        Line Input #1, chk  'read in line
        jobs = jobs + 1 'counter of number of lines in file
        If jobs = 1 Then Print #2, chk 'print first line to file 2
        Close #2
        GoTo linein 'loop back to line in
colchk:
        Close #1
        Open "c:\column" For Input As #1
'        CLS
        'debug.print "Column headers in file:"
varcount:
        If EOF(1) Then GoTo confirm
        Input #1, head
        nvar = nvar + 1
        'debug.print head; " | ";  'appears to be visual check of first line
        GoTo varcount
confirm:
        Close #1
        'ACT 1:
        Open sInFilename For Input As #1
        nvar = nvar - 1: jobs = jobs - 1
        ReDim CLtitle(nvar + 1), RWTitle(jobs), result(jobs, nvar), sData(jobs, nvar), RWtotal(jobs), CLtotal(nvar)
        'ACT 2: READ column's titles
        For i = 1 To nvar + 1
           Input #1, CLtitle(i)
        Next i
        'ACT 3: read row's title: sample no.
        For i = 1 To jobs
           Input #1, RWTitle(i)
           For j = 1 To nvar
                result(i, j) = 0
                sData(i, j) = 0
                'ACT 4: read each data
                Input #1, result(i, j)
                sData(i, j) = result(i, j)
           Next j
        Next i
        Close #1
        If chkLog.Value = Checked Then Open sInFilename & ".log" For Append As #2

End Sub

Sub GDTLproportion(Title$, jobs%, nvar%, CLtitle$(), RWTitle$(), result(), sData())
        '
        'express cell values as proportion of grand total
        '
        Dim RWtotal()
        Dim GDtotal
        Dim i%
        Dim j%
        ReDim RWtotal(jobs)
        GDtotal = 0#
        For i = 1 To jobs
                RWtotal(i) = 0#
                For j = 1 To nvar
                        RWtotal(i) = RWtotal(i) + result(i, j)
                        GDtotal = GDtotal + result(i, j)
                Next j
        Next i
        '
        For i = 1 To jobs
                For j = 1 To nvar
                        result(i, j) = (result(i, j) / GDtotal) * CSng(100)
                Next j
                        RWtotal(i) = RWtotal(i) / GDtotal * CSng(100)
        Next i
End Sub

Sub INITIALgroup(jobs%, nvar%, ng, member1%())
        '
        'initialize classes to classify observations
        '
        Dim i%
        Dim j%
        Dim k%
        Dim L%
        Dim m%
        i = jobs \ ng ' determine a number of classes (integer)
        L = 1
        m = i
        For k = 1 To ng
                ReDim Preserve member1(m)
                For j = L To m
                        member1(j) = k 'initialize each equal-sized class
                Next j
          '
          L = m + 1
          m = m + i
        Next k
        '
        'check whether numbers of definition of classes is satisfied
        'for all observations.
        If L <= jobs Then
                ReDim Preserve member1(jobs)
                For i = L To jobs
                        member1(i) = ng
                Next i
        End If
50      '
End Sub

Private Sub LOOPgroupsize(Title$, CLtitle$(), RWTitle$(), jobs%, nvar%, result(), sData(), Y(), tineq, TM(), SD())
'
'Loop group sizes from minimum to maximum
'
Dim Message, BoxTitle, Default, MyValue, Response
Dim i%
Dim j%
Dim mingrp%
Dim maxgrp%
Dim totgrp%
Dim intmed%
Dim statmx
Dim ng%
Dim ixout%
Dim bineq
Dim pineq
Dim sstt, sset
Dim ngmax%
Dim bDetail As Boolean
Dim sumx()
Dim gmean()
Dim ZT()
Dim member1%()
Dim member2%()
ReDim sumx(jobs, nvar)
ReDim gmean(jobs, nvar)
ReDim ZT(jobs, nvar)
Dim bexit As Boolean
Dim bAgain As Boolean
Dim bChange As Boolean
Dim Counter%, nCounterIndex%
Dim nGrpDum
Dim fCHDum
Dim nSLen%, nFSlen%, nPos%, sDum$, sFilename$
Dim CHsstsse()
Dim fSST, fSSE, fCHF, fCHP, fRs
Dim AGroup As GroupData
Dim TheGroups() As GroupSetData
        '--------------------------------------------------
        'definition of minimum and maximum number of groups
        '--------------------------------------------------
        mingrp = 1
        maxgrp = jobs
        totgrp = 1
        If chkGrps Then
            mingrp = 2
            maxgrp = 20
        Else
            Form1.MousePointer = vbDefault
            Response = MsgBox("Modify number of Groups, " & "Min = " & mingrp + 1 & " Max = " & maxgrp, vbInformation _
            + vbYesNo, "Modify Groups?")
            If Response = vbYes Then   ' User chose Yes.
               bChange = True
            Else   ' User chose No.
               bChange = False
            End If
            If bChange Then
rent:           Message = "Enter a new minimum number of groups"   ' Set prompt.
                BoxTitle = "Groups"   ' Set title.
                Default = mingrp + 1    ' Set default.
                ' Display message, title, and default value.
                MyValue = InputBox(Message, BoxTitle, Default)
                If CInt(MyValue) < 2 Then
                    Beep
                    GoTo rent
                End If
                mingrp = CInt(MyValue)
                Message = "Enter a new maximum number of groups"   ' Set prompt.
                BoxTitle = "Groups"   ' Set title.
                Default = maxgrp   ' Set default.
                ' Display message, title, and default value.
                MyValue = InputBox(Message, BoxTitle, Default)
                maxgrp = CInt(MyValue)
            End If
            Form1.MousePointer = vbHourglass
        End If
        totgrp = maxgrp - mingrp + 1
        ReDim RsGraph(0 To maxgrp - mingrp + 1, 1 To 3)
        ReDim CHsstsse(0 To maxgrp - mingrp + 1, 1 To 6)
        
        ReDim TheGroups(0 To totgrp - 1)
35      intmed = 1
        '
        '
        statmx = 0#
        Counter = -1
        For ng = mingrp To maxgrp
                Form1.Caption = "EntropyMax - processing " & ng & " groups"
                DoEvents
                Counter = Counter + 1
                ixout = 0
                Call INITIALgroup(jobs, nvar, ng, member1())
                Call SWITCHgroup(CLtitle(), ixout, jobs, nvar, ng, member1(), result(), sData(), mingrp, tineq, bineq, pineq, Y(), TM(), SD(), intmed, sumx())
                'calculate groups means and S D S
                ngmax = ng
                ReDim AGroup.fGmean(1 To ng, 1 To nvar)
                ReDim AGroup.member2(1 To jobs)
                ReDim member2(jobs)
                For i = 1 To jobs
                        member2(i) = member1(i)
                        AGroup.member2(i) = member2(i)
                Next i
                For i = 1 To ng
                        For j = 1 To nvar
                            gmean(i, j) = sumx(i, j)
                            AGroup.fGmean(i, j) = gmean(i, j)
                        Next j
                Next i
                AGroup.ngrps = ng
                TheGroups(Counter).Set = AGroup
                statmx = pineq
        Call SAVEdata(Title, CLtitle(), RWTitle(), statmx, jobs, nvar, member2(), ngmax, gmean(), sData(), totgrp, bineq, tineq, CHsstsse(), sstt, sset, Counter)
        Debug.Print "Group progress "; ng
44    Next ng
        nSLen = Len(sOutFileTitle)
        nFSlen = Len(sOutFilename)
        nPos = nFSlen - nSLen
        sDum = Left(sOutFilename, nPos)
        sFilename = ""
        sFilename = sDum & "Detail_" & sOutFileTitle
        Open sFilename For Append As #3
        Print #3,
        If chkPerm.Value = Checked Then
            Print #3, "Groups, C-H Value, SST (Orig.), SSE (Orig.), SST (Perm.) , CHPerm, CHProb, Rs Value"
        Else
            Print #3, "Groups, C-H Value,SST, SSE, Rs Value"
        End If
        fCHDum = 0
        nGrpDum = 0
        fSST = 0
        fSSE = 0
        fCHF = 0
        fCHP = 0
        fRs = 0
        Debug.Print Counter, " counter"
        'Store optimal values
        For i = 0 To Counter
            If RsGraph(i, 2) > fCHDum Then
                nGrpDum = RsGraph(i, 1)
                fCHDum = RsGraph(i, 2)
                fSST = CHsstsse(i, 1)
                fSSE = CHsstsse(i, 2)
                fCHF = CHsstsse(i, 3)
                fCHP = CHsstsse(i, 4)
                fRs = CHsstsse(i, 5)
                nCounterIndex = CHsstsse(i, 6)
            End If
            If chkPerm.Value = Checked Then
                Print #3, RsGraph(i, 1) & ", " & RsGraph(i, 2) & ", " & Prvsstt & ", " & CHsstsse(i, 2) & ", " & CHsstsse(i, 1) & ", " & CHsstsse(i, 3) & ", " & CHsstsse(i, 4) & ", " & CHsstsse(i, 5)
            Else
                Print #3, RsGraph(i, 1) & ", " & RsGraph(i, 2) & ", " & Prvsstt & ", " & CHsstsse(i, 2) & ", " & CHsstsse(i, 5)
            End If
        Next i
        Print #3,
        Print #3, "Optimum Grouping is " & nGrpDum & " groups. C-H value is " & fCHDum
        Print #3, "Total sum of squares: " & Prvsstt & " Within group sum of squares: " & fSSE
        Call RITE(CLtitle(), statmx, jobs, nvar, result(), sData(), ZT(), SD(), TM(), TheGroups(nCounterIndex).Set)
        Close 'closing files 2, 3
49
End Sub

Sub MeansSTdev(CLtitle$(), jobs%, nvar%, result(), sData(), TM(), SD())
        '
        'find means and standard deviations
        '
        Dim i%
        Dim j%
        Dim fPart1, fPart2, fDiff
        For i = 1 To nvar
                SD(i) = 0#: TM(i) = 0#
        Next i
        '
        For i = 1 To jobs
          For j = 1 To nvar
                TM(j) = TM(j) + result(i, j)
                SD(j) = SD(j) + result(i, j) ^ 2
          Next j
        Next i
        '
        For j = 1 To nvar
                TM(j) = TM(j) / CSng(jobs)
                fPart1 = (SD(j) / CSng(jobs))
                fPart2 = TM(j) ^ 2
                fDiff = fPart1 - fPart2
                If fDiff < 0 And fDiff > -0.0001 Then
                    SD(j) = 0
                Else
                    SD(j) = Sqr(fDiff)
                End If
        Next j
        'print means and standard deviations
        If chkLog.Value = Checked Then
                'print column's titles
                i = 0
                Print #2,
                Do: i = i + 1
                        Print #2, CLtitle(i) & ", ";
                Loop While i < nvar + 1 'And i < 5
                Print #2, CLtitle(nvar + 1)
                '
                Print #2, "Mean, ";
                j = 0
                Do: j = j + 1
                        Print #2, Format(TM(j), "Fixed") & ", ";
                Loop While j < nvar 'And j < 4
                Print #2, Format(TM(nvar), "Fixed") & " "
                Print #2, "Std Dev ";
                j = 0
                Do: j = j + 1
                        Print #2, Format(SD(j), "Fixed") & " ";
                Loop While j < nvar 'And j < 4
                Print #2, Format(SD(nvar), "Fixed") & " "
        End If
        '
End Sub

Sub OPTIMALgroup(jobs%, nvar%, ng%, result(), sData(), member1%(), istore%, olstat, pineq, mingrp%, ind%, i%, sumx())
'
'find optimum
'
        Dim I2%
        Dim J2%
        Dim LT%
        Dim ngrp()
        ReDim ngrp(jobs)
        '
        'evaluate new group against previous
        '
        'if Rs statistic (pineq) is greater than old stat then recalculate sums
        If pineq > olstat Then GoTo 34
        ind = ind - 1
        member1(i) = istore
        pineq = olstat
        If ng > mingrp Then GoTo 39
        '
        'sums for optimal groups
        '
34      For I2 = 1 To ng
          ngrp(I2) = 0
          For J2 = 1 To nvar
            sumx(I2, J2) = 0#
          Next J2
        Next I2
        'sum each variable within each group
        For I2 = 1 To jobs
          For J2 = 1 To nvar
            LT = member1(I2)
            sumx(LT, J2) = sumx(LT, J2) + result(I2, J2)
          Next J2
          ngrp(LT) = ngrp(LT) + 1
        Next I2
        'divide sum by number in group
        For I2 = 1 To ng
          For J2 = 1 To nvar
            sumx(I2, J2) = sumx(I2, J2) / ngrp(I2)
          Next J2
        Next I2
39      olstat = pineq 'set olstat to pineq
End Sub

Sub Proportion(Title$, jobs%, nvar%, CLtitle$(), RWTitle$(), result(), sData())
        '
        'check if to take proportions across rows
        '
Dim XTQ
Dim Response
Dim i%
Dim j%
        If Not chkProp Then Exit Sub
        For i = 1 To jobs
                'sum row
                XTQ = 0
                For j = 1 To nvar
                        XTQ = XTQ + result(i, j)
                Next j
                'change to proportions
                For j = 1 To nvar
                        result(i, j) = result(i, j) / XTQ
                Next j
        Next i
End Sub

Private Sub RITE(CLtitle$(), statmx, jobs%, nvar%, result(), sData(), ZT(), SD(), TM(), TheGroup As GroupData)
'
'print all intermediate groups
'
        Dim i%
        Dim j%
        Dim KK%
        Dim ID%
        Dim DIV
        Dim SE()
        Dim TT()
        ReDim SE(nvar)
        ReDim TT(nvar)
        Dim nSLen%, nFSlen%, nPos%, sDum$, sFilename$
        nSLen = Len(sOutFileTitle)
        nFSlen = Len(sOutFilename)
        nPos = nFSlen - nSLen
        sDum = Left(sOutFilename, nPos)
        sFilename = ""
        sFilename = sDum & "Detail_" & sOutFileTitle
        'write group members to log file
        '----------------------
        'RESULT 1: Group means
        '----------------------
        'print column's title
        Print #3,
        Print #3, "Classes, ";
        i = 1
        Do: i = i + 1
                Print #3, CLtitle(i) & ", ";
        Loop While i < nvar
        Print #3, CLtitle(nvar)
        '
        Print #3, "<< Mean Group Proportions >>"
        For i = 1 To TheGroup.ngrps
            Print #3, "Group " & i & ", ";
            j = 0
            Do: j = j + 1
                    Print #3, Format(TheGroup.fGmean(i, j), "Fixed") & ", ";
            Loop While j < nvar - 1 'And j < 7
            Print #3, Format(TheGroup.fGmean(i, nvar), "Fixed")
        Next i
        '
        '---------------------------
        'RESULT: Group Z Statistics
        '---------------------------
        Print #3, "<< Group Z Statistics >>"
        For i = 1 To TheGroup.ngrps
          '
                KK = 0
                For j = 1 To jobs
                        If TheGroup.member2(j) = i And ID <> 1 Then KK = KK + 1 '***is true anyway
                Next j
                '
                '------------------
                'calculate Z values
                DIV = CSng(KK)
                For j = 1 To nvar
                        SE(j) = SD(j) / Sqr(DIV)
                        TT(j) = TheGroup.fGmean(i, j) - TM(j)
                        '
                        ZT(i, j) = TT(j) / SE(j): 'Z values
                Next j
        Next i
        For i = 1 To TheGroup.ngrps
                '
                Print #3, "Group " & i & ", ";
                j = 0
                Do: j = j + 1
                        Print #3, Format(ZT(i, j), "Fixed") & ", ";
                Loop While j < nvar - 1 'And j < 7
                Print #3, Format(ZT(i, nvar), "Fixed")
                '
        Next i
99 End Sub

Sub RSstatistic(tineq, bineq, pineq, ixout%)
'
'calculate RS statistic
'
        If tineq > 0 Then
                pineq = bineq / tineq * 100#
                GoTo 32
        End If
        '
        pineq = 0#
        If bineq = 0 Then pineq = 100#
        ixout = 1
32
End Sub

Sub SAVEdata(Title$, CLtitle$(), RWTitle$(), statmx, jobs%, nvar%, member2%(), ng%, gmean(), sData(), totgrp, bineq, tineq, CHsstsse(), sstt, sset, Counter%)
        Dim k%
        Dim i%
        Dim j%
        Dim m%
        Dim N%
        Dim co%
        Dim CH, fCHpermF, fCHPermP
        Dim nSLen%
        Dim nFSlen%
        Dim nPos%
        Dim m1%
        Dim sDum$
        Dim sFilename$
        Dim fGroupOut()
        Dim nCounter%
        Dim dumGraph() As Variant
        Dim lLoopCnt As Long
        Dim fCHMax, nScaler%
        ReDim fGroupOut(jobs, nvar + 1)
        On Error GoTo errmsg
        Select Case nOutputType
        Case 0, 1
            m1 = 1
        Case 2
            m1 = 0
        End Select
        nCounter = -1
        For m = m1 To 1
        nCounter = nCounter + 1
            If (m = 0 And nOutputType = 2) Or nOutputType = 0 Then
                sFilename = sOutFilename
                Open sFilename For Append As #1 ' Else Open sFilename For Output As #1
            Else
                If (m = 1 And nOutputType = 2) Or nOutputType = 1 Then
                    nSLen = Len(sOutFileTitle)
                    nFSlen = Len(sOutFilename)
                    nPos = nFSlen - nSLen
                    sDum = Left(sOutFilename, nPos)

                    sFilename = ""
                    sFilename = sDum & ng & sOutFileTitle
                    Open sFilename For Output As #1
                End If
            End If
            'SAVE file's name and Title
            Print #1, sFilename
            Print #1, Title; ","; jobs; " samples"
            Print #1, "Data groupings for "; ng; " groups"
            '
            'SAVE Groups and data matrix
            '
            k = 0
            For i = 1 To ng
                'SAVE column's title
                co = 1
                Print #1,
                Print #1, "Group"; ",Sample,";
                Do: co = co + 1
                        Print #1, CLtitle(co); ", ";
                Loop While co < nvar + 1
                Print #1,
                        For j = 1 To jobs
                                If member2(j) = i Then
                                 k = k + 1
                                 fGroupOut(k, 1) = i
                                 Print #1, i; ", "; RWTitle(j);
                                  For N = 1 To nvar
                                    fGroupOut(k, N + 1) = sData(j, N)
                                  Print #1, ", "; sData(j, N);
                                  Next N
                                  Print #1,
                                End If
                        Next j: Print #1,
            Next i
            'only do for first pass
            If nCounter = 0 Then Call CHTest(fGroupOut(), jobs, nvar, ng, CH, sstt, sset, fCHpermF, _
            fCHPermP)
            Print #1, statmx; ", % explained"
            Print #1, "Total inequality"; tineq; "     Between region inequality"; bineq
            Print #1, "Total sum of squares: " & Prvsstt & " Within group sum of squares: " & Prvsset
            Print #1, "Calinski-Harabasz pseudo-F statistic: " & CH
            Print #1,
            Close #1
        Next m
        'not called in Rs case so call now, highest value of CH may be non unique
        'so call on stored CH set too
        CHsstsse(Counter, 1) = sstt
        CHsstsse(Counter, 2) = Prvsset
        CHsstsse(Counter, 3) = fCHpermF
        CHsstsse(Counter, 4) = fCHPermP
        CHsstsse(Counter, 5) = statmx
        CHsstsse(Counter, 6) = Counter
        MSChart1.Enabled = True
        RsGraph(Counter, 1) = ng
        Debug.Print ng
        RsGraph(Counter, 2) = CH
        RsGraph(Counter, 3) = statmx
        'Code to problem whereby converting "ng" to a string in Rs graph doesn't work. Decided just to
        'copy array contents to a new array and set it as variant there.
        ReDim dumGraph(0 To Counter, 1 To 3)
        fCHMax = 0
        For lLoopCnt = 0 To Counter
            dumGraph(lLoopCnt, 1) = " " & CStr(RsGraph(lLoopCnt, 1))
            dumGraph(lLoopCnt, 2) = RsGraph(lLoopCnt, 2)
            If dumGraph(lLoopCnt, 2) > fCHMax Then fCHMax = dumGraph(lLoopCnt, 2)
            dumGraph(lLoopCnt, 3) = RsGraph(lLoopCnt, 3)
        Next lLoopCnt
        'set the chart data
        MSChart1.ChartData = dumGraph
        'set the legend
        MSChart1.Column = 1
        MSChart1.ColumnLabel = "C-H"
        MSChart1.Column = 2
        MSChart1.ColumnLabel = "Rs"
        'plot second series on y-axis 2
        MSChart1.Plot.SeriesCollection(2).SecondaryAxis = True
        'set bounds for y1 scale
        nScaler = Int(fCHMax / 5) + 1
        MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.Minimum = 0
        MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.Maximum = nScaler * 5
        'refresh chart
        MSChart1.Refresh
        Exit Sub
errmsg: Beep
225 End Sub

Private Sub SetGroups(sData(), ng%, jobs%, nvar%, member1%(), fGroupOut())
Dim k%, i%, j%, N%
    k = 0
    For i = 1 To ng
        For j = 1 To jobs
            If member1(j) = i Then
                k = k + 1
                fGroupOut(k, 1) = i
                For N = 1 To nvar
                    fGroupOut(k, N + 1) = sData(j, N)
                Next N
            End If
        Next j
    Next i
End Sub

Sub SWITCHgroup(CLtitle$(), ixout%, jobs%, nvar%, ng%, member1%(), result(), sData(), mingrp%, tineq, bineq, pineq, Y(), TM(), SD(), intmed%, sumx())
'
'switch groups to find optimum
'
Dim i%
Dim j%
Dim NO&
Dim olstat
Dim icnt%
Dim ind%
Dim istore%
Dim G%
Dim member%
Dim statmx
Dim fGroupOut()
ReDim fGroupOut(jobs, nvar + 1)
        NO = 0
        olstat = 0
        icnt = 0
24      ind = 0
        For i = 1 To jobs 'for each sample
            For j = 1 To ng 'for the number of groups
                istore = member1(i) 'store the member value
                member1(i) = j 'update member
                ind = ind + 1
                    Call BETWEENinquality(jobs, nvar, ng, member1(), result(), sData(), Y(), bineq)
                    Call RSstatistic(tineq, bineq, pineq, ixout)
                    NO = NO + 1
    
                    If chkLog.Value = Checked Then
                        Print #2, "Calculation #"; NO; ": "; pineq; "%"
                        For G = 1 To ng
                              Print #2, "Group"; G; " {";
                              For member = 1 To jobs
                                      If member1(member) = G Then Print #2, member;
                              Next member
                              Print #2, "}"
                        Next G
                        Print #2,
                    End If
                    Call OPTIMALgroup(jobs, nvar, ng, result(), sData(), member1(), istore, olstat, pineq, mingrp, ind, i, sumx())
            Next j
        Next i
        If ind = 0 Then icnt = icnt + 1
        If icnt < 3 Then GoTo 24
        '
        'print all intermediate groups
        If intmed = 1 Then Call BESTgroup(statmx, ng, jobs, member1())
        '
        If chkLog.Value = Checked Then
            If ixout <> 1 Then
                Print #2, ng; " classes: ", pineq; "% explained"
            End If
            If ixout = 1 Then
                Print #2, ng, " classes: ", pineq; "% ", tineq, "total inequality", bineq, "between-region inequality"
            End If
        End If
End Sub

Sub TOTALinequality(jobs%, nvar%, result(), sData(), Y(), tineq)
        '
        'find total inequality: tineq
        '  note:equation (4) in page 5.
        '
        Dim JJ%
        Dim II%
        Dim j%
        Dim i%
        Dim X
        tineq = 0#
        For JJ = 1 To nvar
                Y(JJ) = 0#
        Next JJ
        For JJ = 1 To nvar
          For II = 1 To jobs
            Y(JJ) = Y(JJ) + result(II, JJ)
          Next II
        Next JJ
        For j = 1 To nvar
          X = 0#
          For i = 1 To jobs
            If result(i, j) > 0 Then
            X = X + (result(i, j) / Y(j)) * Log(CSng(jobs) * result(i, j) / Y(j)) / Log(2)
           
            Else
            End If
          Next i
            tineq = tineq + Y(j) * X
            If chkLog.Value = Checked Then Print #2, "Variable " & j & " total inequality is "; tineq
        Next j
End Sub

Private Sub CHTest(dat(), Samples%, Classes%, k%, CH, sstt, sset, fCHpermF, fCHPermP)
Dim totsum()
Dim totav()
Dim sst()
Dim clsum()
Dim clsam()
Dim clav()
Dim sse()
'Calculation of Calinski-Harabasz pseudo-F statistic"
Dim j%
Dim i%
Dim r
Dim permutations
Dim Countonce%
Dim Ch1
Dim p
Dim Chsum
Dim a%, b%, L%, G%, num%, nfilenum%
Dim tmp, tmp2
permutations = 0
Prvsstt = 0
Prvsset = 0
CHcode:
ReDim totsum(Classes)
ReDim totav(Classes)
ReDim sst(Classes)
ReDim clsum(Samples, Classes)
ReDim clsam(Samples)
ReDim clav(Samples, Classes)
ReDim sse(Samples, Classes)
sset = 0
sstt = 0

Countonce = 0
'nfilenum = FreeFile
'Open "c:\Temp\CHout.txt" For Append As #nfilenum
For j = 2 To Classes + 1
    For i = 1 To Samples
        If i = 1 Then Debug.Print j, dat(i, j);
        totsum(j - 1) = totsum(j - 1) + dat(i, j)
        clsum(dat(i, 1), j - 1) = clsum(dat(i, 1), j - 1) + dat(i, j)
        If Countonce = 0 Then
            clsam(dat(i, 1)) = clsam(dat(i, 1)) + 1 'calculates number of samples in each cluster
        End If
    Next i
    Debug.Print
    Countonce = 1
Next j
For i = 1 To Classes
    totav(i) = totsum(i) / Samples  'averages for total centroid
Next
On Error GoTo TrapEmptySet
For i = 1 To k  'averages within groups and classes
    For j = 1 To Classes
        clav(i, j) = clsum(i, j) / clsam(i)
    Next j
Next i

For j = 2 To Classes + 1  'calculate total sum of squares
    For i = 1 To Samples
        sst(j - 1) = sst(j - 1) + (dat(i, j) - totav(j - 1)) ^ 2
        sse(dat(i, 1), j - 1) = sse(dat(i, 1), j - 1) + (dat(i, j) - clav(dat(i, 1), j - 1)) ^ 2
        'Write #nfilenum, sst(j - 1), dat(i, j), totav(j - 1), (dat(i, j) - totav(j - 1)) ^ 2, sse(dat(i, 1), j - 1)
    Next i
    sstt = sstt + sst(j - 1)
    'Write #nfilenum, sstt

Next j
'Write #nfilenum, "sstt " & sstt
'Close #nfilenum
For i = 1 To k      'calculate total within group ss
    For j = 1 To Classes
        sset = sset + sse(i, j)
    Next j
Next i
r = (sstt - sset) / sstt
If r = 1 Then
    Debug.Print "Perfect classification, CH = infinity, no within group variability whatsoever!"
    GoTo noP
End If
If permutations < 1 Then
    CH = (r / (k - 1)) / ((1 - r) / (Samples - k))
    Prvsstt = sstt
    Prvsset = sset
    If chkPerm.Value = Unchecked Then GoTo noP
Else
    Ch1 = (r / (k - 1)) / ((1 - r) / (Samples - k))
    If Ch1 > CH Then p = p + 1
    Chsum = Chsum + Ch1
End If
a = 2
b = Classes + 1
For i = 1 To Samples    'Permutations here
    For G = a To b
        tmp = dat(i, G)
        num = Int(Rnd(1) * Classes) + 2
        tmp2 = dat(i, num)
        dat(i, num) = tmp
        dat(i, G) = tmp2
    Next G
    For G = a To b
        If i = 1 Then Debug.Print dat(i, G);
    Next G
    Debug.Print
Next i
permutations = permutations + 1
If permutations < 101 Then GoTo CHcode '101
fCHpermF = Chsum / permutations
fCHPermP = p / permutations
noP:
Exit Sub
TrapEmptySet:
CH = 0.1
End Sub

Public Sub FormUnloadEnd()
Dim nFrmCount As Integer
Dim i As Integer
   ' Loop through the forms collection and unload
   ' each form.
   nFrmCount = Forms.Count - 1
   For i = nFrmCount To 0 Step -1
      Unload Forms(i)
   Next i
End Sub

Private Sub cmdExit_Click()
Call FormUnloadEnd
End Sub

Private Sub cmdProceed_Click()
Call calculate
Call DisableFrames
End Sub

Private Sub Command2_Click()
'Select an input file
Dim bexit As Boolean
Call GetSaveFile(0, sInFilename, sinFileTitle, bexit)
If bexit Then Exit Sub
fraOutput.Enabled = True
cmdSavFile.Enabled = True
Option1(0).Enabled = True
Option1(1).Enabled = True
Option1(2).Enabled = True
End Sub

Private Sub cmdSavFile_Click()
Dim bexit As Boolean
bexit = False
Call GetSaveFile(1, sOutFilename, sOutFileTitle, bexit)
If bexit Then Exit Sub
cmdProceed.Enabled = True
End Sub

Private Sub Form_Load()
Dim axisID
Dim i%
Dim dumGraph(2 To 20, 1 To 3) As Variant
For i = 2 To 20
    dumGraph(i, 1) = " " & CStr(i)
    dumGraph(i, 2) = 0 ' i / 2
    dumGraph(i, 3) = 0.01 'i / 3
Next i
frmSplash.Show
Call DisableFrames
MSChart1.Plot.AutoLayout = False
MSChart1.Enabled = True
MSChart1.RandomFill = False
MSChart1.Plot.Axis(VtChAxisIdX).AxisTitle.Text = "Groups"
MSChart1.Plot.Axis(VtChAxisIdY).AxisTitle.Text = "C-H"
MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.Auto = False
MSChart1.Plot.Axis(VtChAxisIdY2).AxisTitle.Text = "Rs"
MSChart1.Plot.Axis(VtChAxisIdY2).ValueScale.Auto = False
MSChart1.Plot.Axis(VtChAxisIdY2).ValueScale.Minimum = 0
MSChart1.Plot.Axis(VtChAxisIdY2).ValueScale.Maximum = 100
MSChart1.ShowLegend = True
MSChart1.Legend.Location.LocationType = VtChLocationTypeBottomRight
MSChart1.TitleText = "Calinski-Harabasz pseudo-F and Rs statistics"
MSChart1.Title.VtFont.Size = 11
MSChart1.Plot.UniformAxis = False
MSChart1.Backdrop.Fill.Brush.FillColor.Automatic = False
' Sets Backdrop to Fill - Brush Style.
MSChart1.Backdrop.Fill.Style = VtFillStyleBrush
' Sets chart fill color to white.
With MSChart1.Backdrop.Fill.Brush.FillColor
   .Red = 255   ' Use properties to set color.
   .Green = 255
   .Blue = 255
End With
MSChart1 = dumGraph
'set the legend text
MSChart1.Column = 1
MSChart1.ColumnLabel = "C-H"
MSChart1.Column = 2
MSChart1.ColumnLabel = "Rs"
MSChart1.Plot.Axis(VtChAxisIdY).AxisGrid.MajorPen.Style = VtPenStyleDotted
MSChart1.Plot.Axis(VtChAxisIdX).AxisGrid.MajorPen.Style = VtPenStyleDotted
MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.Minimum = 0
MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.Maximum = 1
MSChart1.Plot.Axis(VtChAxisIdY).ValueScale.MajorDivision = 5
MSChart1.Plot.Axis(VtChAxisIdY2).ValueScale.MajorDivision = 5
frmSplash.SetFocus
End Sub
Private Sub DisableFrames()
fraOutput.Enabled = False
cmdProceed.Enabled = False
cmdSavFile.Enabled = False
Option1(0).Enabled = False
Option1(1).Enabled = False
Option1(2).Enabled = False
End Sub

Private Sub mnuAbout_Click()
        frmSplash.Timer1.Enabled = False
        frmSplash.Show
End Sub

Private Sub mnuContents_Click()
       'The return value is the window handle of the created help window.
        HtmlHelp hWnd, App.Path & "\EMAX.chm", HH_DISPLAY_TOPIC, ByVal "select.htm"
End Sub

Private Sub mnuExit_Click()
Call FormUnloadEnd
End Sub

Private Sub mnuOpen_Click()
Command2_Click
End Sub

Private Sub Option1_Click(Index As Integer)
'sets the public variable indicating desired output format
nOutputType = Index
End Sub
Private Sub mnuCopy_Click()
Clipboard.Clear
MSChart1.EditCopy
MsgBox "Use Edit-Paste Special in MS products to paste chart image.", vbInformation
End Sub
Private Sub mschart1_MouseUp(Button As Integer, Shift As _
   Integer, X As Single, Y As Single)
   If Button = 2 Then   ' Check if right mouse button
                        ' was clicked.
      PopupMenu mnuChrtOpt   ' Display the File menu as a
                        ' pop-up menu.
   End If
End Sub


