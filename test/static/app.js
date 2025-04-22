document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    const userInput = document.getElementById('userInput');
    const responseOutput = document.getElementById('responseOutput');
    const relatedAreas = document.getElementById('relatedAreas');
    const loading = document.getElementById('loading');
    
    // 后端API地址
    const apiUrl = 'http://localhost:5000/submit';
    
    submitBtn.addEventListener('click', function() {
        // 获取用户输入
        const content = userInput.value.trim();
        
        if (!content) {
            alert('请输入内容');
            return;
        }
        
        // 显示加载状态
        loading.style.display = 'block';
        responseOutput.textContent = '正在获取响应...';
        relatedAreas.textContent = '正在分析相关区域...';
        
        // 发送请求到后端
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
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(data => {
            // 隐藏加载状态
            loading.style.display = 'none';
            
            // 显示API响应
            responseOutput.textContent = data.output || '无响应内容';
            
            // 显示相关区域
            if (data.result_array && data.result_array.length > 0) {
                relatedAreas.textContent = '找到相关区域: ' + data.result_array.join(', ');
            } else {
                relatedAreas.textContent = '未找到相关区域';
            }
            
            console.log('完整响应数据:', data);
        })
        .catch(error => {
            // 隐藏加载状态
            loading.style.display = 'none';
            
            // 显示错误信息
            responseOutput.textContent = '请求出错: ' + error.message;
            console.error('请求出错:', error);
        });
    });
});