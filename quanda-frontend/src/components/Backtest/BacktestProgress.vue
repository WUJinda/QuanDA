<template>
  <div class="backtest-progress">
    <div class="progress-header">
      <span class="status-badge" :class="statusClass">{{ statusText }}</span>
      <span class="progress-percent">{{ progress }}%</span>
    </div>
    <el-progress
      :percentage="progress"
      :status="progressStatus"
      :stroke-width="8"
      :show-text="false"
    />
    <div class="progress-message">{{ message }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'idle' | 'running' | 'completed' | 'error'
  progress: number
  message: string
}

const props = withDefaults(defineProps<Props>(), {
  status: 'idle',
  progress: 0,
  message: ''
})

const statusClass = computed(() => {
  return {
    'status-idle': props.status === 'idle',
    'status-running': props.status === 'running',
    'status-completed': props.status === 'completed',
    'status-error': props.status === 'error'
  }
})

const statusText = computed(() => {
  const statusMap = {
    idle: '等待',
    running: '运行中',
    completed: '完成',
    error: '错误'
  }
  return statusMap[props.status] || props.status
})

const progressStatus = computed(() => {
  if (props.status === 'completed') return 'success'
  if (props.status === 'error') return 'exception'
  return undefined
})
</script>

<style lang="scss" scoped>
.backtest-progress {
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .status-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;

      &.status-idle {
        background: #f0f0f0;
        color: #909399;
      }

      &.status-running {
        background: #e6f7ff;
        color: #1890ff;
      }

      &.status-completed {
        background: #f6ffed;
        color: #52c41a;
      }

      &.status-error {
        background: #fff2f0;
        color: #ff4d4f;
      }
    }

    .progress-percent {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
    }
  }

  .progress-message {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
}
</style>
