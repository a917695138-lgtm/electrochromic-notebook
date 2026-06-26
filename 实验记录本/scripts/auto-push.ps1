# auto-push.ps1 - File watcher that auto-syncs and pushes on changes
$ErrorActionPreference = "Stop"
$projectDir = "D:\Users\ao\Documents\电致变色\实验记录本"
$git = "C:\Program Files\Git\bin\git.exe"
$python = "C:\Program Files\Python39\python.exe"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $projectDir
$watcher.Filter = "*.md"
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::CreationTime
$watcher.EnableRaisingEvents = $false

$script:lastSync = Get-Date
$script:debounceMs = 3000  # wait 3s after last change before syncing

$action = {
    $now = Get-Date
    if (($now - $script:lastSync).TotalMilliseconds -lt $script:debounceMs) { return }
    $script:lastSync = $now
    Start-Sleep -Milliseconds $script:debounceMs

    Set-Location $projectDir
    Write-Host "$(Get-Date -Format 'HH:mm:ss') 检测到文件变更，同步中..." -ForegroundColor Yellow

    # Sync data
    & $python scripts\sync-data.py 2>&1 | Out-Null
    Copy-Item "index.html" "实验记录本.html" -Force

    # Commit
    & $git add . 2>&1 | Out-Null
    $status = & $git status --short
    if ($status) {
        & $git commit -m "Auto-sync: experiment update" 2>&1 | Out-Null
        Write-Host "$(Get-Date -Format 'HH:mm:ss') 已提交，推送中..." -ForegroundColor Yellow
        & $git push origin master 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$(Get-Date -Format 'HH:mm:ss') 推送成功！" -ForegroundColor Green
        } else {
            Write-Host "$(Get-Date -Format 'HH:mm:ss') 推送失败，请手动运行 push-to-github.bat" -ForegroundColor Red
        }
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  实验记录本自动推送监控已启动" -ForegroundColor Cyan
Write-Host "  检测到 .md 文件变更时自动同步并推送" -ForegroundColor Cyan
Write-Host "  关闭此窗口即停止监控" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $watcher.Dispose()
}



