<template>
    <div class="info_menu">
        <ul>
            <div class = "title">{{ props.area_target.name }}</div>
            <li v-for="(name, index) in props.area_target.options" :key="index" @click="handle_menu_lick(index)">
                {{ name }}
            </li>
        </ul>

    </div>
</template>

<script setup>
import { defineProps, ref } from 'vue';
import { EventBus } from './bus.js';

// 接收父组件 Area 传递过来的 props
const props = defineProps({
    area_target: {
        type: Object,
        required: true
    }
});

// 处理点击事件，调用对应的函数
const handle_menu_lick = (index) => {
    const method_name = props.area_target.methods[index];
    if (typeof window[method_name] === 'function') {
        window[method_name]();
    } else {
        console.error(`方法 ${method_name} 未定义`);
    }
};
window.handle_menu_lick = handle_menu_lick;

// 处理导航事件，让用户选择出行方式
const navigation = () => {
    const location = ref(props.location);

    let handler = {
        status: true,
    }
    EventBus.emit('toggle_travel_mode_menu', handler);

    let sub_menu_handler = {
        status: false,
        target: props.area_target,
        position: null
    }
    EventBus.emit('toggle_sub_menu', sub_menu_handler);

}
window.navigation = navigation;

const internal_map = () => {
    // 使用 fetch 向后端发送 POST 请求
    fetch('http://127.0.0.1:5000/receive_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify("message") // 将 JavaScript 对象转为 JSON 字符串
    })
        .then(response => response.json())  // 解析 JSON 格式的响应
        .then(data => {
            console.log("Response from server:", data);
            alert("Response from server: " + JSON.stringify(data));
        })
        .catch(error => {
            console.error("Error:", error);
        });
}
window.internal_map = internal_map;
</script>

<style scoped>
.info_menu {
    position: absolute;
    background-color: #fff;
    border: 1px solid #ccc;
    padding: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 100;
}

.info_menu ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.info_menu li {
    padding: 8px;
    cursor: pointer;
}

.info_menu li:hover {
    background-color: #f0f0f0;
}

.title {
    font-family: 微软雅黑;
    font-size: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 4px;
}
</style>
