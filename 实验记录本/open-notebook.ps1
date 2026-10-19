$ErrorActionPreference = "Stop"

function Show-StartupError($message) {
    try {
        Add-Type -AssemblyName PresentationFramework -ErrorAction SilentlyContinue
        [System.Windows.MessageBox]::Show($message, "Lab notebook startup failed") | Out-Null
    } catch {
        Write-Host $message
    }
    exit 1
}

$NotebookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Server = Join-Path $NotebookDir "scripts\server.py"
$HealthUrl = "http://127.0.0.1:8765/api/health"
$Url = "http://127.0.0.1:8765/index.html"
$OutLog = Join-Path $NotebookDir "server-start.out.log"
$ErrLog = Join-Path $NotebookDir "server-start.err.log"

function Test-NotebookServer {
    try {
        $response = Invoke-WebRequest -UseBasicParsing $HealthUrl -TimeoutSec 2
        if (-not $response.Content) { return $false }
        $payload = $response.Content | ConvertFrom-Json
        return $payload.ok -eq $true -and $payload.app -eq "electrochromic-notebook"
    } catch {
        return $false
    }
}

if (-not (Test-NotebookServer)) {
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
        Show-StartupError "Could not find a real Python executable. Expected the py launcher or C:\Program Files\Python39\python.exe."
    }

    Start-Process -FilePath $pythonPath -ArgumentList $pythonArgs -WorkingDirectory $NotebookDir -WindowStyle Minimized -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 250
        if (Test-NotebookServer) { $ready = $true; break }
    }
    if (-not $ready) {
        Show-StartupError "The lab notebook server did not pass its health check at $HealthUrl.`n`nCheck logs:`n$OutLog`n$ErrLog"
    }
}

try {
    Start-Process $Url
} catch {
    Show-StartupError "The lab notebook server is ready, but the browser could not be opened.`n$Url"
}
