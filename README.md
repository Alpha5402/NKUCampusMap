## 项目简介
本项目是2025年火山杯参赛项目，项目名称为`云览津南-从现实到数字化`，由软件学院和密码学院同学进行开发。
项目的主要功能是将校园内的建筑物、道路、绿地等信息进行数字化处理，并在地图上进行展示。用户可以通过地图进行导航，获取建筑物的信息等。
项目基于高德地图和NKGeniOSSDK进行开发，前端使用Vue.js进行开发，后端使用Flask进行开发。
## 构建工具
本项目部署在linux服务器上，部署命令如下。
#### 开发环境构建
###### 前端环境配置
```
npm install
```
###### 前端构建
```
npm run dev
```
###### 后端构建
```
python run.py
```

#### 生产环境构建
###### 前端构建
```
cd NKUCampusMap/Front-end
npm run build
sudo cp -r dist/* /var/www/nkucampusmap
sudo systemctl restart nginx
```

如果已经在 Front-end 目录下

```
npm run build
sudo cp -r dist/* /var/www/nkucampusmap
sudo systemctl restart nginx
```
###### 后端构建
```
lsof -i :5000 | awk 'NR==2 {print $2}' | xargs kill -9
cd NKUCampusMap/Back-end
gunicorn --config gunicorn_config.py app:app
```

## 双端通信示例

#### 客户端
###### GET
```js
fetch('https://www.nkucampusmap.xin/api/route')
	.then(response => {
		if (!response.ok) {
			return Promise.reject('Failed to fetch: ' + response.statusText);
		}
			return response.json();
		})
	.then(data => {
        console.log("Received data: ", data);
	})
	.catch(error => {
		return Promise.reject(error);
	})
})
```
###### POST
```js
fetch('https://www.nkucampusmap.xin/api/route', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        content: content.value
    })
})
    .then(response => response.json())
    .then(data => {
        console.log("Received data: ", data);
    })
	.catch(error => {
		return Promise.reject(error);
	})
```
#### 服务端

```python
@app.route('/api/route')
def custom_function():
	result_1 = ...
	result_2 = ...
    ...
    return jsonify({
	    'response_result_1': result_1, 
	    'response_result_2': result_2
	})

@app.route('/api/submit', methods=['POST'])
def receive_message():
    data = request.get_json()
    
    print("Received message:", data)

    response = {
        "status": "success",
        "message": "Message received successfully",
        "received_data": data
    }

    return jsonify(response)
```