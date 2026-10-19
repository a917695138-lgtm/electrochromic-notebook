$ErrorActionPreference = "Stop"

$NotebookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat = Join-Path $NotebookDir "open-notebook.bat"
$Root = "HKCU:\Software\Classes\pulsework"
$CommandKey = Join-Path $Root "shell\open\command"
$ComSpec = Join-Path $env:SystemRoot "System32\cmd.exe"

if (-not (Test-Path -LiteralPath $Bat -PathType Leaf)) {
    throw "Cannot find notebook launcher: $Bat"
}

$Command = '"' + $ComSpec + '" /d /s /c ""' + $Bat + '""'
if (Test-Path -LiteralPath $CommandKey) {
    $Existing = (Get-Item -LiteralPath $CommandKey).GetValue("")
    if ($Existing -and $Existing -ne $Command) {
        throw "pulsework protocol is already owned by another handler; no changes were made."
    }
}

New-Item -LiteralPath $Root -Force | Out-Null
Set-Item -LiteralPath $Root -Value "URL: Pulsework Notebook Protocol"
New-ItemProperty -LiteralPath $Root -Name "URL Protocol" -PropertyType String -Value "" -Force | Out-Null
New-Item -LiteralPath (Join-Path $Root "shell\open") -Force | Out-Null
New-Item -LiteralPath $CommandKey -Force | Out-Null
Set-Item -LiteralPath $CommandKey -Value $Command

Write-Host "Installed pulsework://notebook for the current Windows user."
Write-Host "Handler: $Bat"
Write-Host "The browser may ask for permission the first time the protocol is used."
