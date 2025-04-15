<template>
    <div class = "modal-overlay" @click = "handle_overlay_click">
        <div class = "image_provider" ref = "modal">
            <div class = "image_title"> {{ props.image_title }} </div>
            <div class = "image_container">
                <img :src = "current_image_src" :alt="image_description" width = "300px" height = "300px">
                <div v-for="(name, index) in image_src_list" :key="index" @click="handle_image_toggle(index)">
                    {{ name }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { EventBus } from '@/scripts/bus';
import { onMounted, ref } from 'vue'

const current_image_src = ref(null);
const image_src_list = ref([]);
const image_description = ref("");
const modal = ref(null);

const props = defineProps({
    target: {
        required: false,
        type: Object
    },
    image_title: {
        required: false,
        type: String,
        default: "未命名"
    },
    image_index: {
        required: false,
        type: Array
    },
    image_src: {
        
        required: true,
        type: Array
    }
})

const handle_overlay_click = (event) => {
    if (!is_click_inside_modal(event)) {
        let handler = {
            area_info_display_state: false,
            travel_mode_display_status: false
        }
        EventBus.emit('toggle_menu', handler);
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

onMounted (() => {
    EventBus.on('render_image', (data) => {
        if (props.target) {
            image_src_list.value = props.target.floor_name;
            console.log(image_src_list);
            current_image_src.value = props.target.internal_id + "\\"+ image_src_list[0] + ".png";
        } else {
            console.log("no target");
        }
    })
})

const handle_image_toggle = (index) => {
    current_image_src.value = props.target.internal_id + "\\"+ image_src_list[index] + ".png";
    image_description.value = "我是" + props.target.fullName + " " + image_src_list[index] + " 的地图";
}


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

.image_provider {
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

.image_title {
    font-family: 微软雅黑;
    font-weight: bold;
    font-size: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px;
}
</style>