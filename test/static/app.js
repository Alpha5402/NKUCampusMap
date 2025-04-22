document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    const userInput = document.getElementById('userInput');
    const responseOutput = document.getElementById('responseOutput');
    const relatedAreas = document.getElementById('relatedAreas');
    const loading = document.getElementById('loading');
    // 获取卡片元素
    const cardContainer = document.getElementById('cardContainer');
    const cardName = document.getElementById('cardName');
    const cardDescription = document.getElementById('cardDescription');
    const cardFeatures = document.getElementById('cardFeatures');

    // 后端API地址
    const apiUrl = 'http://localhost:5000/submit';

    submitBtn.addEventListener('click', function() {
        const content = userInput.value.trim();
        if (!content) {
            alert('请输入内容');
            return;
        }

        loading.style.display = 'block';
        responseOutput.textContent = '正在获取响应...';
        relatedAreas.textContent = '正在分析相关区域...';
        cardContainer.style.display = 'none'; // 隐藏旧卡片

        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`网络响应不正常 (${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            loading.style.display = 'none';

            // 显示原始API响应
            responseOutput.textContent = data.output || '无原始响应内容';

            // 显示相关区域
            if (data.result_array && data.result_array.length > 0) {
                relatedAreas.textContent = '找到相关区域: ' + data.result_array.join(', ');
            } else {
                relatedAreas.textContent = '未找到相关区域';
            }

            console.log('完整响应数据:', data);

            // 渲染卡片 - 改进逻辑，确保始终显示卡片
            if (data.structured_output) {
                // 设置卡片标题
                cardName.textContent = data.structured_output.name;
                
                // 设置卡片描述
                cardDescription.textContent = data.structured_output.description;
                
                // 清空旧的特点列表
                cardFeatures.innerHTML = '';
                
                // 添加特点列表
                if (data.structured_output.features && data.structured_output.features.length > 0) {
                    data.structured_output.features.forEach(feature => {
                        const li = document.createElement('li');
                        li.textContent = feature;
                        cardFeatures.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.textContent = '暂无特点信息';
                    cardFeatures.appendChild(li);
                }
                
                // 显示卡片
                cardContainer.style.display = 'block';
                console.log('卡片已渲染:', data.structured_output);
            } else {
                // 即使没有结构化输出，也创建一个基本卡片
                cardName.textContent = "处理失败";
                cardDescription.textContent = "无法从AI响应中提取结构化数据";
                cardFeatures.innerHTML = '';
                const li = document.createElement('li');
                li.textContent = '请尝试重新提问';
                cardFeatures.appendChild(li);
                cardContainer.style.display = 'block';
                console.log('创建了默认卡片，因为没有结构化输出');
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            responseOutput.textContent = '请求出错: ' + error.message;
            relatedAreas.textContent = '错误';
            
            // 显示错误卡片
            cardName.textContent = "请求错误";
            cardDescription.textContent = error.message;
            cardFeatures.innerHTML = '';
            const li = document.createElement('li');
            li.textContent = '请检查网络连接并重试';
            cardFeatures.appendChild(li);
            cardContainer.style.display = 'block';
            
            console.error('请求出错:', error);
        });
    });
});