$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location (Split-Path -Parent $PSScriptRoot)
$git = "C:\Program Files\Git\bin\git.exe"
$python = "C:\Program Files\Python39\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送实验记录本到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Sync data
Write-Host "[1/3] 同步数据..." -ForegroundColor Yellow
& $python scripts\sync-data.py
Write-Host ""

# Step 2: Sync index.html
Write-Host "[2/3] 同步 index.html..." -ForegroundColor Yellow
Copy-Item "实验记录本.html" "index.html" -Force
& $git add data.js db-data.json index.html
$status = & $git status --short
if ($status) {
    & $git commit -m "Auto-sync: update data.js and index.html"
    Write-Host "  已提交更新"
} else {
    Write-Host "  无新变更"
}
Write-Host ""

# Step 3: Push
Write-Host "[3/3] 推送到 GitHub..." -ForegroundColor Yellow
try {
    & $git push origin master
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  推送成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "  手机访问：" -ForegroundColor Cyan
        Write-Host "  https://a917695138-lgtm.github.io/electrochromic-notebook/" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Green
    }
} catch {
    Write-Host "推送失败: $_" -ForegroundColor Red
}

Read-Host "按 Enter 退出"


