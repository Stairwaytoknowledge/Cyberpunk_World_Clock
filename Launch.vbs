' Cyberpunk World Clock launcher.
' Runs main_qt.py through pythonw.exe (no console window).
'
' Resolution order:
'   1. <folder>\runtime\pythonw.exe   (shipped inside the release bundle)
'   2. pythonw.exe on PATH            (dev machines that have Python installed)
' Falls back to a clear error dialog if neither is available.

Option Explicit

Dim shell, fso, here, pyw, main, cmd
Set shell = CreateObject("WScript.Shell")
Set fso   = CreateObject("Scripting.FileSystemObject")

here = fso.GetParentFolderName(WScript.ScriptFullName)
main = here & "\main_qt.py"

If Not fso.FileExists(main) Then
    MsgBox "main_qt.py not found next to Launch.vbs." & vbCrLf & _
           "Make sure the whole folder was extracted.", vbExclamation, "Cyberpunk Clock"
    WScript.Quit 1
End If

' Prefer the bundled runtime
pyw = here & "\runtime\pythonw.exe"
If fso.FileExists(pyw) Then
    cmd = """" & pyw & """ """ & main & """"
Else
    ' Dev-mode fallback: use whichever pythonw is on PATH
    cmd = "pythonw.exe """ & main & """"
End If

shell.CurrentDirectory = here

' Run hidden (window state 0), do NOT wait for the app to finish
On Error Resume Next
shell.Run cmd, 0, False
If Err.Number <> 0 Then
    MsgBox "Could not start Cyberpunk Clock." & vbCrLf & vbCrLf & _
           "Install Python from https://python.org, or run Install.bat from a " & _
           "release bundle.", vbExclamation, "Cyberpunk Clock"
    WScript.Quit 1
End If
