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
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(232, 232, 232, 0.6);
  transition: all 0.3s ease;

  .left {
    display: flex;
    align-items: center;
    gap: 20px;

    .collapse-icon {
      font-size: 20px;
      cursor: pointer;
      color: #595959;
      transition: all 0.3s ease;
      padding: 8px;
      border-radius: 8px;

      &:hover {
        color: #5B8FF9;
        background: rgba(91, 143, 249, 0.08);
      }
    }

    :deep(.el-breadcrumb) {
      .el-breadcrumb__item {
        .el-breadcrumb__inner {
          color: #595959;
          font-weight: 500;

          &:hover {
            color: #5B8FF9;
          }
        }

        &:last-child .el-breadcrumb__inner {
          color: #262626;
          font-weight: 600;
        }
      }

      .el-breadcrumb__separator {
        color: #8C8C8C;
      }
    }
  }

  .right {
    display: flex;
    align-items: center;
    gap: 20px;

    .notification {
      cursor: pointer;
      color: #595959;
      transition: all 0.3s ease;
      padding: 8px;
      border-radius: 8px;

      &:hover {
        color: #5B8FF9;
        background: rgba(91, 143, 249, 0.08);
      }

      :deep(.el-badge__content) {
        background-color: #FF7A7E;
        border-color: #FFFFFF;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: 8px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba(91, 143, 249, 0.06);
      }

      .username {
        font-size: 14px;
        font-weight: 500;
        color: #262626;
      }

      :deep(.el-avatar) {
        border: 2px solid rgba(91, 143, 249, 0.1);
      }
    }
  }
}
</style>
