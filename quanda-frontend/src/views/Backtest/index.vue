<template>
  <div class="backtest-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showStrategyDialog = true">
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
          <el-table :data="backtestList" stripe>
            <el-table-column prop="name" label="任务名称" width="200" />
            <el-table-column prop="strategy" label="策略" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="startDate" label="开始日期" width="120" />
            <el-table-column prop="endDate" label="结束日期" width="120" />
            <el-table-column prop="profit" label="收益率" width="100">
              <template #default="{ row }">
                <span :class="row.profit >= 0 ? 'up' : 'down'">
                  {{ row.profit }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewResult(row)">
                  查看结果
                </el-button>
                <el-button link type="primary" @click="runBacktest(row)">
                  运行
                </el-button>
                <el-button link type="danger" @click="deleteBacktest(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card">
          <h3>实时输出</h3>
          <div class="console-output" ref="consoleRef">
            <div v-for="(log, index) in consoleLogs" :key="index" class="log-line">
              {{ log }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showStrategyDialog" title="新建回测任务" width="600px">
      <el-form :model="backtestForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="backtestForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="策略文件">
          <el-input v-model="backtestForm.strategyPath" placeholder="策略文件路径">
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
          />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="backtestForm.initCash" :min="10000" :step="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStrategyDialog = false">取消</el-button>
        <el-button type="primary" @click="createBacktest">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { backtestApi } from '@/api/backtest'

const searchKeyword = ref('')
const showStrategyDialog = ref(false)
const consoleLogs = ref<string[]>([])
const consoleRef = ref<HTMLElement>()

const backtestList = ref([
  {
    id: 1,
    name: '双均线策略回测',
    strategy: 'MA_Strategy',
    status: '已完成',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    profit: 15.6
  },
  {
    id: 2,
    name: 'MACD策略回测',
    strategy: 'MACD_Strategy',
    status: '运行中',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    profit: 0
  }
])

const backtestForm = ref({
  name: '',
  strategyPath: '',
  dateRange: [],
  initCash: 100000
})

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    '已完成': 'success',
    '运行中': 'warning',
    '失败': 'danger',
    '待运行': 'info'
  }
  return typeMap[status] || 'info'
}

const viewResult = (row: any) => {
  ElMessage.info(`查看回测结果: ${row.name}`)
}

const runBacktest = async (row: any) => {
  try {
    consoleLogs.value = []
    consoleLogs.value.push(`[${new Date().toLocaleTimeString()}] 开始运行回测: ${row.name}`)
    
    const command = `python ${row.strategy}.py`
    await backtestApi.runCommand(command)
    
    consoleLogs.value.push(`[${new Date().toLocaleTimeString()}] 回测任务已提交`)
    ElMessage.success('回测任务已启动')
  } catch (error) {
    consoleLogs.value.push(`[${new Date().toLocaleTimeString()}] 错误: ${error}`)
    ElMessage.error('启动失败')
  }
}

const deleteBacktest = (row: any) => {
  ElMessage.warning(`删除回测: ${row.name}`)
}

const selectFile = () => {
  ElMessage.info('请选择策略文件')
}

const createBacktest = () => {
  if (!backtestForm.value.name || !backtestForm.value.strategyPath) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  ElMessage.success('回测任务创建成功')
  showStrategyDialog.value = false
}
</script>

<style lang="scss" scoped>
.backtest-page {
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
    font-weight: 600;
    color: #262626;
  }

  .console-output {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 8px;
    height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);

    .log-line {
      margin-bottom: 4px;
      line-height: 1.5;
    }
  }

  .up {
    color: #FF7A7E;
  }

  .down {
    color: #73D13D;
  }
}
</style>
