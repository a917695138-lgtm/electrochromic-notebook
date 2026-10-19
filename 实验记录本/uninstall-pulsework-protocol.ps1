$ErrorActionPreference = "Stop"

$NotebookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat = Join-Path $NotebookDir "open-notebook.bat"
$Root = "HKCU:\Software\Classes\pulsework"
$CommandKey = Join-Path $Root "shell\open\command"
$ComSpec = Join-Path $env:SystemRoot "System32\cmd.exe"
$Expected = '"' + $ComSpec + '" /d /s /c ""' + $Bat + '""'

if (-not (Test-Path -LiteralPath $Root)) {
    Write-Host "pulsework protocol is not installed for the current Windows user."
    exit 0
}

$Actual = ""
if (Test-Path -LiteralPath $CommandKey) {
    $Actual = (Get-Item -LiteralPath $CommandKey).GetValue("")
}
if ($Actual -ne $Expected) {
    throw "Current pulsework handler does not belong to this notebook installation; no changes were made."
}

Remove-Item -LiteralPath $Root -Recurse -Force
Write-Host "Removed pulsework://notebook for the current Windows user."
