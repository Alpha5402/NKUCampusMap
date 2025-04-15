<template>
    <div class = "modal-overlay" @click = "handle_overlay_click">
        <div class="travel_mode_menu" ref = "modal">
            <div class = "title">出行方式</div>
            <div class = "travelmode" @click="start_navigation('driving')">驾车</div>
            <div class = "travelmode" @click="start_navigation('riding')">骑行</div>
            <div class = "travelmode" @click="start_navigation('walking')">步行</div>
        </div>
    </div>
</template>

<script setup>
import {defineProps, ref} from 'vue';
import { EventBus } from '../scripts/bus.js';

const props = defineProps({
    map: {
        type: Object,
        required: true
    },
    target: {
        type: Object,
        required: true
    },
    begin: {
        type: Object,
        required: true
    }
});


const modal = ref(null);

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


/**
 * something necessnary
 * - destination
 * - transportation (Anyone of the following
 *  - driving
 *  - walking
 *  - transfer
 *  - riding
 */

const start_navigation = (type) => {
    let start = new AMap.Marker({
        position: props.begin
    });

    if (!start) {
        start = new AMap.Marker({
            position: [117.342581, 38.983879]
        })
    }

    let end = new AMap.Marker({
        position: props.target.location
    })
    if (!props.target.location) {
        let centroid = get_centroid(props.target.coordinates);
        end = new AMap.Marker({
            position: centroid
        })
    }

    let travelMode;
    let policy;

    switch (type) {
        case 'driving':
            props.map.plugin(["AMap.Driving"], function () {
                policy = AMap.DrivingPolicy.LEAST_TIME;
                travelMode = new AMap.Driving({
                    map: props.map,
                    policy: policy,
                    panel: "steps"
                });
                AMap.Event.addListener(travelMode, "complete", (result) => {
                    console.log('Driving completed', result);
                });
                travelMode.search(start.getPosition(), end.getPosition());
            });
            break;

        case 'riding':
            props.map.plugin(["AMap.Riding"], function () {
                policy = AMap.RidingPolicy.LEAST_TIME;
                travelMode = new AMap.Riding({
                    map: props.map,
                    policy: policy,
                    panel: "steps"
                });
                AMap.Event.addListener(travelMode, "complete", (result) => {
                    console.log('Riding completed', result);
                });
                travelMode.search(start.getPosition(), end.getPosition());
            });
            break;

        case 'walking':
            props.map.plugin(["AMap.Walking"], function () {
                travelMode = new AMap.Walking({
                    map: props.map,
                    panel: "steps"
                });
                AMap.Event.addListener(travelMode, "complete", (result) => {
                    console.log('Walking completed', result);
                });
                travelMode.search(start.getPosition(), end.getPosition());
            });
            break;

        default:
            console.error('Unsupported navigation type:', type);
            return;
    }

    EventBus.emit('clear_navigation', {});
    // 保存当前的导航模式
    EventBus.emit('update_navigation', {navigation: travelMode});

    let handler = {
        area_info_display_state: false,
        travel_model_display_state: false
    }
    EventBus.emit('toggle_menu', handler);
}
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

    console.log(x, y);
    return [x, y];
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

button {
    margin: 10px;
}

.travel_mode_menu {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 80%;
    width: 500px;
    text-align: center;
}

.travel_mode_menu ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.travel_mode_menu li {
    padding: 8px;
    cursor: pointer;
}

.travel_mode_menu li:hover {
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

.travelmode {
    padding: 8px;
    cursor: pointer;
}
</style>
