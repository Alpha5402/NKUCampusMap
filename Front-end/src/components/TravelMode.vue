<template>
    <div class="travel_mode_menu">
        <button @click="start_navigation('driving')">驾车</button>
        <button @click="start_navigation('riding')">骑行</button>
        <button @click="start_navigation('walking')">步行</button>
        <button @click="start_navigation('transfer')">公交</button>
    </div>
</template>

<script setup>
import { defineProps } from 'vue';
import { EventBus } from './bus.js';

const props = defineProps({
    map: {
        type: Object,
        required: true
    },
    location: {
        type: Object,
        required: true
    }
});

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
        position: [117.342581,38.983879]
    })

    let end = new AMap.Marker({
        position: props.location
    })

    props.map.add(start);
    props.map.add(end);

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
                    policy: policy
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
                    map: props.map
                });
                AMap.Event.addListener(travelMode, "complete", (result) => {
                    console.log('Walking completed', result);
                });
                travelMode.search(start.getPosition(), end.getPosition());
            });
            break;

        case 'transfer':
            props.map.plugin(["AMap.Transfer"], function () {
                travelMode = new AMap.Transfer({
                    map: props.map
                });
                AMap.Event.addListener(travelMode, "complete", (result) => {
                    console.log('Transfer completed', result);
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
    EventBus.emit('update_navigation', { navigation: travelMode });

    let handler = { status: false };
    EventBus.emit('toggle_travel_mode_menu', handler);
}
</script>

<style scoped>

button {
    margin: 10px;
}

.travel_mode_menu {
    position: absolute;
    background-color: #fff;
    border: 1px solid #ccc;
    padding: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 100;
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
</style>
