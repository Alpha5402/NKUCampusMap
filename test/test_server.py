from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
# 导入 Pydantic 相关库
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

# --- Pydantic 模型定义 ---
class LocationInfo(BaseModel):
    name: str = Field(..., description="地点的标准名称")
    description: str = Field(..., description="关于地点的详细描述")
    features: List[str] = Field(default_factory=list, description="地点的显著特点列表")

# --- Flask 应用设置 ---
# 创建Flask应用，并指定静态文件夹为当前目录
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # 启用CORS，允许前端页面访问

# --- 辅助函数 ---
# 读取区域数据
def load_areas_data():
    try:
        # 尝试读取前端的Area.json文件
        with open('../Front-end/src/assets/Area.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('areas', [])
    except Exception as e:
        print(f"读取区域数据失败: {str(e)}")
        return []

# 调用DeepSeek API 并尝试解析为 Pydantic 模型
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
    parsed_data: Optional[LocationInfo] = None
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

# --- API 路由 ---
# 处理提交请求
@app.route('/submit', methods=['POST'])
def handle_submit():
    data = request.get_json()
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

# 提供静态文件
@app.route('/')
def index():
    # 确保从当前目录提供 index.html
    return send_from_directory('.', 'index.html')
#——————————————-新增————————————————————————————
# 首先在Pydantic模型部分新增详细信息模型（放在LocationInfo下方）
class LocationDetailInfo(BaseModel):
    name: str = Field(..., description="地点完整名称")
    description: str = Field(..., description="详细描述")
    location: str = Field(..., description="具体位置")
    features: List[str] = Field(default_factory=list, description="特点列表")
    opening_hours: Optional[str] = Field(None, description="开放时间")
    services: Optional[List[str]] = Field(default_factory=list, description="提供服务")
    tips: Optional[List[str]] = Field(default_factory=list, description="注意事项")


# 新增详细信息数据库（实际项目建议用数据库）
location_detail_db = {
    "食堂": {
            "name": "南开大学津南校区学生食堂",
            "location": "位于校区中心区域，靠近学生宿舍区和教学区",
            "features": ["提供多种菜系", "价格实惠", "环境整洁"],
            "opening_hours": "早餐: 6:30-9:00, 午餐: 11:00-13:30, 晚餐: 17:00-19:30",
            "services": ["堂食", "打包", "校园卡支付"],
            "tips": ["高峰时段可能拥挤", "建议错峰就餐"],
            "nearby": ["宿舍楼", "教学楼", "便利店"]
        },
        "图书馆": {
            "name": "南开大学津南校区图书馆",
            "location": "校区中心位置，靠近行政楼和主教学楼",
            "features": ["藏书丰富", "现代化设施", "安静学习环境"],
            "opening_hours": "周一至周日 8:00-23:00",
            "services": ["图书借阅", "自习室", "电子资源", "研讨室"],
            "tips": ["需要校园卡进入", "保持安静"],
            "nearby": ["世纪华联超市", "大通学生活动中心", "教学楼"]
        },
        "体育馆": {
            "name": "津南校区体育馆",
            "location": "校区西北部，靠近西门",
            "features": ["设施齐全", "专业场地", "多功能区域"],
            "opening_hours": "8:00~22:00",
            "services": ["篮球场", "游泳池", "健身房", "羽毛球馆","乒乓球场","排球馆","体育舞蹈教室"],
            "tips": ["部分设施需要预约", "需携带运动装备","进入场馆需刷脸"],
            "nearby": ["主体育场", "文科操场", "学生活动中心"]
    }
}


# 新增info路由（与submit保持相同风格）
@app.route('/info', methods=['POST'])
def handle_info():
    # 统一响应数据结构
    response_data = {
        "status": "error",
        "output": "",
        "detail_info": None,
        "related_locations": [],
        "message": ""
    }

    # 获取输入（与submit完全一致）
    data = request.get_json()
    user_input = data.get('content', '')

    if not user_input:
        response_data.update({
            "output": "未提供查询内容",
            "message": "请输入要查询的地点详细信息"
        })
        return jsonify(response_data)

    # 调用AI解析（使用专用system_prompt）
    ai_raw_output, ai_structured_output = call_deepseek_api(
        user_input,
        system_prompt="请精确提取要查询详情的地点名称，只需返回标准名称不要解释"
    )
    response_data["output"] = ai_raw_output

    # 错误处理（与submit相同模式）
    if not ai_structured_output or ai_structured_output.name in ["无法处理的请求", "解析失败"]:
        response_data.update({
            "message": "无法识别要查询的地点",
            "detail_info": {
                "name": "未知地点",
                "suggestion": "请尝试使用更标准的地点名称"
            }
        })
        return jsonify(response_data)

    # 获取详细信息
    location_name = ai_structured_output.name
    detail_info = location_detail_db.get(location_name, {
        "name": location_name,
        "description": "暂无详细信息",
        "location": "位置信息待补充",
        "features": ["信息更新中"],
        "tips": ["请咨询校园工作人员"]
    })

    # 关联地点匹配（与submit相同的匹配逻辑）
    areas_data = load_areas_data()
    related_locations = []
    for area in areas_data:
        if area.get('name', '').lower() in location_name.lower():
            if 'internal_id' in area:
                related_locations.append(area['internal_id'])

    # 数据验证（与submit相同的验证模式）
    try:
        validated_info = LocationDetailInfo(**detail_info)
        response_data.update({
            "status": "success",
            "detail_info": validated_info.dict(),
            "related_locations": related_locations,
            "message": "详细信息获取成功"
        })
    except ValidationError as e:
        response_data.update({
            "message": "数据验证失败",
            "error": str(e),
            "detail_info": detail_info  # 保持返回原始数据
        })

    return jsonify(response_data)


# --- 主程序入口 ---
if __name__ == '__main__':
    # 确保静态文件目录存在
    if not os.path.exists('static'):
        os.makedirs('static')

    print("测试服务器已启动，请访问 http://localhost:5000")
    app.run(debug=True) # debug=True 会在代码更改时自动重启服务器