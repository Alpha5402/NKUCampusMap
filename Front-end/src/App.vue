<template>
    <div id="wrap" class="my_map">
        <div id="map_container" :style="map_styles"></div>
        <div id = "area" v-if="map_rendered">
            <Area
                v-for="(area, index) in areas"
                :key="index"
                :map="map"
                :area_target="area"
            />
        </div>

        <AreaInfo
            v-if="map_rendered"
            v-show="area_info_display_status"
            :area_target="current_target"
        />
        <TravelMode
            v-if="travel_mode_display_status && map_rendered"
            :target="current_target"
            :map="map"
            :begin="navigation_begin"
        />
        <ImageProvider
            v-if="map_rendered"
            v-show= "image_provider_display_status"
            :target="current_target"
            :image_title="image_title"
            :image_index="image_index"
            :image_src="image_src"
        />
        <Response
            v-if="map_rendered"
            v-show="response_display_status"
            :result="response_result"
            :main_description="response_main_description"
            :areas_list="areas"
            :response_content="response_content"
        />
        />

        <GPS
            v-if="map_rendered"
            :map="map"
        ></GPS>
        <Input
            :content = "input_content"
        ></Input>
    </div>
    <div id = "steps" :style="steps_styles" v-show = "steps_display_status"></div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from 'vue'
import Area from './components/Area.vue';
import Input from './components/Input.vue';

import areas_data from './assets/Area.json';
import AreaInfo from "@/components/AreaInfo.vue";
import TravelMode from "@/components/TravelMode.vue";
import ImageProvider from "@/components/ImageProvider.vue";
import {EventBus} from "@/scripts/bus.js";
import GPS from "@/components/GPS.vue";
import Response from './components/Response.vue';

// map -- the map object
// rendered -- if the map has been rendered
// style -- make a reavtive style for dynameically admit the map for the navigation steps list
const map = ref(null);
const map_container = ref(null);
const map_rendered = ref(false);
const map_styles = ref( {
    margin: "0 auto",
    width: "100vw",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
})

// travel mode 
// display_status -- true: display, false: hide
// current_target -- target which is selected
// navigation_begin -- user location
// navigation -- navigation object, recording the current navigation
const travel_mode_display_status = ref(false);
const current_target = ref({ lng: 0, lat: 0});
const navigation_begin = ref({ lng: 0, lat: 0 });
const navigation = ref(null);

// area info
// display status -- true: display, false: hide
const area_info_display_status = ref(false);

// image provide
// display_status -- true: display, false: hide
const image_provider_display_status = ref(false);

// input
// content -- default content in input area
const input_content = ref("Hello world");

// areas -- a array of areas
const areas = ref(areas_data.areas); 

// steps
// display_status -- true: display, false: hide
const steps_display_status = ref(false);
const steps_styles = ref({
    width: '100vw',
    height: "30vh",
    zIndex: 100,
    background: '#fff',
    transition: 'height 0.3s ease'
});

// response
// result -- response result
// main_description -- main description of response
const response_result = ref([]);
const response_main_description = ref("");
const response_content = ref(null);
const response_display_status = ref(false);

const load_AMap_script = () => {
    return fetch('https://www.nkucampusmap.xin/api/get_security_key')
        .then(response => {
            if (!response.ok) {
                return Promise.reject('Failed to fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            window._AMapSecurityConfig = {securityJsCode: data.security_code};
            const api_key = data.api_key;

            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = `//webapi.amap.com/maps?v=2.0&key=${api_key}&plugin=AMap.Geolocation`;

                script.onload = () => {
                    // console.log("AMap script loaded successfully");
                    resolve();
                };

                script.onerror = (error) => {
                    // console.error("Failed to load AMap script", error);
                    reject(error);
                };

                document.head.appendChild(script);
            })
                .catch(error => {
                    return Promise.reject(error);
                })
        })
};

function showPermissionDeniedToast() {
    tt.showToast({
        title: "请开启定位权限",
        icon: "none",
        duration: 3000,
        success(res) {
            console.log("showToast 调用成功", res.errMsg);
            // 提示用户后，跳转到权限设置页面
            tt.openSetting({
                success(res) {
                    console.log("openSetting success: ", res.authSetting);
                },
                fail(err) {
                    console.log("openSetting fail: ", err);
                }
            });
        },
        fail(res) {
            console.log("showToast 调用失败", res.errMsg);
        }
    });
}

const feishu_auth = () => {
    const local_tt = document.createElement('script');
    const SCOPE_LOCATION = "scope.userLocation";
    const user_name = null;

    local_tt.src = 'https://lf1-cdn-tos.bytegoofy.com/goofy/lark/op/h5-js-sdk-1.5.26.js';
    local_tt.type = 'text/javascript';
    local_tt.async = true; // 异步加载

    // 调用config接口的当前网页url
    // 这里前端一定要用这种方式获取，不建议手写，以免获取到的链接和真实使用的有差距
    const url = encodeURIComponent(location.href.split("#")[0]);
    local_tt.onerror = () => {
        console.error('脚本加载失败！');
    };

    document.head.appendChild(local_tt);
    // 向接入方服务端发起请求，获取鉴权参数（appId、timestamp、nonceStr、signature）
    fetch(`https://www.nkucampusmap.xin/api/get_config_parameters?url=${url}`)
        .then(response => {
            if (!response.ok) {
                return Promise.reject('Failed to fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then((res) => {
            if (window.h5sdk) {
                window.h5sdk.error((err) => {
                    throw ("h5sdk error:", JSON.stringify(err));
                });

                console.log("appid: " + res.appId);

                window.h5sdk.config({
                    appId: res.appId,
                    timestamp: res.timestamp,
                    nonceStr: res.noncestr,
                    signature: res.signature,
                    jsApiList: ["startLocationUpdate", "getLocation", "getUserInfo"],
                    onSuccess: (res) => {
                        console.log(`config success: ${JSON.stringify(res)}`);
                    },
                    onFail: (err) => {
                        throw `config failed: ${JSON.stringify(err)}`;
                    },
                });

                // 完成鉴权后，可在 window.h5sdk.ready 里调用 JSAPI
                window.h5sdk.ready(() => {
                    // window.h5sdk.ready回调函数在环境准备就绪时触发
                    // 调用 getUserInfo API 获取已登录用户的基本信息，详细文档参见https://open.feishu.cn/document/uYjL24iN/ucjMx4yNyEjL3ITM
                    tt.getUserInfo({
                        // getUserInfo API 调用成功回调
                        success(res) {
                            input_content.value = res.userInfo.nickName;
                        },
                        fail(err) {
                            console.log(`getUserInfo failed:`, JSON.stringify(err));
                        },
                    });
                    tt.getLocation({
                        "type": "gcj02",
                        "timeout": 30,
                        "cacheTimeout": 30,
                        "accuracy": "best",
                        success(res) {
                            console.log(JSON.stringify(res));
                        },
                        fail(res) {
                            console.log(`getLocation fail: ${JSON.stringify(res)}`);
                        }
                    });
                    tt.showToast({
                        title: "鉴权成功",
                        icon: "success",
                        duration: 3000,
                        success(res) {
                            console.log("showToast 调用成功", res.errMsg);
                        },
                        fail(res) {
                            console.log("showToast 调用失败", res.errMsg);
                        },
                        complete(res) {
                            console.log("showToast 调用结束", res.errMsg);
                        },
                    });
                });
            } else {
                console.error("window.h5sdk was undefined");
            }
        })
        .catch(function (e) {
            console.error(e);
        });
}

const initialize_map = () => {
    try {
        if (typeof AMap !== 'undefined') {
            // console.log("Now initializing map...");
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

                map.value.on('click', (event) => {
                    let target = {
                        name: "选定位置",
                        location: [ event.lnglat.lng, event.lnglat.lat],
                        undocumented: true,
                        options: ["导航到这里"],
                        methods: ["navigation"]
                    };

                    toggle_menu("area_info", true, target)
                    //toggle_area_info_menu(true, target)
                    current_target.value = target;
                });

                // map.value.on('dblclick', () => {
                //     toggle_area_info(false, null, null)
                // });

                // map.value.on('mapmove', () => {
                //     toggle_area_info(false, null, null)
                // });

                // console.log("Successfully.");
                map_rendered.value = true;
            })();

        } else {
            console.error('AMap is not defined. Please check if the API script is loaded.');
        }
    }  catch (error) {
        console.error("Error in initialize_map:", error);
    }
};

const toggle_menu = (type, status, target) => {
    switch (type) {
        case "area_info":
            area_info_display_status.value = status;
            if (status) {
                if (target) {
                    current_target.value = target;
                } else {
                    console.error("When opening a area info menu, target must be provided.")
                }
            }
            break;
        case "travel_mode":
            travel_mode_display_status.value = status;
            break;  
        case "image_provider":
            image_provider_display_status.value = status;   
            break;
        default:
            console.error("Unknown menu type:", type);
    }
}


onMounted(async () => {
    try {
        await load_AMap_script();
        await feishu_auth();
        initialize_map();

        /** Set the display status of AreaInfo menu
         *  params
         *  - status(boolean) - if the menu should be shown (If it is false, the following two parameters do not need to be provided
         *  - target(Object) - which area object's menu should be called
         *  - position(Object) - where menu should be display
         * */
        // EventBus.on('toggle_area_info', (handler) => {
        //     toggle_area_info(handler.status, handler.target, handler.position);
        // });
        // /** Set the display status of TravelMode menu
        //  *  something necessary
        //  *  - status(boolean) - if the menu should be shown
        //  * */
        // EventBus.on('toggle_travel_mode_menu', (handler) => {
        //     // console.log("opening the travel mode menu")
        //     travel_mode_display_status.value = handler.status;
        //     travel_mode_Lnglat.value = current_target_Lnglat.value;
        //     travel_mode_target.value = handler.target;

        //     if (handler.status)
        //         travel_mode_position.value = {
        //             left: area_info_position.value.left,
        //             top: area_info_position.value.top,
        //         }
        // });
        /**
         * Set the menu display status
         * decide whether the display will be displayed.
         * parameters:
         * - areainfo_display_status
         * - travel_mode_display_status
         * */
        EventBus.on('toggle_menu', (handler) => {
            toggle_menu("travel_mode", handler.travel_mode_display_status, handler.target);
            toggle_menu("area_info", handler.area_info_display_status, handler.target)
            toggle_menu("image_provider", handler.image_provider_display_status, handler.target)
            
        })

        EventBus.on('update_navigation', (handler) => {
            navigation.value = handler.navigation;
            steps_display_status.value = true;
            const element = document.getElementById("steps");
            map_styles.value.height = "70vh";
            element.style.overflowY = "auto";  // 设置 overflow-y
            element.style.scrollbarWidth = "none";  // 设置 scrollbar-width（仅 Firefox 支持）
            element.style.msOverflowStyle = "none"; // 设置 -ms-overflow-style（IE/Edge）
        })

        EventBus.on('update_geolocation', (handler) => {
            navigation_begin.value = handler.geolocation;
        })

        EventBus.on('clear_navigation', (handler) => {
            if (navigation.value)
                navigation.value.clear();
        })

        EventBus.on('display_response', (handler) => {
            map_styles.value = handler.map_styles;
            response_display_status.value = handler.response_display_status;
            response_content.value = handler.response_content;
        })
    }  catch (error) {
        console.error("Error in onMounted:", error);
    }
});

onUnmounted(() => {
    // 在组件销毁时移除事件监听器，避免内存泄漏
    EventBus.off('toggle_area_info');
    EventBus.off('toggle_travel_mode_menu');
    EventBus.off('update_navigation');
    EventBus.off('clear_navigation');
});
</script>

<script>
</script>

<style scoped>
steps {
    width: 100vw;  /* 为地图留出足够空间 */
    height: 100vh;  /* 高度为全屏 */
    overflow-y: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;


}

#steps::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Edge */
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
    overflow: hidden;      /* 禁用滚动 */
    touch-action: none;   /* 禁用触摸事件 */
    position: fixed;      /* 防止 iOS 页面跳动 */
    width: 100%;
}

#map_container {
    width: 100%;
    height: 100%;
}

.my-map {
    margin: 0 auto;
    width: 100vw;  /* 为地图留出足够空间 */
    height: 100vh;  /* 高度为全屏 */
    display: flex;  /* 使用flex布局 */
    justify-content: center;  /* 水平居中 */
    align-items: center  /* 垂直居中 */
}

.my_map .icon {
    height: 100vh;
    width: 100vw;
    background: url(//a.amap.com/lbs-dev-yuntu/static/web/image/tools/creater/marker.png) no-repeat;
}

.amap-container {
    height: auto;
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

.modal-open {
    overflow: hidden;      /* 禁用滚动 */
    touch-action: none;   /* 禁用触摸事件 */
    position: fixed;      /* 防止 iOS 页面跳动 */
    width: 100%;
}
</style>
