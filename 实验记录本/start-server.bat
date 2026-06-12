@echo off
chcp 65001 >nul
cd /d "D:\Users\ao\Documents\电致变色\实验记录本"
echo 正在启动实验记录本服务器...
"C:\Program Files\Python39\python.exe" scripts\server.py
pause
