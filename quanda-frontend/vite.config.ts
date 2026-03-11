import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler', // 使用现代编译器，性能更好
        // 移除 additionalData，避免重复导入
        // 设计系统通过 index.scss 统一导入
      }
    },
    // 启用 CSS 模块热更新
    devSourcemap: true
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: false,
    open: false,
    hmr: {
      overlay: true // 显示错误覆盖层
    },
    watch: {
      usePolling: false, // Windows 下如热更新不生效，改为 true
      interval: 100,
      ignored: ['**/node_modules/**', '**/.git/**']
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/uploads': {
        target: 'http://localhost:8010',
        changeOrigin: true
      }
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['element-plus', '@element-plus/icons-vue'],
          'chart-vendor': ['echarts', 'vue-echarts']
        }
      }
    }
  },
  // 优化预构建
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'element-plus', 'echarts', 'vue-echarts']
  }
})
