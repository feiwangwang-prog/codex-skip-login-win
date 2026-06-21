@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  Codex Switch - 一键安装（Windows）
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 获取脚本所在目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

:: 安装依赖（纯标准库，这步几乎秒过）
echo [1/3] 安装依赖...
pip install -r "%PROJECT_DIR%\requirements.txt" --quiet 2>nul
if %errorlevel% neq 0 (
    echo [警告] pip 安装失败，但本项目使用纯标准库，不影响使用
)

:: 创建 GUI 启动脚本（如果不存在）
echo [2/3] 创建快捷方式...
if not exist "%PROJECT_DIR%\run_gui.bat" (
    (
        echo @echo off
        echo cd /d "%PROJECT_DIR%"
        echo python -m codex_switch.gui
        echo pause
    ) > "%PROJECT_DIR%\run_gui.bat"
)

:: 注册开机自启适配器（可选）
echo.
echo [3/3] 开机自启设置
echo.
set /p "AUTO_START=是否注册适配器开机自启？(Y/N): "
if /i "%AUTO_START%"=="Y" (
    set /p "ADAPTER_URL=请输入上游 API 地址: "
    set /p "ADAPTER_MODEL=请输入模型 ID: "
    set /p "ADAPTER_KEY=请输入 API Key: "

    :: 在 Startup 文件夹创建 .bat
    set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    (
        echo @echo off
        echo cd /d "%PROJECT_DIR%"
        echo python -m codex_switch.cli adapter --base-url "%ADAPTER_URL%" --model "%ADAPTER_MODEL%" --api-key "%ADAPTER_KEY%"
    ) > "%STARTUP_DIR%\codex-adapter.bat"

    echo ✅ 已注册开机自启: %STARTUP_DIR%\codex-adapter.bat
) else (
    echo 跳过开机自启设置
)

echo.
echo ========================================
echo  安装完成！
echo ========================================
echo.
echo 使用方式：
echo   GUI:     双击 run_gui.bat
echo   CLI:     python -m codex_switch.cli --help
echo   状态:    python -m codex_switch.cli status
echo.
pause
