<template>
    <div class = "modal-overlay" @click = "handle_overlay_click">
        <div class="info_menu" ref = "modal">
            <ul>
                <div class = "title">{{ props.area_target.name }}</div>
                <li v-for="(name, index) in props.area_target.options" :key="index" @click="handle_menu_click(index)">
                    {{ name }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { defineProps, ref } from 'vue';
import { EventBus } from '../scripts/bus.js';

const modal = ref(null);
const flag = ref(false)

// 接收父组件 Area 传递过来的 props
const props = defineProps({
    area_target: {
        type: Object,
        required: true
    }
});

/**
 * 处理菜单点击事件的函数
 * @param {number} index - 被点击菜单的索引，用于确定要调用的方法
 */
const handle_menu_click = (index) => {
    // 获取对应索引的方法名
    const method_name = props.area_target.methods[index];
    // 检查方法是否在全局作用域中定义且为函数类型
    if (typeof window[method_name] === 'function') {
        // 调用对应的方法
        window[method_name]();
    } else {
        // 输出错误信息，指示方法未定义
        console.error(`方法 ${method_name} 未定义`);
    }
};
window.handle_menu_click = handle_menu_click;

// 处理导航事件，让用户选择出行方式
const navigation = () => {
    const location = ref(props.area_target.location);
    //console.log("Areainfo location " + location.x + " " + location.y);

    let handler = {
        area_info_display_status: false,
        travel_mode_display_status: true
    }
    flag.value = true;
    EventBus.emit('toggle_menu', handler);
}
window.navigation = navigation;

// 向后端请求打开图片
const internal_map = () => {
     let handler = {
        area_info_display_status: false,
        travel_mode_display_status: false,
        image_provider_display_status: true
    }
    flag.value = true;
    EventBus.emit('toggle_menu', handler);
    EventBus.emit('render_image', {});
}
window.internal_map = internal_map;

const handle_overlay_click = (event) => {
    if (!is_click_inside_modal(event)) {
        if (!flag.value) {
            let handler = {
                area_info_display_status: false,
                travel_mode_display_status: false
            }
            EventBus.emit('toggle_menu', handler);
            console.log("Closing all menu...")
        } else {
            flag.value = false;
        }
    }
}

const is_click_inside_modal = (event) => {
    if (!modal.value) return false;

    const modal_rect = modal.value.getBoundingClientRect();

    return (
        event.clientX >= modal_rect.left &&
        event.clientX <= modal_rect.right &&
        event.clientY >= modal_rect.top &&
        event.clientY <= modal_rect.bottom
    );
}

window.internal_map = internal_map;
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.info_menu {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 80%;
    width: 500px;
    text-align: center;
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
    font-weight: bold;
    font-size: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px;
}
</style>
