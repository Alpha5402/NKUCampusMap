import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    // 允许的域名列表
    allowedHosts: [
      'www.nkucampusmap.xin', // 添加你的域名
      'nkucampusmap.xin',     // 如果需要，也可以添加不带 www 的域名
    ],
    host: '0.0.0.0', // 允许外部访问
    
    port: 5173
  }
})
