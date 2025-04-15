import os

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS 扩展
import hashlib
import time

app = Flask(__name__)
CORS(app, origins=["https://www.nkucampusmap.xin/"])  # 启用 CORS 支持，允许所有来源的跨域请求
# CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api")
def home():
    return "Hello World!"

# 接收前端发送的消息
@app.route('/api/submit', methods=['POST'])
def receive_message():
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

# 替换为你的 App ID 和 App Secret

from flask import Flask, request, jsonify
import requests
import time
import hashlib
import os
from dotenv import load_dotenv

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
