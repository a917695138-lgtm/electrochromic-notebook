$ErrorActionPreference = "SilentlyContinue"

function Show-StartupError($message) {
    try {
        $shell = New-Object -ComObject WScript.Shell
        $shell.Popup($message, 0, "Lab notebook startup failed", 16) | Out-Null
    } catch {
        Write-Host $message
    }
    exit 1
}

$NotebookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Server = Join-Path $NotebookDir "scripts\server.py"
$BaseUrl = "http://127.0.0.1:8765/"
$Url = "${BaseUrl}index.html"
$OutLog = Join-Path $NotebookDir "server-start.out.log"
$ErrLog = Join-Path $NotebookDir "server-start.err.log"

$running = $false
try {
    Invoke-WebRequest -UseBasicParsing $BaseUrl -TimeoutSec 3 | Out-Null
    $running = $true
} catch {
    $running = $false
}

if (-not $running) {
    $pythonPath = $null
    $pythonArgs = $null
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        $pythonPath = $py.Source
        $pythonArgs = @("-3", $Server)
    } elseif (Test-Path -LiteralPath "C:\Program Files\Python39\python.exe") {
        $pythonPath = "C:\Program Files\Python39\python.exe"
        $pythonArgs = @($Server)
    } else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python -and ($python.Source -notlike "*\WindowsApps\python.exe")) {
            $pythonPath = $python.Source
            $pythonArgs = @($Server)
        }
    }

    if (-not $pythonPath) {
        Show-StartupError "Could not find a real Python executable. Expected C:\Program Files\Python39\python.exe or the py launcher."
    }

    Start-Process -FilePath $pythonPath -ArgumentList $pythonArgs -WorkingDirectory $NotebookDir -WindowStyle Minimized -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog
    Start-Sleep -Seconds 3
}

try {
    Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 5 | Out-Null
} catch {
    Show-StartupError "The lab notebook server did not start at $Url.`n`nCheck logs:`n$OutLog`n$ErrLog"
}

Start-Process $Url
