import os
import subprocess
import time
import webbrowser

print("启动 DeepSeek API 测试环境...")

# 启动服务器
server_process = subprocess.Popen(["python", "test_server.py"], 
                                 cwd=os.path.dirname(os.path.abspath(__file__)))

# 等待服务器启动
print("等待服务器启动...")
time.sleep(5)

# 打开默认浏览器访问测试页面
print("正在打开浏览器...")
webbrowser.open("http://localhost:5000")

print("测试环境已启动，请在浏览器中操作。")
print("按 Ctrl+C 关闭服务器...")

try:
    # 保持脚本运行，直到用户按下 Ctrl+C
    server_process.wait()
except KeyboardInterrupt:
    # 用户按下 Ctrl+C，关闭服务器
    server_process.terminate()
    print("服务器已关闭。")