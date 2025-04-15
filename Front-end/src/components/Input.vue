<template>
    <div class="textarea-container">
        <!-- Textarea input element -->
        <textarea
            id = "input_area"
            v-model="textContent"
            :rows="rows"
            class="textarea"
            text
            @focus="handleFocus"
            @input="handleInput"
            @blur="handleBlur"
        ></textarea>
        <!-- Submit Button -->
        <button @click="content_submit" class="submit-btn">
            <font-awesome-icon :icon="['fas', 'magnifying-glass']" />
        </button>
    </div>
</template>

<script setup>
import { EventBus } from '@/scripts/bus';
import {defineProps, ref, watch} from 'vue';

const props = defineProps({
    content: {
        type: String,
        required: true
    },
});

// 监听 props.content 的变化，并更新 textContent
watch(() => props.content, (newContent) => {
    textContent.value = getTimeOfDay() + "好，" + newContent;
});

const textContent = ref('Hello, world！'); // 绑定文本框内容
const rows = ref(1); // 默认显示 1 行


const handleBlur = () => {
    rows.value = 1;
};


const getTimeOfDay = () => {
    const hour = new Date().getHours();

    if (hour >= 5 && hour < 11) {
        return "早上";
    } else if (hour >= 11 && hour < 14) {
        return "中午";
    } else if (hour >= 14 && hour < 18) {
        return "下午";
    } else {
        return "晚上";
    }
}


// 提交内容到后端
const content_submit = () => {
    console.log("Submitting content:", textContent.value);
    // 示例：发送 POST 请求到后端
    fetch('https://www.nkucampusmap.xin/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content: textContent.value
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const handler = {
                response_display_status: true
            }
            EventBus.emit('display_response', handler);
        })
        .catch(error => console.error('Error:', error));
};
</script>

<style scoped>
.textarea-container {
    position: absolute;
    display: flex;
    justify-content: space-between;
    align-items: center; /* 保持垂直居中 */
    gap: 10px; /* 设置 textarea 和 button 之间的间距 */

    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 320px; /* 宽度略微调整 */
    height: auto;
    z-index: 100;
}

.textarea {
    position: relative;
    flex: 1;
    padding: 0.5em;
    height: 100%; /* 固定高度，防止变形 */
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
    resize: none;
    font-family: '微软雅黑';
    color: #333;
    z-index: 100;

    align-content: center;
}

.submit-btn {
    position: relative;
    width: 40px; /* 固定按钮宽度 */
    height: 40px; /* 保持和 textarea 同高 */
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-family: Consolas;
    transition: background-color 0.3s ease;
    z-index: 100;
}

.textarea::placeholder {
    color: #888;
}

.submit-btn:hover {
    background-color: #0056b3;
    transition: background-color 0.3s ease;
}
</style>
