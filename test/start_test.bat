@echo off
echo 启动DeepSeek API测试环境...
cd /d %~dp0

:: 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 系统找不到Python。请确保Python已安装并添加到PATH环境变量中。
    pause
    exit /b 1
)

:: 启动服务器
echo 正在启动服务器...
start python test_server.py

:: 等待服务器启动
echo 等待服务器启动...
timeout /t 5 /nobreak > nul

:: 打开默认浏览器访问测试页面
echo 正在打开浏览器...
start http://localhost:5000

echo 测试环境已启动，请在浏览器中操作。
echo 按任意键关闭此窗口...
pause > nul
