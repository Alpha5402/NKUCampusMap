from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os

# 创建Flask应用，并指定静态文件夹为当前目录
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # 启用CORS，允许前端页面访问

# 读取区域数据
def load_areas_data():
    try:
        # 尝试读取前端的Area.json文件
        with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('areas', [])
    except Exception as e:
        print(f"读取区域数据失败: {str(e)}")
        return []

# 调用DeepSeek API
def call_deepseek_api(prompt, system_prompt=""):
    """
    调用 DeepSeek API 处理用户输入
    
    Args:
        prompt (str): 用户输入的内容
        system_prompt (str, optional): 系统提示词
        
    Returns:
        str: AI 模型的输出
    """
    try:
        # 这里实现调用 DeepSeek API 的逻辑
        api_key = 'sk-427f6bb3cbca46d38cdd4cd5878ba955'  # 使用与主应用相同的API密钥
        if not api_key:
            return "未配置 DeepSeek API 密钥"
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt if system_prompt else "你是一个校园导航助手，请根据用户的问题提供南开大学津南校区的相关信息。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            print(f"DeepSeek API 调用失败: {response.status_code}, {response.text}")
            return f"AI 服务暂时不可用，请稍后再试 (错误码: {response.status_code})"
            
    except Exception as e:
        print(f"调用 DeepSeek API 出错: {str(e)}")
        return "处理请求时发生错误，请稍后再试"

# 处理提交请求
@app.route('/submit', methods=['POST'])
def handle_submit():
    # 从请求中获取 JSON 数据
    data = request.get_json()

    # 获取用户输入的内容
    user_input = data.get('content', '')
    
    if not user_input:
        return jsonify({
            "status": "error",
            "output": "未提供输入内容",
            "result_array": []
        })

    # 调用 AI 模型处理用户输入
    ai_output = call_deepseek_api(user_input)
    
    # 加载区域数据
    areas_data = load_areas_data()
    
    # 根据 AI 输出找到相关区域
    result_array = []
    for area in areas_data:
        # 如果区域名称或全名出现在 AI 输出中，则认为相关
        if (area.get('name', '') in ai_output or 
            area.get('fullName', '') in ai_output):
            if 'internal_id' in area:
                result_array.append(area['internal_id'])
            else:
                result_array.append(area.get('name', '未命名区域'))
    
    # 返回响应
    response = {
        "status": "success",
        "output": ai_output,
        "result_array": result_array
    }

    return jsonify(response)

# 提供静态文件
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # 确保静态文件目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("测试服务器已启动，请访问 http://localhost:5000")
    app.run(debug=True)