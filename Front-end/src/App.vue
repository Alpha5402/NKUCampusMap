<template>
    <div id="wrap" class="my_map">
        <div id="map_container"></div>
        <Area
            v-if="map_rendered"
            v-for="(area, index) in areas"
            :key="index"
            :map="map"
            :area_target="area"
        />

        <AreaInfo
            v-if="sub_menu_display_state && map_rendered"
            :area_target="sub_menu_target"
            :style="{ top: sub_menu_position.top + 'px', left: sub_menu_position.left + 'px' }"
        />
        <TravelMode
            v-if="travel_mode_display_state && map_rendered"
            :area_target="travel_mode_target"
            :location="current_target_Lnglat"
            :map="map"
            :style="{ top: travel_mode_position.top + 'px', left: travel_mode_position.left + 'px' }"
        />
        <GPS
            v-if="map_rendered"
            :map="map"
        ></GPS>
        <Input></Input>

    </div>
    <div id = "steps"></div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from 'vue'
import Area from './components/Area.vue';
import Input from './components/Input.vue';

import areas_data from './assets/Area.json';
import AreaInfo from "@/components/AreaInfo.vue";
import TravelMode from "@/components/TravelMode.vue";
import {EventBus} from "@/components/bus.js";
import GPS from "@/components/GPS.vue";

const map = ref(null);
const map_container = ref(null);
const map_rendered = ref(false);
const travel_mode_display_state = ref(false);
const travel_mode_target = ref(null);
const travel_mode_Lnglat = ref({ lng: 0, lat: 0});
const current_target_Lnglat = ref({ lng: 0, lat: 0});
const travel_mode_position = ref({ top: 0, left: 0 });
const sub_menu_display_state = ref(false);
const sub_menu_target = ref(null);
const sub_menu_position = ref({ top: 0, left: 0 });  // 菜单显示位置
let navigation = null;

const areas = ref(areas_data.areas); // 存储区域数据

// 动态加载高德地图 API
const load_AMap_script = async () => {
    const response = await fetch('http://localhost:5000/get_security_key');
    const data = await response.json();
    window._AMapSecurityConfig = { securityJsCode: data.security_code };
    const api_key = data.api_key;

    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = `//webapi.amap.com/maps?v=2.0&key=${api_key}&plugin=AMap.Geolocation`;

        script.onload = () => {
            console.log("AMap script loaded successfully");
            resolve();
        };

        script.onerror = (error) => {
            console.error("Failed to load AMap script", error);
            reject(error);
        };

        document.head.appendChild(script);
    });
};


// 地图初始化函数
const initialize_map = () => {
    try {
        // 确保 AMap 对象已定义
        if (typeof AMap !== 'undefined') {
            console.log("Now initializing map...");
            (function() {
                var level = 16,
                    center = {lng: 117.346974, lat: 38.986286};

                map.value = new AMap.Map("map_container", {
                    center: new AMap.LngLat(center.lng, center.lat),
                    zoom: 18,
                    level: level,
                    keyboardEnable: true,
                    dragEnable: true,
                    scrollWheel: true,
                    doubleClickZoom: true,
                    mapStyle: "amap://styles/93cf6fcd07ed0fc4ec70b74a9a99ec33"
                });

                console.log("Successfully.");
                map_rendered.value = true;
            })();

        } else {
            console.error('AMap is not defined. Please check if the API script is loaded.');
        }
    }  catch (error) {
        console.error("Error in initialize_map:", error);
    }
};

onMounted(async () => {
    try {
        await load_AMap_script();
        initialize_map();

        /** Set the display state of AreaInfo menu
         *  params
         *  - status(boolean) - if the menu should be shown (If it is false, the following two parameters do not need to be provided
         *  - target(Object) - which area object's menu should be called
         *  - position(Object) - where menu should be display
         * */
        EventBus.on('toggle_sub_menu', (handler) => {
            sub_menu_display_state.value = handler.status;
            if (handler.status) {
                if (handler.position){
                    sub_menu_position.value = {
                        left: handler.position.x,
                        top: handler.position.y,
                    }
                } else
                    console.error("When opening a sub menu, position must be provided.")

                if (handler.target) {
                    sub_menu_target.value = handler.target;
                    current_target_Lnglat.value = get_centroid(sub_menu_target.value.coordinates);
                }
                else
                    console.error("When opening a sub menu, target must be provided.")

                if (travel_mode_display_state)
                    travel_mode_display_state.value = false;
            } else {
                sub_menu_target.value = null;
                sub_menu_position.value = null;
            }
        });
        /** Set the display state of TravelMode menu
         *  something necessary
         *  - status(boolean) - if the menu should be shown
         * */
        EventBus.on('toggle_travel_mode_menu', (handler) => {
            console.log("opening the travel mode menu")
            travel_mode_display_state.value = handler.status;
            travel_mode_Lnglat.value = current_target_Lnglat.value;
            travel_mode_target.value = handler.target;

            if (handler.status)
                travel_mode_position.value = {
                    left: sub_menu_position.value.left,
                    top: sub_menu_position.value.top,
                }
        });

        EventBus.on('update_navigation', (handler) => {
            navigation = handler.navigation;
        })

        EventBus.on('clear_navigation', (handler) => {
            if (navigation)
                navigation.clear();
        })
    }  catch (error) {
        console.error("Error in onMounted:", error);
    }
});

onUnmounted(() => {
    // 在组件销毁时移除事件监听器，避免内存泄漏
    EventBus.off('toggle_sub_menu');
    EventBus.off('toggle_travel_mode_menu');
    EventBus.off('update_navigation');
    EventBus.off('clear_navigation');
});
</script>

<script>
</script>

<style scoped>
steps {
    width: 20vw;  /* 为地图留出足够空间 */
    height: 100vh;  /* 高度为全屏 */
    transform: translateX(-50%);
}

header {
    line-height: 1.5;
}

@media (min-width: 1024px) {
    header {
        display: flex;
        place-items: center;
        padding-right: calc(var(--section-gap) / 2);
    }

    .logo {
        margin: 0 2rem 0 0;
    }

    header .wrapper {
        display: flex;
        place-items: flex-start;
        flex-wrap: wrap;
    }
}

html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
}

.my_map {
    margin: 0 auto;
    width: 80vw;  /* 为地图留出足够空间 */
    height: 100vh;  /* 高度为全屏 */
    display: flex;  /* 使用flex布局 */
    justify-content: center;  /* 水平居中 */
    align-items: center;  /* 垂直居中 */
}

#map_container {
    width: 100%;
    height: 100%;
}


.my_map .icon {
    background: url(//a.amap.com/lbs-dev-yuntu/static/web/image/tools/creater/marker.png) no-repeat;
}

.amap-container {
    height: 100%;
}

.myinfowindow{
    width: 240px;
    min-height: 50px;
}

.myinfowindow h5{
    height: 20px;
    line-height: 20px;
    overflow: hidden;
    font-size: 14px;
    font-weight: bold;
    width: 220px;
    text-overflow: ellipsis;
    word-break: break-all;
    white-space: nowrap;
}

.myinfowindow div{
    margin-top: 10px;
    min-height: 40px;
    line-height: 20px;
    font-size: 13px;
    color: #6f6f6f;
}
</style>
