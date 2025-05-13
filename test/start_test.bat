@echo off
echo 启动南开大学校园地图测试环境...
echo.
echo 请确保已安装 Python 和必要的依赖包
echo 如果尚未安装，请运行: pip install flask flask-cors requests pydantic
echo.
python test_server.py
pause