import os

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS 扩展
import hashlib
import time
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, origins=["https://www.nkucampusmap.xin/"])  # 启用 CORS 支持，允许所有来源的跨域请求
# CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api")
def home():
    return "Hello World!"

@app.route('/api/get_security_key')
def get_security_key():
    security_js_code = get_security_code()
    api_key = get_api_key()
    return jsonify({'security_code': security_js_code, 'api_key': api_key})

def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token"), data.get("expire")
    else:
        raise Exception(f"Failed to get tenant_access_token: {data.get('msg')}")



# 加载环境变量
load_dotenv()
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')
FEISHU_HOST = "https://open.feishu.cn"

# 获取 tenant_access_token
def get_tenant_access_token():
    url = f"{FEISHU_HOST}/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json = payload)
    response_data = response.json()
    return response_data.get("tenant_access_token")

# 获取 jsapi_ticket
def get_jsapi_ticket(tenant_access_token):
    url = f"{FEISHU_HOST}/open-apis/jssdk/ticket/get"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    response_data = response.json()
    return response_data.get("data", {}).get("ticket")

# 生成签名
def generate_signature(jsapi_ticket, nonce_str, timestamp, url):
    verify_str = f"jsapi_ticket={jsapi_ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={url}"
    signature = hashlib.sha1(verify_str.encode("utf-8")).hexdigest()
    return signature

@app.route("/api/get_config_parameters", methods=["GET"])
def get_config_parameters():
    # 获取前端传递的 URL
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    # 获取 tenant_access_token
    tenant_access_token = get_tenant_access_token()
    if not tenant_access_token:
        return jsonify({"error": "Failed to get tenant_access_token"}), 500

    # 获取 jsapi_ticket
    jsapi_ticket = get_jsapi_ticket(tenant_access_token)
    if not jsapi_ticket:
        return jsonify({"error": "Failed to get jsapi_ticket"}), 500

    # 生成签名
    nonce_str = "randomString12345"  # 随机字符串，可自行生成
    timestamp = int(time.time() * 1000)  # 当前时间戳，毫秒级
    signature = generate_signature(jsapi_ticket, nonce_str, timestamp, url)

    # print("APP_ID" + APP_ID)
    # print("SIGNATURE" + signature)
    # print("noncestr" + nonce_str)
    # print("timestamp" + str(timestamp))
    # 返回鉴权参数
    return jsonify({
        "appId": APP_ID,
        "signature": signature,
        "noncestr": nonce_str,
        "timestamp": timestamp
    })

def get_security_code():
    security_key = os.environ.get('AMAP_SECURITY_CODE')
    return security_key

def get_api_key():
    api_key = os.environ.get('AMAP_API_KEY')
    return api_key

if __name__ == '__main__':
    app.run(debug=True)

# TODO

@app.route('/api/submit', methods=['POST'])
def handle_sumbit():
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
    
    # 根据 AI 输出，找到相关区域的内部 ID
    # 从 Area.json 中读取区域数据
    areas_data = []
    try:
        # 假设前端的 Area.json 文件路径
        import json
        with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
            areas_data = json.load(f).get('areas', [])
    except Exception as e:
        print(f"读取区域数据失败: {str(e)}")
    
    # 根据 AI 输出找到相关区域
    result_array = []
    for area in areas_data:
        # 这里需要根据实际情况实现相关性判断逻辑
        # 简单示例：如果区域名称或全名出现在 AI 输出中，则认为相关
        if 'internal_id' in area and (
            area.get('name', '') in ai_output or 
            area.get('fullName', '') in ai_output
        ):
            result_array.append(area['internal_id'])
    
    # 返回符合 API 文档要求的响应
    response = {
        "status": "success",
        "output": ai_output,
        "result_array": result_array
    }

    return jsonify(response)

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
        # 示例代码，需要根据实际 API 进行修改
        api_key = os.environ.get('DEEPSEEK_API_KEY')
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
            return f"AI 服务暂时不可用，请稍后再试"
            
    except Exception as e:
        print(f"调用 DeepSeek API 出错: {str(e)}")
        return "处理请求时发生错误，请稍后再试"

# TODO
"""
- /api/info 
	- Receive
		- full_name (String)   the full name of the target area
	- Response
		- status (String)   status of response
		- output (String)   output from ai
"""
@app.route('/api/info', methods=['POST'])
def handle_get_info():
    # 从请求中获取 JSON 数据
    data = request.get_json()

    # 打印接收到的消息
    print("Received message:", data)

    # 返回一个响应给前端
    response = {
        "status": "success",
        "message": "Message received successfully",
        "received_data": data
    }

    return jsonify(response)