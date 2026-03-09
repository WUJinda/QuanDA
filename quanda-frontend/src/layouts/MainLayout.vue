<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="header">
        <Header />
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from '@/components/Layout/Sidebar.vue'
import Header from '@/components/Layout/Header.vue'

const appStore = useAppStore()
const isCollapse = computed(() => appStore.isCollapse)
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;

  .sidebar {
    background: linear-gradient(180deg, #1a2942 0%, #0f1c2e 100%);
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .header {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(232, 232, 232, 0.6);
    padding: 0 20px;
    display: flex;
    align-items: center;
  }

  .main-content {
    background: #F5F7FA;
    padding: 20px;
    overflow-y: auto;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
