<template>
  <div class="header-container">
    <div class="left">
      <el-icon class="collapse-icon" @click="toggleSidebar">
        <Fold v-if="!isCollapse" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="right">
      <el-badge :value="12" class="notification">
        <el-icon :size="20"><Bell /></el-icon>
      </el-badge>
      <el-dropdown>
        <div class="user-info">
          <el-avatar :size="32" />
          <span class="username">管理员</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人中心</el-dropdown-item>
            <el-dropdown-item>系统设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const currentTitle = computed(() => route.meta?.title || '')

const toggleSidebar = () => {
  appStore.toggleSidebar()
}
</script>

<style lang="scss" scoped>
.header-container {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .left {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .collapse-icon {
      font-size: 20px;
      cursor: pointer;
      transition: color 0.3s;
      
      &:hover {
        color: #1890ff;
      }
    }
  }
  
  .right {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .notification {
      cursor: pointer;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      
      .username {
        font-size: 14px;
      }
    }
  }
}
</style>
