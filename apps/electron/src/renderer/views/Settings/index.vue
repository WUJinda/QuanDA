<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>
        <el-icon><Setting /></el-icon>
        系统设置
      </h1>
      <p class="subtitle">配置系统参数和环境</p>
    </div>

    <div class="settings-container">
      <!-- 演示模式开关 -->
      <div class="setting-card">
        <div class="card-header">
          <h3>
            <el-icon><TrendCharts /></el-icon>
            演示模式
          </h3>
          <el-switch v-model="config.demoMode" @change="handleDemoModeChange" />
        </div>
        <p class="card-description">
          启用演示模式将使用模拟数据，无需真实数据源连接。适合用于产品演示和功能测试。
        </p>
        <el-alert
          v-if="config.demoMode"
          type="info"
          :closable="false"
          show-icon
        >
          当前处于演示模式，所有数据均为模拟数据。
        </el-alert>
      </div>

      <!-- MongoDB 配置 -->
      <div class="setting-card">
        <div class="card-header">
          <h3>
            <el-icon><Coin /></el-icon>
            MongoDB 数据库
          </h3>
          <el-switch v-model="config.mongodb.enabled" @change="handleMongoEnabledChange" />
        </div>
        <p class="card-description">
          MongoDB 用于存储账户数据、策略参考等信息。如未启用，将使用内存模式（数据不持久化）。
        </p>
        <el-form :model="config.mongodb" label-width="120px" class="setting-form">
          <el-form-item label="服务器地址">
            <el-input
              v-model="config.mongodb.host"
              placeholder="localhost"
              :disabled="!config.mongodb.enabled"
            />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number
              v-model="config.mongodb.port"
              :min="1024"
              :max="65535"
              :disabled="!config.mongodb.enabled"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- Python 配置 -->
      <div class="setting-card">
        <div class="card-header">
          <h3>
            <el-icon><Document /></el-icon>
            Python 环境
          </h3>
        </div>
        <p class="card-description">
          Python 用于运行后端服务和执行回测任务。
        </p>
        <el-form label-width="120px" class="setting-form">
          <el-form-item label="Python 路径">
            <el-input
              v-model="config.python.path"
              placeholder="D:\\Programs\\Python\\Python313\\python.exe"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 后端配置 -->
      <div class="setting-card">
        <div class="card-header">
          <h3>
            <el-icon><Connection /></el-icon>
            后端服务
          </h3>
        </div>
        <p class="card-description">
          Python 后端 Web 服务配置。
        </p>
        <el-form label-width="120px" class="setting-form">
          <el-form-item label="服务器地址">
            <el-input v-model="config.backend.host" placeholder="localhost" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input-number v-model="config.backend.port" :min="1024" :max="65535" />
          </el-form-item>
        </el-form>
      </div>

      <!-- 操作按钮 -->
      <div class="action-bar">
        <el-button @click="handleReset">
          <el-icon><RefreshLeft /></el-icon>
          重置默认
        </el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  TrendCharts,
  Coin,
  Document,
  Connection,
  RefreshLeft,
  Check
} from '@element-plus/icons-vue'
import { getConfig, saveConfig, resetConfig, defaultConfig, type AppConfig } from '@/api/config'

const config = ref<AppConfig>({ ...defaultConfig })
const saving = ref(false)

onMounted(async () => {
  try {
    config.value = await getConfig()
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
})

const handleDemoModeChange = (value: boolean) => {
  if (value) {
    ElMessage.info('演示模式已启用，将使用模拟数据')
  }
}

const handleMongoEnabledChange = (value: boolean) => {
  if (value) {
    ElMessage.info('MongoDB 已启用，请确保服务正在运行')
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await saveConfig(config.value)
    ElMessage.success('配置保存成功，请重启应用以应用更改')
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    saving.value = false
  }
}

const handleReset = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有配置为默认值吗？',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await resetConfig()
    config.value = { ...defaultConfig }
    ElMessage.success('配置已重置为默认值')
  } catch {
    // 用户取消
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.settings-page {
  padding: spacing(lg);
  background: color(bg-secondary);
  min-height: 100vh;

  .page-header {
    margin-bottom: spacing(xl);

    h1 {
      font-size: font-size(huge);
      font-weight: font-weight(bold);
      color: color(text-primary);
      margin: 0 0 spacing(xs) 0;
      display: flex;
      align-items: center;
      gap: spacing(sm);
    }

    .subtitle {
      font-size: font-size(base);
      color: color(text-tertiary);
      margin: 0;
      padding-left: spacing(xxl);
    }
  }

  .settings-container {
    display: flex;
    flex-direction: column;
    gap: spacing(xl);
    max-width: 800px;
    margin: 0 auto;
  }

  .setting-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    transition: all transition(base) easing(smooth);

    &:hover {
      box-shadow: shadow(md);
      border-color: color(primary-light);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: spacing(md);

      h3 {
        font-size: font-size(lg);
        font-weight: font-weight(semibold);
        color: color(text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: spacing(sm);
      }
    }

    .card-description {
      font-size: font-size(sm);
      color: color(text-secondary);
      margin-bottom: spacing(lg);
      line-height: 1.6;
    }

    .setting-form {
      :deep(.el-form-item) {
        margin-bottom: spacing(md);
      }

      :deep(.el-form-item__label) {
        font-weight: font-weight(medium);
        color: color(text-primary);
      }
    }

    .el-alert {
      margin-top: spacing(md);
    }
  }

  .action-bar {
    display: flex;
    justify-content: flex-end;
    gap: spacing(md);
    margin-top: spacing(xl);

    :deep(.el-button) {
      padding: spacing(md) spacing(xl);
      font-weight: font-weight(semibold);
      border-radius: radius(md);
      transition: all transition(base) easing(smooth);

      &:hover {
        transform: translateY(-2px);
      }
    }
  }
}
</style>
