<template>
    <div>
    </div>
</template>

<script setup>
import {onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {EventBus} from "@/scripts/bus.js";

const props = defineProps({
    map: {
        type: Object,
        required: true
    }
});

const geolocation = ref(null);
const marker = ref(null);

const geolocation_initialize = () => {
    if (typeof AMap !== 'undefined') {
        props.map.plugin(["AMap.Geolocation"], function () {
            geolocation.value = new AMap.Geolocation({
                enableHighAccuracy: true,
                timeout: 10000,
                buttonPosition: 'RB',
                buttonOffset: new AMap.Pixel(10, 20),
                zoomToAccuracy: true
            });

            props.map.add(geolocation);

            geolocation.value.on('complete', onLocationComplete);
            geolocation.value.on('error', onLocationError);
            geolocation.value.getCurrentPosition();
        });
    }
};


// 定位成功后的回调函数
const onLocationComplete = (data) => {
    const {position} = data;

    if (marker.value) {
        props.map.remove(marker.value);
    }

    marker.value = new AMap.Marker({
        position: position,
        map: props.map
    });

    props.map.setCenter(position);

    let handler = {
        geolocation: position
    }

    EventBus.emit('update_geolocation', handler);

    watch_position();
};

const onLocationError = (error) => {
    console.error('Location error:', error);
};

// 监听位置变化
const watch_position = () => {
    if (geolocation.value) {
        geolocation.value.watchPosition((status, result) => {
            if (status === 'complete') {
                const {position} = result;

                if (marker.value) {
                   marker.value.setPosition(position);
                }

                let handler = {
                    geolocation: position
                }

                EventBus.emit('update_geolocation', handler);

                props.map.setCenter(position);
            } else {
                console.error('Watch position error:', result);
            }
        });
    }
};

onMounted(() => {
    if (props.map) {
        geolocation_initialize();
    }
});

// 组件销毁前停止监听位置变化
onBeforeUnmount(() => {
    if (geolocation.value) {
        geolocation.value.clearWatch();
    }
});

watch(() => props.map, (newMap) => {
    if (newMap) {
        geolocation_initialize();
    }
});
</script>

<style scoped>
/* 这里可以添加一些样式 */
</style>