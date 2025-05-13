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
# load_dotenv()
# APP_ID = os.environ.get('APP_ID')
# APP_SECRET = os.environ.get('APP_SECRET')
# FEISHU_HOST = "https://open.feishu.cn"
#
# @app.route('/api/get_security_key')
# def get_security_key():
#     security_js_code = get_security_code()
#     api_key = get_api_key()
#     return jsonify({'security_code': security_js_code, 'api_key': api_key})
#
# def get_tenant_access_token(app_id, app_secret):
#     url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
#     payload = {
#         "app_id": app_id,
#         "app_secret": app_secret
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()
#     if data.get("code") == 0:
#         return data.get("tenant_access_token"), data.get("expire")
#     else:
#         raise Exception(f"Failed to get tenant_access_token: {data.get('msg')}")
#
# # 获取 tenant_access_token
# def get_tenant_access_token():
#     url = f"{FEISHU_HOST}/open-apis/auth/v3/tenant_access_token/internal"
#     payload = {
#         "app_id": APP_ID,
#         "app_secret": APP_SECRET
#     }
#     response = requests.post(url, json = payload)
#     response_data = response.json()
#     return response_data.get("tenant_access_token")
#
# # 获取 jsapi_ticket
# def get_jsapi_ticket(tenant_access_token):
#     url = f"{FEISHU_HOST}/open-apis/jssdk/ticket/get"
#     headers = {
#         "Authorization": f"Bearer {tenant_access_token}",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(url, headers=headers)
#     response_data = response.json()
#     return response_data.get("data", {}).get("ticket")
#
# # 生成签名
# def generate_signature(jsapi_ticket, nonce_str, timestamp, url):
#     verify_str = f"jsapi_ticket={jsapi_ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={url}"
#     signature = hashlib.sha1(verify_str.encode("utf-8")).hexdigest()
#     return signature
#
# @app.route("/api/get_config_parameters", methods=["GET"])
# def get_config_parameters():
#     # 获取前端传递的 URL
#     url = request.args.get("url")
#     if not url:
#         return jsonify({"error": "Missing URL parameter"}), 400
#
#     # 获取 tenant_access_token
#     tenant_access_token = get_tenant_access_token()
#     if not tenant_access_token:
#         return jsonify({"error": "Failed to get tenant_access_token"}), 500
#
#     # 获取 jsapi_ticket
#     jsapi_ticket = get_jsapi_ticket(tenant_access_token)
#     if not jsapi_ticket:
#         return jsonify({"error": "Failed to get jsapi_ticket"}), 500
#
#     # 生成签名
#     nonce_str = "randomString12345"  # 随机字符串，可自行生成
#     timestamp = int(time.time() * 1000)  # 当前时间戳，毫秒级
#     signature = generate_signature(jsapi_ticket, nonce_str, timestamp, url)
#
#     # 返回鉴权参数
#     return jsonify({
#         "appId": APP_ID,
#         "signature": signature,
#         "noncestr": nonce_str,
#         "timestamp": timestamp
#     })
#
# def get_security_code():
#     security_key = os.environ.get('AMAP_SECURITY_CODE')
#     return security_key
#
# def get_api_key():
#     api_key = os.environ.get('AMAP_API_KEY')
#     return api_key
#


# 模拟区域数据 - 添加到 app.py 中
MOCK_AREAS = [
    {"name": "图书馆", "fullName": "南开大学津南校区图书馆", "internal_id": "lib001"},
    {"name": "食堂", "fullName": "南开大学津南校区学生食堂", "internal_id": "canteen001"},
    {"name": "体育馆", "fullName": "南开大学津南校区体育馆", "internal_id": "gym001"},
    {"name": "宿舍", "fullName": "南开大学津南校区学生宿舍", "internal_id": "dorm001"}
]

# 模拟详情数据库 - 替代原有的 location_detail_db
location_detail_db = {
    "食堂": {
        "name": "南开大学津南校区学生食堂",
        "location": "位于校区中心区域，靠近学生宿舍区和教学区",
        "description": "南开大学津南校区学生食堂提供多种菜系，价格实惠，环境整洁。",
        "features": ["提供多种菜系", "价格实惠", "环境整洁"],
        "opening_hours": "早餐: 6:30-9:00, 午餐: 11:00-13:30, 晚餐: 17:00-19:30",
        "services": ["堂食", "打包", "校园卡支付"],
        "tips": ["高峰时段可能拥挤", "建议错峰就餐"],
        "nearby": ["宿舍楼", "教学楼", "便利店"]
    },
    "图书馆": {
        "name": "南开大学津南校区图书馆",
        "location": "校区中心位置，靠近行政楼和主教学楼",
        "description": "南开大学津南校区图书馆藏书丰富，环境安静，设施完善。",
        "features": ["藏书丰富", "现代化设施", "安静学习环境"],
        "opening_hours": "周一至周日 8:00-23:00",
        "services": ["图书借阅", "自习室", "电子资源", "研讨室"],
        "tips": ["需要校园卡进入", "保持安静"],
        "nearby": ["世纪华联超市", "大通学生活动中心", "教学楼"]
    },
    "体育馆": {
        "name": "津南校区体育馆",
        "location": "校区西北部，靠近西门",
        "description": "南开大学津南校区体育馆设施齐全，包括篮球场、游泳池、健身房等。",
        "features": ["设施齐全", "专业场地", "多功能区域"],
        "opening_hours": "8:00~22:00",
        "services": ["篮球场", "游泳池", "健身房", "羽毛球馆", "乒乓球场", "排球馆", "体育舞蹈教室"],
        "tips": ["部分设施需要预约", "需携带运动装备", "进入场馆需刷脸"],
        "nearby": ["主体育场", "文科操场", "学生活动中心"]
    }
}

# 添加模拟 AI 响应函数
def mock_ai_response(query):
    """
    模拟 AI 响应，根据查询文本返回预设答案
    """
    query = query.lower()
    if "图书馆" in query:
        return (
            "南开大学津南校区图书馆位于校区中心位置，是学生学习和查阅资料的主要场所。图书馆藏书丰富，环境安静，设施完善。",
            LocationInfo(
                name="南开大学津南校区图书馆",
                description="位于校区中心位置，是学生学习和查阅资料的主要场所",
                features=["藏书丰富", "环境安静", "设施完善"]
            )
        )
    elif "食堂" in query:
        return (
            "南开大学津南校区学生食堂提供多种菜系，价格实惠，环境整洁。位于校区中心区域，靠近学生宿舍区和教学区。",
            LocationInfo(
                name="南开大学津南校区学生食堂",
                description="位于校区中心区域，靠近学生宿舍区和教学区",
                features=["提供多种菜系", "价格实惠", "环境整洁"]
            )
        )
    elif "体育馆" in query:
        return (
            "南开大学津南校区体育馆设施齐全，包括篮球场、游泳池、健身房等。位于校区西北部，靠近西门。",
            LocationInfo(
                name="南开大学津南校区体育馆",
                description="位于校区西北部，靠近西门",
                features=["设施齐全", "专业场地", "多功能区域"]
            )
        )
    else:
        return (
            "抱歉，我无法识别您询问的地点。请尝试询问南开大学津南校区内的具体地点，如图书馆、食堂等。",
            LocationInfo(
                name="无法处理的请求",
                description="您的问题与南开大学津南校区的地点无关，请询问校园内的具体地点。",
                features=[]
            )
        )

def load_areas_data():
    """
    加载区域数据，优先使用硬编码数据
    """
    try:
        # 尝试从文件加载数据
        with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('areas', [])
    except Exception as e:
        print(f"读取区域数据失败，使用默认数据: {str(e)}")
        return MOCK_AREAS

def load_location_details():
    """
    加载位置详情数据，优先从文件加载，如果文件不存在则使用内置数据
    """
    try:
        # 尝试从文件加载详情数据
        with open('../Front-end/src/assets/LocationDetails.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"无法从文件加载位置详情，使用默认数据: {str(e)}")
        # 返回默认的位置详情数据
        return location_detail_db


def call_nkugenious_api(prompt, system_prompt=""):
    """
    模拟调用 AI 接口，使用本地硬编码数据返回响应

    Args:
        prompt (str): 用户输入的内容
        system_prompt (str, optional): 系统提示词（在硬编码模式下忽略）

    Returns:
        tuple: (原始文本输出, 解析后的 Pydantic 对象)
    """
    print(f"处理查询: {prompt}")
    return mock_ai_response(prompt)
@app.route('/api/submit', methods=['POST'])
def handle_submit():
    # 获取用户输入
    data = request.get_json()
    user_input = data.get('content', '')

    # 输入验证
    if not user_input:
        return jsonify({
            "status": "error",
            "output": "未提供输入内容",
            "result_array": [],
            "structured_output": None
        })

    # 调用模拟 AI 响应
    ai_raw_output, ai_structured_output = call_nkugenious_api(user_input)

    # 匹配地点
    result_array = []

    # 只有当结构化输出有效且不是错误状态时才进行匹配
    if (ai_structured_output and
        ai_structured_output.name not in ["无法处理的请求", "解析失败", "API调用失败", "处理异常"]):

        areas_data = load_areas_data()
        location_name = ai_structured_output.name.lower()

        print(f"正在匹配地点: {location_name}")
        print(f"可用区域数量: {len(areas_data)}")

        # 遍历所有区域进行匹配
        for area in areas_data:
            area_name = area.get('name', '').lower()
            area_fullname = area.get('fullName', '').lower()

            # 匹配条件 - 包含关系即可
            if (area_name in location_name or
                location_name in area_name or
                area_fullname in location_name or
                location_name in area_fullname):

                # 添加匹配结果
                if 'internal_id' in area:
                    result_array.append(area['internal_id'])
                    print(f"匹配到区域: {area.get('name')} (ID: {area['internal_id']})")
                else:
                    result_array.append(area.get('name', '未命名区域'))
                    print(f"匹配到区域: {area.get('name')} (无ID)")

    # 如果没有匹配到地点，修改输出信息
    if not result_array and ai_structured_output and ai_structured_output.name not in ["无法处理的请求", "API调用失败", "处理异常"]:
        ai_structured_output = LocationInfo(
            name="未找到匹配地点",
            description=f"无法在校园地图中找到与{ai_structured_output.name}匹配的地点",
            features=["请尝试使用更准确的地点名称", "可以询问常见地点如图书馆、食堂等"]
        )

    # 返回响应
    response_data = {
        "status": "success",
        "output": ai_raw_output,
        "result_array": result_array,
        "structured_output": ai_structured_output.dict() if ai_structured_output else None
    }

    return jsonify(response_data)


# # 读取区域数据
# def load_areas_data():
#     try:
#         # 尝试读取前端的Area.json文件
#         with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
#             return json.load(f).get('areas', [])
#     except Exception as e:
#         print(f"读取区域数据失败: {str(e)}")
#         return []
#
# @app.route('/api/submit', methods=['POST'])
# def handle_submit():
#     # 获取用户输入
#     data = request.get_json()
#     user_input = data.get('content', '')
#
#     # 输入验证
#     if not user_input:
#         return jsonify({
#             "status": "error",
#             "output": "未提供输入内容",
#             "result_array": [],
#             "structured_output": None
#         })
#
#     # 调用AI模型处理用户输入
#     ai_raw_output, ai_structured_output = call_nkugenious_api(user_input)
#
#     # 匹配地点
#     result_array = []
#
#     # 只有当结构化输出有效且不是错误状态时才进行匹配
#     if (ai_structured_output and
#         ai_structured_output.name not in ["无法处理的请求", "解析失败", "API调用失败", "处理异常"]):
#
#         areas_data = load_areas_data()
#         location_name = ai_structured_output.name.lower()
#
#         print(f"正在匹配地点: {location_name}")
#         print(f"可用区域数量: {len(areas_data)}")
#
#         # 遍历所有区域进行匹配
#         for area in areas_data:
#             area_name = area.get('name', '').lower()
#             area_fullname = area.get('fullName', '').lower()
#
#             # 简化匹配条件，只匹配名称
#             if (area_name in location_name or
#                 area_fullname in location_name or
#                 location_name in area_name or
#                 location_name in area_fullname):
#
#                 # 添加匹配结果
#                 if 'internal_id' in area:
#                     result_array.append(area['internal_id'])
#                     print(f"匹配到区域: {area.get('name')} (ID: {area['internal_id']})")
#                 else:
#                     result_array.append(area.get('name', '未命名区域'))
#                     print(f"匹配到区域: {area.get('name')} (无ID)")
#
#     # 如果没有匹配到地点，修改输出信息
#     if not result_array and ai_structured_output and ai_structured_output.name not in ["无法处理的请求", "API调用失败", "处理异常"]:
#         ai_structured_output = LocationInfo(
#             name="未找到匹配地点",
#             description=f"无法在校园地图中找到与{ai_structured_output.name}匹配的地点",
#             features=["请尝试使用更准确的地点名称", "可以询问常见地点如图书馆、食堂等"]
#         )
#
#     # 返回响应
#     response_data = {
#         "status": "success",
#         "output": ai_raw_output,
#         "result_array": result_array,
#         "structured_output": ai_structured_output.dict() if ai_structured_output else None
#     }
#
#     return jsonify(response_data)
#
# def call_nkugenious_api(prompt, system_prompt=""):
#     """
#     调用 NKUGenious 智能体 API 处理用户输入，简化版本
#
#     Args:
#         prompt (str): 用户输入的内容
#         system_prompt (str, optional): 系统提示词
#
#     Returns:
#         tuple: (原始文本输出, 解析后的 Pydantic 对象或 None)
#     """
#     try:
#         # 设置 API 端点和凭据
#         api_endpoint = "https://coze.nankai.edu.cn/api/proxy/api/v1"
#         app_id = "d0go2puunshmtco3guo0"
#
#         # 如果没有提供系统提示词，使用默认提示词
#         if not system_prompt:
#             system_prompt = "你是南开大学津南校区的专业导航助手。你的任务是提供校园内各地点的准确信息，并严格按照要求的JSON格式返回。"
#
#         # 构建提示词
#         structured_prompt = (
#             f"你是南开大学津南校区的导航助手。请分析用户的问题：\"{prompt}\"，并提取相关的地点信息。\n\n"
#             f"请严格按照以下 JSON 格式返回信息，不要添加任何额外的文本、解释或代码块标记：\n"
#             "{\n"
#             '  "name": "地点的准确名称（如南开大学图书馆、八里台校区等）",\n'
#             '  "description": "详细描述该地点的位置、功能和重要信息",\n'
#             '  "features": ["该地点的特点1", "特点2", "特点3"]\n'
#             "}\n\n"
#             f"如果问题与南开大学津南校区的地点无关，请返回：\n"
#             "{\n"
#             '  "name": "无法处理的请求",\n'
#             '  "description": "您的问题与南开大学津南校区的地点无关，请询问校园内的具体地点。",\n'
#             '  "features": []\n'
#             "}\n"
#         )
#
#         # 构建请求头和请求体
#         headers = {
#             "Content-Type": "application/json"
#         }
#
#         payload = {
#             "app_id": app_id,
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": structured_prompt}
#             ]
#         }
#
#         # 发送请求
#         print(f"发送请求到NKUGenious API，提示词：{prompt}")
#         response = requests.post(api_endpoint, headers=headers, json=payload)
#
#         # 简化的响应处理
#         if response.status_code == 200:
#             response_json = response.json()
#             # 根据实际 API 响应格式调整
#             raw_output = response_json.get("response", "")
#
#             # 尝试解析 JSON
#             try:
#                 # 提取 JSON 部分
#                 json_start = raw_output.find('{')
#                 json_end = raw_output.rfind('}')
#
#                 if json_start != -1 and json_end != -1:
#                     json_str = raw_output[json_start:json_end+1]
#                     parsed_data = LocationInfo.parse_raw(json_str)
#                 else:
#                     # 创建默认响应
#                     parsed_data = LocationInfo(
#                         name="解析失败",
#                         description="无法从响应中提取结构化数据",
#                         features=["请尝试重新提问"]
#                     )
#             except Exception:
#                 # 简化的错误处理
#                 parsed_data = LocationInfo(
#                     name="解析失败",
#                     description="无法解析响应数据",
#                     features=["请尝试重新提问"]
#                 )
#         else:
#             # API 调用失败
#             raw_output = "API 调用失败"
#             parsed_data = LocationInfo(
#                 name="API调用失败",
#                 description=f"状态码: {response.status_code}",
#                 features=["请稍后再试"]
#             )
#
#     except Exception as e:
#         # 捕获所有异常，简化处理
#         print(f"API 调用异常: {str(e)}")
#         raw_output = "处理请求时发生错误"
#         parsed_data = LocationInfo(
#             name="处理异常",
#             description="请求处理失败",
#             features=["请稍后再试"]
#         )
#
#     return raw_output, parsed_data
#
# # 添加一个路由处理导航请求
# @app.route('/api/route', methods=['GET', 'POST'])
# def handle_route():
#     if request.method == 'POST':
#         data = request.get_json()
#         start_point = data.get('start', {})
#         end_point = data.get('end', {})
#
#         # 这里可以实现路径规划逻辑
#         # 简单示例：返回起点和终点信息
#         return jsonify({
#             "status": "success",
#             "route": {
#                 "start": start_point,
#                 "end": end_point,
#                 "distance": "计算的距离",
#                 "duration": "预计时间",
#                 "steps": []  # 路径步骤
#             }
#         })
#     else:
#         # GET 请求返回示例路径数据
#         return jsonify({
#             "status": "success",
#             "routes": [
#                 {
#                     "name": "图书馆到教学楼",
#                     "distance": "500米",
#                     "duration": "约5分钟"
#                 },
#                 {
#                     "name": "宿舍到食堂",
#                     "distance": "300米",
#                     "duration": "约3分钟"
#                 }
#             ]
#         })
#
# #——-------------------新增————————————————
# # 在Pydantic模型定义部分添加（放在LocationInfo类后面）
# class LocationDetailInfo(BaseModel):
#     name: str = Field(..., description="地点完整名称")
#     description: str = Field(..., description="详细描述")
#     location: str = Field(..., description="具体位置")
#     features: List[str] = Field(default_factory=list, description="特点列表")
#     opening_hours: Optional[str] = Field(None, description="开放时间")
#     services: Optional[List[str]] = Field(default_factory=list, description="提供服务")
#     tips: Optional[List[str]] = Field(default_factory=list, description="注意事项")
#     nearby: Optional[List[str]] = Field(default_factory=list, description="附近地点")
#
#
# # 在全局变量部分添加（可以放在load_dotenv()后面）
# location_detail_db = {
#     "食堂": {
#         "name": "南开大学津南校区学生食堂",
#         "location": "位于校区中心区域，靠近学生宿舍区和教学区",
#         "features": ["提供多种菜系", "价格实惠", "环境整洁"],
#         "opening_hours": "早餐: 6:30-9:00, 午餐: 11:00-13:30, 晚餐: 17:00-19:30",
#         "services": ["堂食", "打包", "校园卡支付"],
#         "tips": ["高峰时段可能拥挤", "建议错峰就餐"],
#         "nearby": ["宿舍楼", "教学楼", "便利店"]
#     },
#     "图书馆": {
#         "name": "南开大学津南校区图书馆",
#         "location": "校区中心位置，靠近行政楼和主教学楼",
#         "features": ["藏书丰富", "现代化设施", "安静学习环境"],
#         "opening_hours": "周一至周日 8:00-23:00",
#         "services": ["图书借阅", "自习室", "电子资源", "研讨室"],
#         "tips": ["需要校园卡进入", "保持安静"],
#         "nearby": ["世纪华联超市", "大通学生活动中心", "教学楼"]
#     },
#     "体育馆": {
#         "name": "津南校区体育馆",
#         "location": "校区西北部，靠近西门",
#         "features": ["设施齐全", "专业场地", "多功能区域"],
#         "opening_hours": "8:00~22:00",
#         "services": ["篮球场", "游泳池", "健身房", "羽毛球馆", "乒乓球场", "排球馆", "体育舞蹈教室"],
#         "tips": ["部分设施需要预约", "需携带运动装备", "进入场馆需刷脸"],
#         "nearby": ["主体育场", "文科操场", "学生活动中心"]
#     }
# }
#
#
# # 新增info路由（放在submit路由后面）
# @app.route('/info', methods=['POST'])
# def handle_info():
#     # 统一响应结构
#     response_data = {
#         "status": "error",
#         "output": "",
#         "detail_info": None,
#         "related_locations": [],
#         "message": ""
#     }
#
#     try:
#         data = request.get_json()
#         user_input = data.get('content', '')
#
#         if not user_input:
#             response_data.update({
#                 "output": "未提供查询内容",
#                 "message": "请输入要查询的地点详细信息"
#             })
#             return jsonify(response_data)
#
#         # 调用AI解析（使用专用提示词）
#         ai_raw_output, ai_structured_output = call_nkugenious_api(
#             user_input,
#             system_prompt="请精确提取要查询详情的地点名称，只需返回{'name':'标准名称'}格式"
#         )
#         response_data["output"] = ai_raw_output
#
#         # 错误处理
#         if not ai_structured_output or ai_structured_output.name in ["无法处理的请求", "解析失败", "API调用失败", "处理异常"]:
#             response_data.update({
#                 "message": "无法识别要查询的地点",
#                 "detail_info": {
#                     "name": "未知地点",
#                     "description": "无法识别您查询的地点",
#                     "location": "未知",
#                     "features": ["请尝试使用更标准的地点名称如'图书馆'或'食堂'"]
#                 }
#             })
#             return jsonify(response_data)
#
#         # 获取详细信息 - 严格匹配
#         location_name = ai_structured_output.name.lower()
#         matched_key = None
#
#         # 从前端获取区域数据
#         areas_data = load_areas_data()
#
#         # 严格匹配区域中的地点
#         for area in areas_data:
#             area_name = area.get('name', '').lower()
#             if area_name in location_name:
#                 matched_key = area_name
#                 break
#
#         # 获取详情数据库
#         location_detail_db = load_location_details()
#         detail_info = location_detail_db.get(matched_key) if matched_key else None
#
#         # 如果在详情数据库中找不到该地点，直接返回未找到
#         if not detail_info:
#             response_data.update({
#                 "message": f"未找到{ai_structured_output.name}的详细信息",
#                 "detail_info": {
#                     "name": ai_structured_output.name,
#                     "description": "暂无该地点的详细信息",
#                     "location": "位置信息待补充",
#                     "features": ["信息更新中"]
#                 }
#             })
#             return jsonify(response_data)
#
#         # 关联地点匹配 - 严格匹配
#         related_locations = []
#
#         for area in areas_data:
#             if 'internal_id' in area and area.get('name', '').lower() == matched_key:
#                 related_locations.append(area['internal_id'])
#                 print(f"精确匹配到区域: {area.get('name')}")
#
#         # 数据验证
#         try:
#             validated_info = LocationDetailInfo(**detail_info)
#             response_data.update({
#                 "status": "success",
#                 "detail_info": validated_info.dict(),
#                 "related_locations": related_locations,
#                 "message": "详细信息获取成功"
#             })
#         except ValidationError as e:
#             # 处理验证错误
#             print(f"数据验证错误: {str(e)}")
#             response_data.update({
#                 "message": "数据验证失败",
#                 "error": str(e)
#             })
#
#     except ValidationError as e:
#         response_data.update({
#             "message": "数据验证失败",
#             "error": str(e)
#         })
#     except Exception as e:
#         response_data.update({
#             "message": f"服务器错误: {str(e)}",
#             "error": str(e)
#         })
#
#     return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)