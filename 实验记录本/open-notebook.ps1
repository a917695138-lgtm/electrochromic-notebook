$ErrorActionPreference = "SilentlyContinue"

$NotebookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Server = Join-Path $NotebookDir "scripts\server.py"
$Url = "http://localhost:8765/实验记录本.html"
$OutLog = Join-Path $NotebookDir "server-start.out.log"
$ErrLog = Join-Path $NotebookDir "server-start.err.log"

$running = $false
try {
    Invoke-WebRequest -UseBasicParsing "http://localhost:8765/" -TimeoutSec 1 | Out-Null
    $running = $true
} catch {
    $running = $false
}

if (-not $running) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        Start-Process -FilePath $py.Source -ArgumentList @("-3", $Server) -WorkingDirectory $NotebookDir -WindowStyle Minimized -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog
    } else {
        Start-Process -FilePath "python" -ArgumentList @($Server) -WorkingDirectory $NotebookDir -WindowStyle Minimized -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog
    }
    Start-Sleep -Seconds 2
}

Start-Process $Url
