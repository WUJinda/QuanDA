<template>
  <div class="backtest-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建回测
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索回测任务"
          style="width: 200px;"
          clearable
          @clear="loadBacktestList"
          @keyup.enter="loadBacktestList"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <div class="card">
          <h3>回测任务列表</h3>
          <el-table :data="backtestList" stripe v-loading="loading">
            <el-table-column prop="name" label="任务名称" width="200">
              <template #default="{ row }">
                {{ getTaskName(row) }}
              </template>
            </el-table-column>
            <el-table-column prop="strategy_path" label="策略" width="180">
              <template #default="{ row }">
                {{ getStrategyName(row.strategy_path) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="150">
              <template #default="{ row }">
                <el-progress
                  v-if="row.status === 'running'"
                  :percentage="row.progress || 0"
                  :stroke-width="6"
                />
                <span v-else>{{ row.progress || 0 }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column label="收益率" width="100">
              <template #default="{ row }">
                <span v-if="row.metrics" :class="row.metrics.profit >= 0 ? 'up' : 'down'">
                  {{ row.metrics.profit }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewResult(row)" :disabled="row.status !== 'completed'">
                  查看结果
                </el-button>
                <el-button link type="primary" @click="runBacktest(row)" :disabled="row.status === 'running'">
                  运行
                </el-button>
                <el-button link type="danger" @click="deleteBacktest(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadBacktestList"
              @current-change="loadBacktestList"
            />
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card">
          <h3>实时输出</h3>
          <div class="console-output" ref="consoleRef">
            <div v-for="(log, index) in consoleLogs" :key="index" class="log-line" :class="log.type">
              <span class="time">{{ log.time }}</span>
              <span class="message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 创建回测对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建回测任务" width="600px">
      <el-form :model="backtestForm" label-width="100px">
        <el-form-item label="策略文件">
          <el-input v-model="backtestForm.strategy_path" placeholder="策略文件路径">
            <template #append>
              <el-button @click="selectFile">选择文件</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="回测周期">
          <el-date-picker
            v-model="backtestForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="backtestForm.init_cash" :min="10000" :step="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="回测标的">
          <el-input v-model="backtestForm.code" placeholder="如: rb2405" />
        </el-form-item>
        <el-form-item label="K线周期">
          <el-select v-model="backtestForm.frequence" style="width: 100%">
            <el-option label="1分钟" value="1min" />
            <el-option label="5分钟" value="5min" />
            <el-option label="15分钟" value="15min" />
            <el-option label="30分钟" value="30min" />
            <el-option label="日线" value="day" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createBacktest" :loading="creating">创建并运行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { backtestApi } from '@/api/backtest'
import { useWebSocket } from '@/composables/useWebSocket'
import type { BacktestTask, WSMessage } from '@/types/backtest'

const router = useRouter()

const loading = ref(false)
const creating = ref(false)
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const consoleLogs = ref<{ time: string; message: string; type: string }[]>([])
const consoleRef = ref<HTMLElement | null>(null)

const backtestList = ref<BacktestTask[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const backtestForm = ref({
  strategy_path: '',
  dateRange: [] as string[],
  init_cash: 100000,
  code: '',
  frequence: '1min'
})

// WebSocket 连接
let ws: WebSocket | null = null
let currentRunningId: string | null = null

const loadBacktestList = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await backtestApi.getList(skip, pageSize.value)
    backtestList.value = response.list || []
    total.value = response.total || 0
  } catch (error) {
    console.error('加载回测列表失败:', error)
    ElMessage.error('加载回测列表失败')
  } finally {
    loading.value = false
  }
}

const createBacktest = async () => {
  if (!backtestForm.value.strategy_path) {
    ElMessage.warning('请选择策略文件')
    return
  }
  if (!backtestForm.value.dateRange || backtestForm.value.dateRange.length !== 2) {
    ElMessage.warning('请选择回测周期')
    return
  }

  creating.value = true
  try {
    const config = {
      strategy_path: backtestForm.value.strategy_path,
      start_date: backtestForm.value.dateRange[0],
      end_date: backtestForm.value.dateRange[1],
      init_cash: backtestForm.value.init_cash,
      code: backtestForm.value.code,
      frequence: backtestForm.value.frequence
    }

    // 创建回测任务
    const { backtest_id } = await backtestApi.create(config)

    ElMessage.success('回测任务创建成功')
    showCreateDialog.value = false

    // 刷新列表
    await loadBacktestList()

    // 启动回测
    await startBacktest(backtest_id)

  } catch (error) {
    console.error('创建回测失败:', error)
    ElMessage.error('创建回测失败')
  } finally {
    creating.value = false
  }
}

const startBacktest = async (backtestId: string) => {
  currentRunningId = backtestId
  consoleLogs.value = []
  addLog('info', `开始运行回测: ${backtestId}`)

  // 建立 WebSocket 连接
  ws = backtestApi.createWebSocket(
    backtestId,
    handleWSMessage,
    handleWSError
  )
}

const handleWSMessage = (data: WSMessage) => {
  switch (data.type) {
    case 'started':
      addLog('info', '回测任务已启动')
      break
    case 'progress':
      addLog('info', `[${data.progress}%] ${data.message}`)
      // 更新列表中的进度
      const task = backtestList.value.find(t => t.backtest_id === currentRunningId)
      if (task) {
        task.progress = data.progress
        task.message = data.message
      }
      break
    case 'completed':
      addLog('success', '回测完成!')
      if (data.result) {
        addLog('success', `总收益率: ${data.result.metrics?.profit}%`)
        addLog('success', `夏普比率: ${data.result.metrics?.sharpe_ratio}`)
        addLog('success', `最大回撤: ${data.result.metrics?.max_drawdown}%`)
      }
      // 关闭连接并刷新列表
      closeWebSocket()
      loadBacktestList()
      break
    case 'error':
      addLog('error', `错误: ${data.message}`)
      closeWebSocket()
      loadBacktestList()
      break
    case 'status':
      if (data.data) {
        addLog('info', `状态: ${data.data.status}`)
      }
      break
  }
}

const handleWSError = (error: Event) => {
  addLog('error', 'WebSocket 连接错误')
  console.error('WebSocket error:', error)
}

const closeWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
  currentRunningId = null
}

const addLog = (type: string, message: string) => {
  const now = new Date()
  const time = now.toLocaleTimeString()
  consoleLogs.value.push({ time, message, type })

  // 滚动到底部
  nextTick(() => {
    if (consoleRef.value) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight
    }
  })
}

const runBacktest = async (row: BacktestTask) => {
  try {
    await backtestApi.run(row.backtest_id)
    startBacktest(row.backtest_id)
    ElMessage.success('回测任务已启动')
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

const viewResult = (row: BacktestTask) => {
  router.push(`/backtest/${row.backtest_id}`)
}

const deleteBacktest = async (row: BacktestTask) => {
  try {
    await ElMessageBox.confirm('确定要删除该回测任务吗？', '确认删除', {
      type: 'warning'
    })
    await backtestApi.delete(row.backtest_id)
    ElMessage.success('删除成功')
    loadBacktestList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const selectFile = () => {
  // TODO: 实现文件选择对话框
  ElMessage.info('请输入策略文件路径')
}

const getTaskName = (row: BacktestTask) => {
  const name = row.strategy_path.split('/').pop() || row.strategy_path
  return name.replace('.py', '')
}

const getStrategyName = (path: string) => {
  return path.split('/').pop()?.replace('.py', '') || path
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    completed: 'success',
    running: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    pending: '待运行'
  }
  return map[status] || status
}

onMounted(() => {
  loadBacktestList()
})

onUnmounted(() => {
  closeWebSocket()
})
</script>

<style lang="scss" scoped>
.backtest-page {
  padding: 20px;

  h3 {
    margin-bottom: 20px;
    font-size: 16px;
    font-weight: 600;
    color: #262626;
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 16px 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .console-output {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 8px;
    height: 500px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);

    .log-line {
      margin-bottom: 4px;
      line-height: 1.5;

      .time {
        color: #6a9955;
        margin-right: 8px;
      }

      &.success .message {
        color: #4ec9b0;
      }

      &.error .message {
        color: #f14c4c;
      }

      &.info .message {
        color: #d4d4d4;
      }
    }
  }

  .up {
    color: #FF7A7E;
    font-weight: 600;
  }

  .down {
    color: #73D13D;
    font-weight: 600;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
