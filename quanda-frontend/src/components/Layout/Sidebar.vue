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
      background-color="#001529"
      text-color="#fff"
      active-text-color="#1890ff"
      router
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
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .el-menu {
    border-right: none;
  }
}
</style>
