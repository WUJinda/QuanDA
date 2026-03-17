<template>
  <div class="header-container">
    <!-- 左侧区域 -->
    <div class="header-left">
      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleSidebar">
        <el-icon :size="20">
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>

      <!-- Logo区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <el-icon :size="24"><TrendCharts /></el-icon>
        </div>
        <span class="logo-text">QuanDA</span>
      </div>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 面包屑导航 -->
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentTitle">
          {{ currentTitle }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 右侧区域 -->
    <div class="header-right">
      <!-- 搜索框 -->
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索功能..."
          :prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
        />
      </div>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <!-- 全屏切换 -->
        <el-tooltip content="全屏" placement="bottom">
          <div class="action-btn" @click="toggleFullscreen">
            <el-icon :size="18">
              <FullScreen v-if="!isFullscreen" />
              <Aim v-else />
            </el-icon>
          </div>
        </el-tooltip>

        <!-- 通知 -->
        <el-tooltip content="通知" placement="bottom">
          <el-badge :value="notificationCount" :max="99" class="action-btn notification-badge">
            <div class="action-btn-inner" @click="handleNotification">
              <el-icon :size="18"><Bell /></el-icon>
            </div>
          </el-badge>
        </el-tooltip>

        <!-- 帮助 -->
        <el-tooltip content="帮助文档" placement="bottom">
          <div class="action-btn" @click="handleHelp">
            <el-icon :size="18"><QuestionFilled /></el-icon>
          </div>
        </el-tooltip>
      </div>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 用户信息 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-section">
          <el-avatar :size="36" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-info">
            <span class="username">{{ username }}</span>
            <span class="user-role">管理员</span>
          </div>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="user-dropdown">
            <el-dropdown-item command="account">
              <el-icon><Wallet /></el-icon>
              <span>账户管理</span>
            </el-dropdown-item>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-dropdown-item>
            <el-dropdown-item command="theme">
              <el-icon><Sunny /></el-icon>
              <span>主题切换</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import {
  Fold,
  Expand,
  TrendCharts,
  HomeFilled,
  Search,
  FullScreen,
  Aim,
  Bell,
  QuestionFilled,
  User,
  ArrowDown,
  Setting,
  Sunny,
  SwitchButton,
  Wallet
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const searchKeyword = ref('')
const isFullscreen = ref(false)
const notificationCount = ref(12)
const username = ref('管理员')

const isCollapse = computed(() => appStore.isCollapse)
const currentTitle = computed(() => route.meta?.title || '')

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    ElMessage.info(`搜索: ${searchKeyword.value}`)
  }
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const handleNotification = () => {
  ElMessage.info('通知功能开发中')
}

const handleHelp = () => {
  ElMessage.info('帮助文档开发中')
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'account':
      router.push('/account')
      break
    case 'profile':
      ElMessage.info('个人中心')
      break
    case 'settings':
      ElMessage.info('系统设置')
      break
    case 'theme':
      ElMessage.info('主题切换')
      break
    case 'logout':
      ElMessage.success('退出登录成功')
      router.push('/login')
      break
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.header-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 spacing(lg);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(232, 232, 232, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  transition: all transition(base) easing(smooth);

  // ==================== 左侧区域 ====================
  .header-left {
    display: flex;
    align-items: center;
    gap: spacing(lg);
    flex: 1;

    // 折叠按钮
    .collapse-btn {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: radius(md);
      cursor: pointer;
      color: color(text-secondary);
      background: color(bg-secondary);
      transition: all transition(fast) easing(smooth);

      &:hover {
        color: color(primary);
        background: rgba(91, 143, 249, 0.1);
        transform: scale(1.05);
      }

      &:active {
        transform: scale(0.95);
      }
    }

    // Logo区域
    .logo-section {
      display: flex;
      align-items: center;
      gap: spacing(sm);
      padding: spacing(sm) spacing(md);
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.08) 0%, rgba(122, 165, 255, 0.05) 100%);
      border-radius: radius(md);
      transition: all transition(base) easing(smooth);

      &:hover {
        background: linear-gradient(135deg, rgba(91, 143, 249, 0.12) 0%, rgba(122, 165, 255, 0.08) 100%);
        transform: translateY(-1px);
      }

      .logo-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        border-radius: radius(sm);
        color: #FFFFFF;
        box-shadow: shadow(xs);
      }

      .logo-text {
        font-size: font-size(lg);
        font-weight: font-weight(bold);
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.5px;
      }
    }

    // 分隔线
    .divider {
      width: 1px;
      height: 24px;
      background: linear-gradient(180deg, transparent 0%, color(border-light) 50%, transparent 100%);
    }

    // 面包屑
    .breadcrumb {
      :deep(.el-breadcrumb__item) {
        .el-breadcrumb__inner {
          display: flex;
          align-items: center;
          gap: spacing(xs);
          color: color(text-secondary);
          font-weight: font-weight(medium);
          font-size: font-size(sm);
          transition: all transition(fast) easing(smooth);
          padding: 4px spacing(sm);
          border-radius: radius(sm);

          &:hover {
            color: color(primary);
            background: rgba(91, 143, 249, 0.06);
          }

          .el-icon {
            font-size: font-size(base);
          }
        }

        &:last-child .el-breadcrumb__inner {
          color: color(text-primary);
          font-weight: font-weight(semibold);
          background: rgba(91, 143, 249, 0.08);
        }
      }

      :deep(.el-breadcrumb__separator) {
        color: color(text-tertiary);
        margin: 0 spacing(xs);
      }
    }
  }

  // ==================== 右侧区域 ====================
  .header-right {
    display: flex;
    align-items: center;
    gap: spacing(md);

    // 搜索框
    .search-box {
      width: 240px;
      transition: all transition(base) easing(smooth);

      &:focus-within {
        width: 280px;
      }

      :deep(.el-input) {
        .el-input__wrapper {
          background: color(bg-secondary);
          border-radius: radius(lg);
          border: 1px solid transparent;
          box-shadow: none;
          transition: all transition(fast) easing(smooth);

          &:hover {
            background: color(bg-hover);
            border-color: color(border-light);
          }

          &.is-focus {
            background: #FFFFFF;
            border-color: color(primary);
            box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
          }

          .el-input__inner {
            font-size: font-size(sm);
            color: color(text-primary);

            &::placeholder {
              color: color(text-tertiary);
            }
          }

          .el-input__prefix {
            color: color(text-tertiary);
          }
        }
      }
    }

    // 快捷操作
    .quick-actions {
      display: flex;
      align-items: center;
      gap: spacing(xs);

      .action-btn {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: radius(md);
        cursor: pointer;
        color: color(text-secondary);
        background: color(bg-secondary);
        transition: all transition(fast) easing(smooth);
        position: relative;

        &:hover {
          color: color(primary);
          background: rgba(91, 143, 249, 0.1);
          transform: translateY(-2px);
          box-shadow: shadow(sm);
        }

        &:active {
          transform: translateY(0);
        }
      }

      .notification-badge {
        :deep(.el-badge__content) {
          background: linear-gradient(135deg, #FF7A7E 0%, #FF9D9F 100%);
          border: 2px solid #FFFFFF;
          font-weight: font-weight(semibold);
          font-size: font-size(xs);
          box-shadow: shadow(xs);
        }

        .action-btn-inner {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: radius(md);
          cursor: pointer;
          color: color(text-secondary);
          background: color(bg-secondary);
          transition: all transition(fast) easing(smooth);

          &:hover {
            color: color(primary);
            background: rgba(91, 143, 249, 0.1);
            transform: translateY(-2px);
            box-shadow: shadow(sm);
          }
        }
      }
    }

    // 用户区域
    .user-section {
      display: flex;
      align-items: center;
      gap: spacing(sm);
      padding: spacing(xs) spacing(md);
      border-radius: radius(lg);
      cursor: pointer;
      background: color(bg-secondary);
      transition: all transition(base) easing(smooth);

      &:hover {
        background: rgba(91, 143, 249, 0.08);
        transform: translateY(-1px);
        box-shadow: shadow(sm);

        .dropdown-icon {
          transform: rotate(180deg);
        }
      }

      .user-avatar {
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        color: #FFFFFF;
        border: 2px solid rgba(91, 143, 249, 0.2);
        box-shadow: shadow(xs);
        transition: all transition(fast) easing(smooth);

        &:hover {
          transform: scale(1.05);
          box-shadow: shadow(sm);
        }
      }

      .user-info {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .username {
          font-size: font-size(sm);
          font-weight: font-weight(semibold);
          color: color(text-primary);
          line-height: 1.2;
        }

        .user-role {
          font-size: font-size(xs);
          color: color(text-tertiary);
          line-height: 1.2;
        }
      }

      .dropdown-icon {
        color: color(text-tertiary);
        transition: all transition(base) easing(smooth);
        font-size: font-size(sm);
      }
    }
  }

  // ==================== 响应式 ====================
  @media (max-width: 1200px) {
    .header-left {
      .logo-section {
        .logo-text {
          display: none;
        }
      }
    }

    .header-right {
      .search-box {
        width: 180px;

        &:focus-within {
          width: 220px;
        }
      }
    }
  }

  @media (max-width: 768px) {
    padding: 0 spacing(base);

    .header-left {
      gap: spacing(sm);

      .logo-section {
        display: none;
      }

      .divider {
        display: none;
      }
    }

    .header-right {
      gap: spacing(xs);

      .search-box {
        display: none;
      }

      .quick-actions {
        .action-btn {
          width: 36px;
          height: 36px;
        }
      }

      .user-section {
        padding: spacing(xs);

        .user-info {
          display: none;
        }

        .dropdown-icon {
          display: none;
        }
      }
    }
  }
}

// ==================== 下拉菜单样式 ====================
:deep(.user-dropdown) {
  margin-top: spacing(sm);
  border-radius: radius(lg);
  border: 1px solid color(border-light);
  box-shadow: shadow(lg);
  padding: spacing(xs);

  .el-dropdown-menu__item {
    display: flex;
    align-items: center;
    gap: spacing(sm);
    padding: spacing(sm) spacing(md);
    border-radius: radius(md);
    font-size: font-size(sm);
    font-weight: font-weight(medium);
    color: color(text-primary);
    transition: all transition(fast) easing(smooth);

    .el-icon {
      font-size: font-size(base);
      color: color(text-secondary);
      transition: all transition(fast) easing(smooth);
    }

    &:hover {
      background: rgba(91, 143, 249, 0.08);
      color: color(primary);

      .el-icon {
        color: color(primary);
        transform: scale(1.1);
      }
    }

    &:not(:last-child) {
      margin-bottom: spacing(xs);
    }
  }

  .el-dropdown-menu__item--divided {
    margin-top: spacing(xs);
    padding-top: spacing(sm);
    border-top: 1px solid color(border-light);

    &:hover {
      background: rgba(255, 122, 126, 0.08);
      color: color(danger);

      .el-icon {
        color: color(danger);
      }
    }
  }
}
</style>
