<template>
  <div class="sidebar-container">
    <!-- Logo 区域 -->
    <div class="logo-section">
      <div class="logo-wrapper">
        <div class="logo-icon">
          <span class="logo-text" v-if="!isCollapse">QuanDA</span>
          <span class="logo-text-collapsed" v-else>QA</span>
        </div>
        <div class="logo-subtitle" v-if="!isCollapse">量化交易平台</div>
      </div>
    </div>

    <!-- 菜单区域 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :unique-opened="true"
      background-color="transparent"
      text-color="rgba(255, 255, 255, 0.7)"
      active-text-color="#FFFFFF"
      router
      class="sidebar-menu"
    >
      <el-menu-item
        v-for="route in menuRoutes"
        :key="route.path"
        :index="route.path"
        class="menu-item"
      >
        <el-icon class="menu-icon">
          <component :is="route.meta?.icon" />
        </el-icon>
        <template #title>
          <span class="menu-title">{{ route.meta?.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>

    <!-- 底部装饰 -->
    <div class="sidebar-footer" v-if="!isCollapse">
      <div class="footer-decoration"></div>
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
@use '@/styles/design-system.scss' as *;

.sidebar-container {
  height: 100%;
  background: linear-gradient(180deg, #1a2942 0%, #0f1c2e 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  /* 双色渐变装饰背景 */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 20%, rgba(91, 143, 249, 0.12) 0%, transparent 40%),
      radial-gradient(circle at 80% 50%, rgba(255, 140, 66, 0.08) 0%, transparent 40%),
      radial-gradient(circle at 50% 80%, rgba(146, 84, 222, 0.06) 0%, transparent 40%);
    pointer-events: none;
    animation: gradientShift 15s ease-in-out infinite;
  }

  /* 顶部装饰条 */
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #5B8FF9 0%, #FF8C42 50%, #9254DE 100%);
    z-index: 10;
  }

  /* Logo 区域 */
  .logo-section {
    padding: 24px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
    z-index: 1;
    background: rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);

    .logo-wrapper {
      text-align: center;
      animation: fadeInDown 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .logo-icon {
      margin-bottom: 8px;
    }

    .logo-text {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: 2px;
      background: linear-gradient(135deg, #5B8FF9 0%, #FF8C42 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: inline-block;
      text-shadow: 0 0 30px rgba(91, 143, 249, 0.3);
      animation: pulse 3s ease-in-out infinite;
    }

    .logo-text-collapsed {
      font-size: 24px;
      font-weight: 800;
      letter-spacing: 1px;
      background: linear-gradient(135deg, #5B8FF9 0%, #FF8C42 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: inline-block;
    }

    .logo-subtitle {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.5);
      letter-spacing: 2px;
      margin-top: 4px;
      font-weight: 500;
    }
  }

  /* 菜单区域 */
  .sidebar-menu {
    flex: 1;
    border-right: none;
    position: relative;
    z-index: 1;
    padding: 16px 8px;
    overflow-y: auto;
    overflow-x: hidden;

    /* 自定义滚动条 */
    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.05);
    }

    &::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, #5B8FF9 0%, #FF8C42 100%);
      border-radius: 2px;

      &:hover {
        background: linear-gradient(180deg, #7AA5FF 0%, #FFA666 100%);
      }
    }

    /* 菜单项样式 */
    :deep(.el-menu-item) {
      color: rgba(255, 255, 255, 0.7);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border-radius: 12px;
      margin: 4px 0;
      position: relative;
      height: 48px;
      line-height: 48px;
      overflow: hidden;

      /* 背景装饰 */
      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, rgba(91, 143, 249, 0.15) 0%, rgba(255, 140, 66, 0.08) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 12px;
      }

      /* 悬停效果 */
      &:hover {
        background: rgba(91, 143, 249, 0.12) !important;
        color: #FFFFFF !important;
        transform: translateX(4px);

        &::after {
          opacity: 1;
        }

        &::before {
          opacity: 1;
          width: 4px;
        }

        .menu-icon {
          transform: scale(1.15);
          color: #5B8FF9;
        }

        .menu-title {
          color: #FFFFFF;
        }
      }

      /* 激活状态 */
      &.is-active {
        background: linear-gradient(90deg, rgba(91, 143, 249, 0.25) 0%, rgba(255, 140, 66, 0.12) 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(91, 143, 249, 0.2);

        &::after {
          opacity: 1;
        }

        &::before {
          opacity: 1;
          width: 4px;
          background: linear-gradient(180deg, #5B8FF9 0%, #FF8C42 100%);
        }

        .menu-icon {
          color: #5B8FF9;
          transform: scale(1.1);
          animation: iconPulse 2s ease-in-out infinite;
        }

        .menu-title {
          font-weight: 600;
          color: #FFFFFF;
        }
      }

      /* 左侧高亮条 */
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        height: 24px;
        width: 0;
        background: linear-gradient(180deg, #5B8FF9 0%, #FF8C42 100%);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 0 4px 4px 0;
      }

      /* 图标样式 */
      .menu-icon {
        color: inherit;
        font-size: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-right: 12px;
      }

      /* 标题样式 */
      .menu-title {
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
      }
    }

    /* 折叠状态 */
    &.el-menu--collapse {
      :deep(.el-menu-item) {
        justify-content: center;
        padding: 0 !important;

        .menu-icon {
          margin-right: 0;
        }
      }
    }
  }

  /* 底部装饰 */
  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
    z-index: 1;
    background: rgba(0, 0, 0, 0.2);

    .footer-decoration {
      height: 3px;
      background: linear-gradient(90deg, #5B8FF9 0%, #FF8C42 50%, #9254DE 100%);
      border-radius: 2px;
      animation: shimmer 3s ease-in-out infinite;
      background-size: 200% 100%;
    }
  }

  /* 移除默认边框 */
  .el-menu {
    border-right: none;
  }
}

/* 动画定义 */
@keyframes gradientShift {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

@keyframes iconPulse {
  0%, 100% {
    transform: scale(1.1);
  }
  50% {
    transform: scale(1.15);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
