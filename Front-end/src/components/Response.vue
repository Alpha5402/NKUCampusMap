<template>
    <div class="response-container">
        <div class = "list-container" v-show = "response_invaild">
            <div 
                class = "list-item"
                v-for = "(area, index) in props.areas_list"
                :key = "index"
                @click = "display_area_info(area.fullName)"    
            >
                {{ area.fullName }}
            </div>
        </div>      
    </div>
</template>

<script setup>
import { ref } from 'vue'

const response_invaild = ref(true);

const props = defineProps({
    result: {
        type: Array,
        required: true
    },
    main_description: {
        type: String,
        required: true
    },
    areas_list: {
        type: Array,
        required: true
    }
})

// const computed_content = computed(() => {
//     if (props.result.length > 0) {
//         response_invaild.value = false;
//         return props.result[0].content;
//     } else {
//         response_invaild.value = true;
//         return "無法辨識";
//     }
// })
</script>

<style scoped>
.response-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.list-container {
    width: 100%;
    height: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.list-item {
    font-size: 16px;
    padding: 4px;
    margin: 4px;
}
</style>