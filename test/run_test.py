import os
import sys
import webbrowser
import subprocess
import time

def main():
    print("南开大学校园地图 - 测试工具")
    print("=" * 40)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查测试服务器文件是否存在
    server_file = os.path.join(current_dir, "test_server.py")
    if not os.path.exists(server_file):
        print("错误: 找不到测试服务器文件 test_server.py")
        return
    
    # 检查测试界面文件是否存在
    html_file = os.path.join(current_dir, "index.html")
    if not os.path.exists(html_file):
        print("错误: 找不到测试界面文件 index.html")
        return
    
    print("正在启动测试服务器...")
    
    # 启动测试服务器
    try:
        # 使用子进程启动服务器
        server_process = subprocess.Popen([sys.executable, server_file])
        
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(2)
        
        # 打开浏览器
        print("正在打开测试界面...")
        webbrowser.open("http://localhost:5001")
        
        print("\n测试环境已启动!")
        print("- 测试服务器运行在: http://localhost:5001")
        print("- 使用 Ctrl+C 停止测试服务器")
        
        # 等待用户中断
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n正在停止测试服务器...")
            server_process.terminate()
            server_process.wait()
            print("测试服务器已停止")
    
    except Exception as e:
        print(f"启动测试环境时出错: {str(e)}")

if __name__ == "__main__":
    main()