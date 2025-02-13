<template>
    <div class="textarea-container">
        <!-- Textarea input element -->
        <textarea
            v-model="textContent"
            :rows="rows"
            class="textarea"
            text
            :style="textareaStyle"
            @focus="handleFocus"
            @input="handleInput"
            @blur="handleBlur"
        ></textarea>
        <!-- Submit Button -->
        <button @click="content_submit" class="submit-btn">Submit</button>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const textContent = ref('今天有什么计划？'); // 绑定文本框内容
const rows = ref(1); // 默认显示 1 行
const textareaStyle = ref({
    position: 'absolute',
    top: '10px',
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 100,
    transition: 'height 0.3s ease'
});

const handleFocus = () => {
    if (rows.value === 1) {
        rows.value = 3;
    }
};

const handleInput = () => {
    if (textContent.value.split('\n').length > 10) {
        rows.value = 10;
    } else if (textContent.value.split('\n').length > 3) {
        rows.value = 3;
    }
};

const handleBlur = () => {
    rows.value = 1;
};

// 提交内容到后端
const content_submit = () => {
    // 在这里将内容发送到后端（使用 axios 或 fetch）
    console.log("Submitting content:", textContent.value);
    // 示例：发送 POST 请求到后端
    fetch('http://localhost:5000/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: textContent.value
        })
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error));
};
</script>

<style scoped>
.textarea-container {
    position: absolute;
    top: 10px; /* 距离顶部 10px */
    left: 50%;
    transform: translateX(-50%);
    width: 300px;
    z-index: 100; /* 确保在 Map 上方显示 */
}

.textarea {
    width: 100%;
    padding: 10px;
    font-size: 16px;
    resize: none;
    border: 1px solid #ccc;
    border-radius: 5px;
    overflow-y: auto;
    font-family: '微软雅黑'; /* 设置字体 */
    font-weight: normal; /* 设置字体粗细 */
    color: #333; /* 设置字体颜色 */
}

.textarea::placeholder {
    color: #888;
}

.submit-btn {
    position: absolute;
    top: 50px; /* 距离顶部 10px */
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    z-index: 1000;
    zIndex: 1000;
}

.submit-btn:hover {
    background-color: #0056b3;
}
</style>
