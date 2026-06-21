@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  Codex Switch - 卸载
echo ========================================
echo.

:: 删除开机自启
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if exist "%STARTUP_DIR%\codex-adapter.bat" (
    del "%STARTUP_DIR%\codex-adapter.bat"
    echo ✅ 已删除开机自启项
) else (
    echo 未发现开机自启项
)

:: 提示恢复官方配置
echo.
set /p "RESTORE=是否恢复官方登录配置？(Y/N): "
if /i "%RESTORE%"=="Y" (
    python -m codex_switch.cli official
    echo ✅ 已恢复官方配置
)

echo.
echo ========================================
echo  卸载完成
echo ========================================
echo.
echo 项目文件未删除，如需清理请手动删除目录。
pause
