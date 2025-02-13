import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS 扩展

app = Flask(__name__)
CORS(app, origins=["http://localhost:5174"])  # 启用 CORS 支持，允许所有来源的跨域请求

# 接收前端发送的消息
@app.route('/submit', methods=['POST'])
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

@app.route('/get_security_key')
def get_security_key():
    security_js_code = get_security_code()
    api_key = get_api_key();
    return jsonify({'security_code': security_js_code, 'api_key': api_key})

def get_security_code():
    security_key = os.environ.get('AMAP_SECURITY_CODE')
    return security_key

def get_api_key():
    api_key = os.environ.get('AMAP_API_KEY')
    return api_key

if __name__ == '__main__':
    app.run(debug=True)
