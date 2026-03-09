<template>
  <div class="sidebar-container">
    <div class="logo">
      <span v-if="!isCollapse">QuanDA</span>
      <span v-else>QA</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :unique-opened="true"
      background-color="transparent"
      text-color="#FFFFFF"
      active-text-color="#FFFFFF"
      router
      class="sidebar-menu"
    >
      <el-menu-item
        v-for="route in menuRoutes"
        :key="route.path"
        :index="route.path"
      >
        <el-icon><component :is="route.meta?.icon" /></el-icon>
        <template #title>{{ route.meta?.title }}</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const activeMenu = computed(() => route.path)

const menuRoutes = [
  { path: '/dashboard', meta: { title: '仪表盘', icon: 'DataAnalysis' } },
  { path: '/market', meta: { title: '市场行情', icon: 'TrendCharts' } },
  { path: '/futures', meta: { title: '期货分析', icon: 'Histogram' } },
  { path: '/account', meta: { title: '账户管理', icon: 'Wallet' } },
  { path: '/backtest', meta: { title: '回测系统', icon: 'Operation' } },
  { path: '/strategy', meta: { title: '策略管理', icon: 'Document' } },
  { path: '/strategy-reference', meta: { title: '策略参考库', icon: 'Collection' } }
]
</script>

<style lang="scss" scoped>
.sidebar-container {
  height: 100%;
  background: linear-gradient(180deg, #1a2942 0%, #0f1c2e 100%);
  position: relative;
  overflow: hidden;

  // 渐变装饰效果
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 30%, rgba(91, 143, 249, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(146, 84, 222, 0.06) 0%, transparent 50%);
    pointer-events: none;
  }

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
    z-index: 1;
    letter-spacing: 1px;

    // 渐变文字效果
    background: linear-gradient(135deg, #FFFFFF 0%, #E8E8E8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  // 菜单样式
  .sidebar-menu {
    border-right: none;
    position: relative;
    z-index: 1;
    padding: 8px 0;

    :deep(.el-menu-item) {
      color: rgba(255, 255, 255, 0.65);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border-radius: 0;
      margin: 0;
      position: relative;

      &:hover {
        background: rgba(91, 143, 249, 0.12) !important;
        color: #FFFFFF !important;

        &::before {
          opacity: 1;
        }
      }

      &.is-active {
        background: linear-gradient(90deg, rgba(91, 143, 249, 0.2) 0%, rgba(91, 143, 249, 0.05) 100%) !important;
        color: #FFFFFF !important;

        &::before {
          opacity: 1;
          background: linear-gradient(180deg, #7AA5FF 0%, #5B8FF9 100%);
        }
      }

      // 左侧高亮条
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #7AA5FF 0%, #5B8FF9 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      .el-icon {
        color: inherit;
        font-size: 18px;
      }
    }
  }

  .el-menu {
    border-right: none;
  }
}
</style>
