import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

// 导入 Font Awesome 相关模块
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'; // 放大镜图标

// 添加所需的图标到库
library.add(faMagnifyingGlass);

const app = createApp(App); // ✅ 先创建 Vue 实例
app.component('font-awesome-icon', FontAwesomeIcon); // ✅ 在 `mount` 之前注册组件
app.mount('#app'); // ✅ 最后挂载
