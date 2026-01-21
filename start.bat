@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   航班查询调度器 - 启动服务
echo ========================================
echo.

echo 正在后台启动服务...

REM 使用 PowerShell 后台启动
powershell -Command "Start-Process -FilePath '%~dp0AirTicket.exe' -WorkingDirectory '%~dp0' -WindowStyle Hidden"

timeout /t 2 /nobreak >nul

REM 检查进程是否启动
tasklist | findstr /i "AirTicket.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ 服务已启动（后台运行）
) else (
    echo ❌ 服务启动失败，请检查日志
)

echo.
echo 查看日志: logs\scheduler.log
echo 停止服务: stop.bat
echo.
pause
