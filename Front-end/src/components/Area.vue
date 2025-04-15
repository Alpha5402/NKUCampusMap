<template>
    <div ref="mapContainer">
    </div>
</template>

<script setup>
import { onMounted, defineProps, ref, watch } from 'vue';
import { EventBus } from '../scripts/bus.js';

const props = defineProps({
    map: {
        type: Object,
        required: true
    },
    area_target: {
        type: Object,
        required: true
    }
});

const mapContainer = ref(null);
// 控制 SubMenu 显示

// 控制哪个菜单被打开
let currentPolygon = null;  // 当前打开的多边形
let map = null;  // 地图对象

// 监听 map 是否变化，如果变化则重新设置地图
watch(() => props.map, (newMap) => {
    if (newMap) {
        create_interactive_area(props.area_target.coordinates); // 在地图加载完后初始化多边形
    }
});

function create_interactive_area(coordinates) {
    const polygon = new AMap.Polygon({
        path: coordinates, // 设置多边形路径
        strokeColor: "rgba(0,63,255,0.8)", // 线颜色
        strokeWeight: 2, // 线宽
        strokeOpacity: 0.2, // 线透明度
        fillOpacity: 0.4, // 填充透明度
        fillColor: '#1791fc', // 填充颜色
        zIndex: 50 // 层级
    });

    let centroid = get_centroid(props.area_target.coordinates);

    var text = new AMap.Text({
        text: props.area_target.name,
        position: new AMap.LngLat(centroid[0], centroid[1]),
        anchor: "center",
        offset: new AMap.Pixel(0, 0), // 文本偏移量
        style: {
            'background-color': 'rgba(255, 255, 255, 0)',
            'border': 'none',
            'padding': '5px',
            'font-size': '14px',
            'color': '#333'
        }
    });

    props.map.add(polygon);
    props.map.add(text);

    polygon.on('click', (event) => {
        let handler = {
            area_info_display_status: true,
            target: props.area_target,
        }

        EventBus.emit('toggle_menu', handler);
    });

    // console.log("Interactive area has been drawn successfully.");
}

onMounted(() => {
    if (props.map) {
        create_interactive_area(props.area_target.coordinates);
        // console.log("[onMounted] Polygon has been created")
    }
});
</script>

<script>
function get_centroid(path) {
    var x = 0.0, y = 0.0;
    var len = path.length;

    for (var i = 0; i < len; i++) {
        var p1 = path[i];
        var p2 = path[(i + 1) % len];
        x += (p1[0] + p2[0]) * (p1[0] * p2[1] - p2[0] * p1[1]);
        y += (p1[1] + p2[1]) * (p1[0] * p2[1] - p2[0] * p1[1]);
    }

    var area = 0;
    for (var i = 0; i < len; i++) {
        var p1 = path[i];
        var p2 = path[(i + 1) % len];
        area += p1[0] * p2[1] - p2[0] * p1[1];
    }

    area *= 0.5;
    x = x / (6 * area);
    y = y / (6 * area);

    return [x, y];
}

window.get_centroid = get_centroid;
</script>

<style scoped>
/* 可以添加自定义样式 */

</style>
