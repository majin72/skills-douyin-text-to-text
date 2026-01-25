@echo off
REM 自动检测并使用虚拟环境的启动脚本（Windows）

set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%venv

REM 检查虚拟环境是否存在
if not exist "%VENV_PATH%" (
    echo 虚拟环境不存在，正在创建...
    python "%SCRIPT_DIR%setup_venv.py"
    if errorlevel 1 exit /b 1
)

REM 获取虚拟环境中的Python路径
if exist "%VENV_PATH%\Scripts\python.exe" (
    set PYTHON_CMD=%VENV_PATH%\Scripts\python.exe
) else (
    echo ❌ 无法找到虚拟环境中的Python
    exit /b 1
)

REM 运行主脚本
"%PYTHON_CMD%" "%SCRIPT_DIR%parse_douyin_video.py" %*
