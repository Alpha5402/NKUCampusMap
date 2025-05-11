import os

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS 扩展
import hashlib
import time
from dotenv import load_dotenv
import json
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

# --- Pydantic 模型定义 ---
class LocationInfo(BaseModel):
    name: str = Field(..., description="地点的标准名称")
    description: str = Field(..., description="关于地点的详细描述")
    features: List[str] = Field(default_factory=list, description="地点的显著特点列表")

app = Flask(__name__)
CORS(app, origins=["https://www.nkucampusmap.xin/"])  # 启用 CORS 支持，允许所有来源的跨域请求
# CORS(app, resources={r"/*": {"origins": "*"}})

# 加载环境变量
load_dotenv()
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')
FEISHU_HOST = "https://open.feishu.cn"

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

# 读取区域数据
def load_areas_data():
    try:
        # 尝试读取前端的Area.json文件
        with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('areas', [])
    except Exception as e:
        print(f"读取区域数据失败: {str(e)}")
        return []

@app.route('/api/submit', methods=['POST'])
def handle_submit():
    # 从请求中获取 JSON 数据
    data = request.get_json()

    # 获取用户输入的内容
    user_input = data.get('content', '')
    
    if not user_input:
        return jsonify({
            "status": "error",
            "output": "未提供输入内容",
            "result_array": [],
            "structured_output": None
        })

    # 调用AI模型处理用户输入
    ai_raw_output, ai_structured_output = call_deepseek_api(user_input)

    # 加载区域数据
    areas_data = load_areas_data()
    result_array = []
    
    # 改进区域匹配逻辑
    if ai_structured_output and ai_structured_output.name != "无法处理的请求" and ai_structured_output.name != "解析失败" and ai_structured_output.name != "API调用失败" and ai_structured_output.name != "处理异常":
        location_name = ai_structured_output.name.lower()
        location_desc = ai_structured_output.description.lower()
        
        # 打印调试信息
        print(f"正在匹配地点: {location_name}")
        print(f"可用区域数量: {len(areas_data)}")
        
        for area in areas_data:
            area_name = area.get('name', '').lower()
            area_fullname = area.get('fullName', '').lower()
            
            # 更全面的匹配逻辑
            if (area_name in location_name or 
                area_fullname in location_name or 
                location_name in area_name or 
                location_name in area_fullname or
                area_name in location_desc or
                area_fullname in location_desc):
                
                if 'internal_id' in area:
                    result_array.append(area['internal_id'])
                    print(f"匹配到区域: {area.get('name')} (ID: {area['internal_id']})")
                else:
                    result_array.append(area.get('name', '未命名区域'))
                    print(f"匹配到区域: {area.get('name')} (无ID)")
    
    # 如果结构化匹配没有结果，尝试使用原始文本匹配
    if not result_array:
        print("结构化匹配未找到结果，尝试原始文本匹配")
        raw_text = ai_raw_output.lower()
        for area in areas_data:
            area_name = area.get('name', '').lower()
            area_fullname = area.get('fullName', '').lower()
            
            if area_name in raw_text or area_fullname in raw_text:
                if 'internal_id' in area:
                    result_array.append(area['internal_id'])
                    print(f"原始文本匹配到区域: {area.get('name')} (ID: {area['internal_id']})")
                else:
                    result_array.append(area.get('name', '未命名区域'))
                    print(f"原始文本匹配到区域: {area.get('name')} (无ID)")

    # 返回响应
    response_data = {
        "status": "success",
        "output": ai_raw_output,
        "result_array": result_array,
        "structured_output": ai_structured_output.dict() if ai_structured_output else None
    }

    return jsonify(response_data)

def call_deepseek_api(prompt, system_prompt=""):
    """
    调用 DeepSeek API 处理用户输入，并尝试解析为结构化数据。

    Args:
        prompt (str): 用户输入的内容
        system_prompt (str, optional): 系统提示词

    Returns:
        tuple: (原始文本输出, 解析后的 Pydantic 对象或 None)
    """
    raw_output = ""
    parsed_data = None
    try:
        api_key = 'sk-427f6bb3cbca46d38cdd4cd5878ba955' # 替换为你的 DeepSeek API Key
        if not api_key:
            return "未配置 DeepSeek API 密钥", None

        # --- 构建请求 DeepSeek 的 Payload ---
        # 改进提示词，使其更加明确和具体
        structured_prompt = (
            f"你是南开大学津南校区的导航助手。请分析用户的问题：\"{prompt}\"，并提取相关的地点信息。\n\n"
            f"请严格按照以下 JSON 格式返回信息，不要添加任何额外的文本、解释或代码块标记：\n"
            "{\n"
            '  "name": "地点的准确名称（如南开大学图书馆、八里台校区等）",\n'
            '  "description": "详细描述该地点的位置、功能和重要信息",\n'
            '  "features": ["该地点的特点1", "特点2", "特点3"]\n'
            "}\n\n"
            f"重要提示：\n"
            f"1. 只返回JSON对象本身，不要包含任何其他文本\n"
            f"2. 如果问题与南开大学津南校区的地点无关，请返回：\n"
            "{\n"
            '  "name": "无法处理的请求",\n'
            '  "description": "您的问题与南开大学津南校区的地点无关，请询问校园内的具体地点。",\n'
            '  "features": []\n'
            "}\n"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是南开大学津南校区的专业导航助手。你的任务是提供校园内各地点的准确信息，并严格按照要求的JSON格式返回。"},
                {"role": "user", "content": structured_prompt}
            ],
            "temperature": 0.3, # 降低温度以获得更确定性的输出
            "max_tokens": 1000
        }

        print(f"发送请求到DeepSeek API，提示词：{prompt}")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        # --- 处理 DeepSeek 响应 ---
        if response.status_code == 200:
            response_json = response.json()
            raw_output = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"DeepSeek原始响应: {raw_output}")

            # --- 尝试用 Pydantic 解析 ---
            try:
                # 清理可能的前缀和后缀文本
                cleaned_output = raw_output.strip()
                # 如果输出被Markdown代码块包围，去除它们
                if cleaned_output.startswith("```json") and cleaned_output.endswith("```"):
                    cleaned_output = cleaned_output[7:-3].strip()
                elif cleaned_output.startswith("```") and cleaned_output.endswith("```"):
                    cleaned_output = cleaned_output[3:-3].strip()
                
                # 尝试直接解析清理后的输出
                parsed_data = LocationInfo.parse_raw(cleaned_output)
                print("成功解析DeepSeek输出为Pydantic模型")
            except (ValidationError, json.JSONDecodeError) as e:
                print(f"直接解析失败: {e}")
                # 尝试从输出中提取JSON部分
                try:
                    json_start = raw_output.find('{')
                    json_end = raw_output.rfind('}')
                    if json_start != -1 and json_end != -1:
                        json_str = raw_output[json_start:json_end+1]
                        print(f"提取的JSON字符串: {json_str}")
                        parsed_data = LocationInfo.parse_raw(json_str)
                        print("从原始输出中提取并成功解析JSON")
                    else:
                        print("在原始输出中未找到有效的JSON结构")
                except Exception as inner_e:
                    print(f"尝试提取JSON后解析仍然失败: {inner_e}")
                    # 如果所有解析尝试都失败，创建一个默认的结构化输出
                    parsed_data = LocationInfo(
                        name="解析失败",
                        description=f"无法从AI响应中提取结构化数据。原始响应: {raw_output[:100]}...",
                        features=["请尝试重新提问，使用更明确的地点描述"]
                    )

        else:
            error_msg = f"DeepSeek API调用失败: {response.status_code}, {response.text}"
            print(error_msg)
            raw_output = f"AI服务暂时不可用，请稍后再试 (错误码: {response.status_code})"
            # 创建一个错误的结构化输出
            parsed_data = LocationInfo(
                name="API调用失败",
                description=f"无法连接到DeepSeek API。错误码: {response.status_code}",
                features=["请检查网络连接", "确认API密钥是否有效", "稍后再试"]
            )

    except Exception as e:
        error_msg = f"调用DeepSeek API或解析时出错: {str(e)}"
        print(error_msg)
        raw_output = "处理请求时发生错误，请稍后再试"
        # 创建一个异常的结构化输出
        parsed_data = LocationInfo(
            name="处理异常",
            description=f"处理请求时发生异常: {str(e)}",
            features=["请稍后再试"]
        )

    return raw_output, parsed_data

# 添加一个路由处理导航请求
@app.route('/api/route', methods=['GET', 'POST'])
def handle_route():
    if request.method == 'POST':
        data = request.get_json()
        start_point = data.get('start', {})
        end_point = data.get('end', {})
        
        # 这里可以实现路径规划逻辑
        # 简单示例：返回起点和终点信息
        return jsonify({
            "status": "success",
            "route": {
                "start": start_point,
                "end": end_point,
                "distance": "计算的距离",
                "duration": "预计时间",
                "steps": []  # 路径步骤
            }
        })
    else:
        # GET 请求返回示例路径数据
        return jsonify({
            "status": "success",
            "routes": [
                {
                    "name": "图书馆到教学楼",
                    "distance": "500米",
                    "duration": "约5分钟"
                },
                {
                    "name": "宿舍到食堂",
                    "distance": "300米",
                    "duration": "约3分钟"
                }
            ]
        })