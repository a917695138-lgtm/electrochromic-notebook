param(
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "D:\Users\ao\Documents\电致变色"
$git = "C:\Program Files\Git\bin\git.exe"
$python = "C:\Program Files\Python39\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送实验记录本到 GitHub Pages" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] 同步数据..." -ForegroundColor Yellow
& $python "实验记录本\scripts\sync-data.py"
Write-Host ""

Write-Host "[2/3] 同步网页入口并提交..." -ForegroundColor Yellow
Copy-Item "实验记录本\index.html" "实验记录本\实验记录本.html" -Force
& $git add "实验记录本"
$status = & $git status --short
if ($status) {
    & $git commit -m "Auto-sync: update notebook data"
    Write-Host "  已提交更新"
} else {
    Write-Host "  无新变更"
}
Write-Host ""

Write-Host "[3/3] 推送到 GitHub..." -ForegroundColor Yellow
& $git push origin master
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  推送成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "  访问地址：" -ForegroundColor Cyan
    Write-Host "  https://a917695138-lgtm.github.io/electrochromic-notebook/?t=2" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "推送失败，请稍后重试或检查网络/GitHub 认证。" -ForegroundColor Red
    exit $LASTEXITCODE
}

if (-not $NoPause) {
    Read-Host "按 Enter 退出"
}
