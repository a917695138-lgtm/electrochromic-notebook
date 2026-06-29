@echo off
chcp 65001 >nul
set "NOTEBOOK_DIR=%~dp0"
set "SERVER=%NOTEBOOK_DIR%scripts\server.py"
set "URL=http://localhost:8765/%E5%AE%9E%E9%AA%8C%E8%AE%B0%E5%BD%95%E6%9C%AC.html"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$running=$false; try { Invoke-WebRequest -UseBasicParsing 'http://localhost:8765/' -TimeoutSec 1 | Out-Null; $running=$true } catch {}; if (-not $running) { Start-Process -FilePath 'py' -ArgumentList @('-3', $env:SERVER) -WorkingDirectory $env:NOTEBOOK_DIR -WindowStyle Minimized; Start-Sleep -Seconds 2 }; Start-Process $env:URL"
