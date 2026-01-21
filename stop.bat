@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   航班查询调度器 - 停止服务
echo ========================================
echo.

echo 正在停止服务...
taskkill /F /IM AirTicket.exe >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✓ 服务已停止
) else (
    echo ⚠ 服务未运行或已停止
)

echo.
pause
