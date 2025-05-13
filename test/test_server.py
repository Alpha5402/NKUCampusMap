import sys
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

# --- Pydantic 模型定义 ---
class LocationInfo(BaseModel):
    name: str = Field(..., description="地点的标准名称")
    description: str = Field(..., description="关于地点的详细描述")
    features: List[str] = Field(default_factory=list, description="地点的显著特点列表")

class LocationDetailInfo(BaseModel):
    name: str = Field(..., description="地点完整名称")
    description: str = Field(..., description="详细描述")
    location: str = Field(..., description="具体位置")
    features: List[str] = Field(default_factory=list, description="特点列表")
    opening_hours: Optional[str] = Field(None, description="开放时间")
    services: Optional[List[str]] = Field(default_factory=list, description="提供服务")
    tips: Optional[List[str]] = Field(default_factory=list, description="注意事项")
    nearby: Optional[List[str]] = Field(default_factory=list, description="附近地点")

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟区域数据
MOCK_AREAS = [
    {"name": "图书馆", "fullName": "南开大学津南校区图书馆", "internal_id": "lib001"},
    {"name": "食堂", "fullName": "南开大学津南校区学生食堂", "internal_id": "canteen001"},
    {"name": "体育馆", "fullName": "南开大学津南校区体育馆", "internal_id": "gym001"},
    {"name": "宿舍", "fullName": "南开大学津南校区学生宿舍", "internal_id": "dorm001"}
]

# 模拟详情数据库
MOCK_LOCATION_DETAILS = {
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

# 模拟 AI 响应
def mock_ai_response(query):
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

# 模拟后端的 /api/submit 接口
@app.route('/api/submit', methods=['POST'])
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

    # 模拟调用 AI 模型
    ai_raw_output, ai_structured_output = mock_ai_response(user_input)
    
    # 匹配地点 - 简化逻辑，只匹配 MOCK_AREAS 中的地点
    result_array = []
    
    # 只有当结构化输出有效且不是错误状态时才进行匹配
    if (ai_structured_output and 
        ai_structured_output.name not in ["无法处理的请求", "解析失败", "API调用失败", "处理异常"]):
        
        location_name = ai_structured_output.name.lower()
        print(f"正在匹配地点: {location_name}")
        
        # 严格匹配：只匹配 MOCK_AREAS 中的地点
        for area in MOCK_AREAS:
            area_name = area.get('name', '').lower()
            area_fullname = area.get('fullName', '').lower()
            
            # 精确匹配条件
            if (area_name == location_name or 
                area_fullname == location_name or 
                (area_name in location_name and len(area_name) > 2)):  # 允许部分匹配，但关键词必须足够长
                
                # 只添加有 internal_id 的匹配结果
                if 'internal_id' in area:
                    result_array.append(area['internal_id'])
                    print(f"匹配到区域: {area.get('name')} (ID: {area['internal_id']})")
    
    # 如果没有匹配到地点，修改输出信息
    if not result_array and ai_structured_output and ai_structured_output.name not in ["无法处理的请求", "API调用失败", "处理异常"]:
        ai_structured_output = LocationInfo(
            name="未找到匹配地点",
            description=f"无法在校园地图中找到与{ai_structured_output.name}匹配的地点",
            features=["请尝试使用更准确的地点名称", "可以询问常见地点如'图书馆'、'食堂'等"]
        )
    
    # 返回响应
    # 返回响应
    response_data = {
        "status": "success",
        "output": ai_raw_output,
        "result_array": result_array,
        "structured_output": ai_structured_output.model_dump() if ai_structured_output else None
    }

    return jsonify(response_data)

# 模拟后端的 /info 接口
@app.route('/info', methods=['POST'])
def handle_info():
    # 统一响应结构
    response_data = {
        "status": "error",
        "output": "",
        "detail_info": None,
        "related_locations": [],
        "message": ""
    }

    try:
        data = request.get_json()
        user_input = data.get('content', '')

        if not user_input:
            response_data.update({
                "output": "未提供查询内容",
                "message": "请输入要查询的地点详细信息"
            })
            return jsonify(response_data)

        # 模拟调用AI解析
        ai_raw_output, ai_structured_output = mock_ai_response(user_input)
        response_data["output"] = ai_raw_output

        # 错误处理
        if not ai_structured_output or ai_structured_output.name in ["无法处理的请求", "解析失败", "API调用失败", "处理异常"]:
            response_data.update({
                "message": "无法识别要查询的地点",
                "detail_info": {
                    "name": "未知地点",
                    "description": "无法识别您查询的地点",
                    "location": "未知",
                    "features": ["请尝试使用更标准的地点名称如'图书馆'或'食堂'"]
                }
            })
            return jsonify(response_data)

        # 获取详细信息 - 严格匹配
        location_name = ai_structured_output.name.lower()
        matched_key = None
        
        # 严格匹配 MOCK_AREAS 中的地点
        for area in MOCK_AREAS:
            area_name = area.get('name', '').lower()
            if area_name in location_name:
                matched_key = area_name
                break
        
        # 如果没有匹配到，尝试使用关键词匹配
        if not matched_key:
            key_words = ["图书馆", "食堂", "体育馆"]
            for key in key_words:
                if key in location_name:
                    matched_key = key
                    break
        
        detail_info = MOCK_LOCATION_DETAILS.get(matched_key) if matched_key else None
        
        # 如果在详情数据库中找不到该地点，直接返回未找到
        if not detail_info:
            response_data.update({
                "message": f"未找到{ai_structured_output.name}的详细信息",
                "detail_info": {
                    "name": ai_structured_output.name,
                    "description": "暂无该地点的详细信息",
                    "location": "位置信息待补充",
                    "features": ["信息更新中"]
                }
            })
            return jsonify(response_data)

        # 关联地点匹配 - 严格匹配
        related_locations = []
        
        for area in MOCK_AREAS:
            if 'internal_id' in area and area.get('name', '').lower() == matched_key:
                related_locations.append(area['internal_id'])
                print(f"精确匹配到区域: {area.get('name')}")

        # 数据验证
        try:
            validated_info = LocationDetailInfo(**detail_info)
            response_data.update({
                "status": "success",
                "detail_info": validated_info.model_dump(),
                "related_locations": related_locations,
                "message": "详细信息获取成功"
            })
        except ValidationError as e:
            # 处理验证错误
            print(f"数据验证错误: {str(e)}")
            response_data.update({
                "message": "数据验证失败",
                "error": str(e)
            })

    except ValidationError as e:
        response_data.update({
            "message": "数据验证失败",
            "error": str(e)
        })
    except Exception as e:
        response_data.update({
            "message": f"服务器错误: {str(e)}",
            "error": str(e)
        })

    return jsonify(response_data)

# 转发到实际后端（如果需要）
@app.route('/api/real_submit', methods=['POST'])
def real_submit():
    try:
        # 获取后端 URL（可以通过环境变量或配置文件设置）
        backend_url = "http://localhost:5000/api/submit"
        
        # 设置请求头，关闭持久连接
        headers = {
            "Content-Type": "application/json",
            "Connection": "close",  # 关闭持久连接
            "Host": "localhost:5000"  # 确保 Host 头部正确
        }
        
        # 转发请求，添加超时设置
        response = requests.post(
            backend_url,
            json=request.get_json(),
            headers=headers,
            timeout=5  # 设置5秒超时
        )
        
        # 返回后端响应
        return jsonify(response.json())
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "无法连接到后端服务器，请确保后端服务器已启动",
            "error": "连接被拒绝"
        })
    except requests.exceptions.Timeout as e:
        print(f"请求超时: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "连接后端超时，请检查后端服务器是否响应",
            "error": "请求超时"
        })
    except Exception as e:
        print(f"请求错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"连接后端失败: {str(e)}",
            "error": str(e)
        })

# 提供静态文件
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("测试服务器已启动，访问 http://localhost:5001 查看测试界面")
    app.run(debug=True, port=5001)