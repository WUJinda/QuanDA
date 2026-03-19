<template>
  <div class="backtest-detail-page">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-row :gutter="20" v-if="backtest">
      <el-col :span="18">
        <div class="card">
          <h2>{{ getTaskName(backtest) }}</h2>
          <el-descriptions :column="3" border style="margin-top: 20px;">
            <el-descriptions-item label="策略文件">
              {{ backtest.strategy_path }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(backtest.status)">
                {{ getStatusLabel(backtest.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ backtest.create_time }}
            </el-descriptions-item>
            <el-descriptions-item label="回测周期">
              {{ backtest.start_date }} ~ {{ backtest.end_date }}
            </el-descriptions-item>
            <el-descriptions-item label="初始资金">
              {{ backtest.init_cash?.toLocaleString() }} 元
            </el-descriptions-item>
            <el-descriptions-item label="K线周期">
              {{ getFrequenceLabel(backtest.frequence) }}
            </el-descriptions-item>
            <el-descriptions-item label="回测标的">
              {{ backtest.code || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result">
          <h3>收益曲线</h3>
          <LineChart
            :data="profitCurveData"
            height="350px"
            :options="{ color: '#5B8FF9' }"
          />
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result">
          <h3>回撤曲线</h3>
          <LineChart
            :data="drawdownCurveData"
            height="300px"
            :options="{ color: '#FF4D4F' }"
          />
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result && result.trade_history">
          <h3>交易记录 (共 {{ result.trade_history.length }} 笔)</h3>
          <el-table :data="result.trade_history" stripe max-height="400">
            <el-table-column prop="trade_time" label="时间" width="180" />
            <el-table-column prop="code" label="合约" width="120" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'BUY' ? 'danger' : 'success'" size="small">
                  {{ row.direction === 'BUY' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="offset" label="开平" width="100">
              <template #default="{ row }">
                {{ getOffsetLabel(row.offset) }}
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="120" />
            <el-table-column prop="volume" label="数量" width="100" />
            <el-table-column prop="commission" label="手续费" width="100" />
          </el-table>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="card">
          <h3>回测结果</h3>
          <div class="metrics" v-if="result && result.metrics">
            <div class="metric-item highlight">
              <span class="label">总收益率</span>
              <span class="value" :class="result.metrics.profit >= 0 ? 'up' : 'down'">
                {{ result.metrics.profit >= 0 ? '+' : '' }}{{ result.metrics.profit }}%
              </span>
            </div>
            <div class="metric-item">
              <span class="label">年化收益率</span>
              <span class="value" :class="result.metrics.annual_return >= 0 ? 'up' : 'down'">
                {{ result.metrics.annual_return >= 0 ? '+' : '' }}{{ result.metrics.annual_return }}%
              </span>
            </div>
            <div class="metric-item">
              <span class="label">夏普比率</span>
              <span class="value">{{ result.metrics.sharpe_ratio }}</span>
            </div>
            <div class="metric-item">
              <span class="label">最大回撤</span>
              <span class="value down">{{ result.metrics.max_drawdown }}%</span>
            </div>
            <div class="metric-item">
              <span class="label">胜率</span>
              <span class="value">{{ result.metrics.win_rate }}%</span>
            </div>
            <div class="metric-item">
              <span class="label">盈亏比</span>
              <span class="value">{{ result.metrics.profit_loss_ratio }}</span>
            </div>
            <div class="metric-item">
              <span class="label">年化波动率</span>
              <span class="value">{{ result.metrics.volatility }}%</span>
            </div>
            <div class="metric-item">
              <span class="label">交易次数</span>
              <span class="value">{{ result.metrics.trade_count }}</span>
            </div>
            <div class="metric-item">
              <span class="label">每笔平均利润</span>
              <span class="value">{{ result.metrics.avg_profit_per_trade }}</span>
            </div>
            <div class="metric-item">
              <span class="label">最大连续盈利</span>
              <span class="value up">{{ result.metrics.max_consecutive_wins }}次</span>
            </div>
            <div class="metric-item">
              <span class="label">最大连续亏损</span>
              <span class="value down">{{ result.metrics.max_consecutive_losses }}次</span>
            </div>
          </div>
          <div v-else class="no-result">
            <el-empty description="暂无回测结果" />
          </div>
        </div>

        <div class="card" style="margin-top: 20px;">
          <h3>操作</h3>
          <el-button type="primary" style="width: 100%;" @click="exportReport" :disabled="!result">
            导出报告
          </el-button>
          <el-button style="width: 100%; margin-top: 10px;" @click="rerun" :disabled="backtest.status === 'running'">
            重新运行
          </el-button>
        </div>
      </el-col>
    </el-row>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { backtestApi } from '@/api/backtest'
import LineChart from '@/components/Charts/LineChart.vue'
import type { BacktestTask, BacktestResult } from '@/types/backtest'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const backtest = ref<BacktestTask | null>(null)
const result = ref<BacktestResult | null>(null)

const profitCurveData = computed(() => {
  if (!result.value?.account_history) return []
  return result.value.account_history.map(item => ({
    time: item.datetime.split(' ')[0],
    value: item.balance
  }))
})

const drawdownCurveData = computed(() => {
  if (!result.value?.account_history) return []

  // 计算回撤
  const history = result.value.account_history
  let peak = history[0]?.balance || 0

  return history.map(item => {
    peak = Math.max(peak, item.balance)
    const drawdown = peak > 0 ? ((peak - item.balance) / peak) * 100 : 0
    return {
      time: item.datetime.split(' ')[0],
      value: -drawdown // 显示为负值
    }
  })
})

const fetchBacktestDetail = async () => {
  loading.value = true
  try {
    const backtestId = route.params.id as string
    backtest.value = await backtestApi.getDetail(backtestId)

    if (backtest.value && backtest.value.status === 'completed') {
      result.value = await backtestApi.getResult(backtestId)
    }
  } catch (error) {
    console.error('获取回测详情失败:', error)
    ElMessage.error('获取回测详情失败')
  } finally {
    loading.value = false
  }
}

const getTaskName = (task: BacktestTask) => {
  const name = task.strategy_path.split('/').pop() || task.strategy_path
  return name.replace('.py', '') + ' 回测'
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

const getFrequenceLabel = (frequence: string) => {
  const map: Record<string, string> = {
    '1min': '1分钟',
    '5min': '5分钟',
    '15min': '15分钟',
    '30min': '30分钟',
    'day': '日线'
  }
  return map[frequence] || frequence
}

const getOffsetLabel = (offset: string) => {
  const map: Record<string, string> = {
    'OPEN': '开仓',
    'CLOSE': '平仓',
    'CLOSETODAY': '平今'
  }
  return map[offset] || offset
}

const exportReport = () => {
  if (!result.value) return

  // 生成报告
  const report = {
    backtest_id: result.value.backtest_id,
    strategy_path: result.value.strategy_path,
    date_range: `${result.value.start_date} ~ ${result.value.end_date}`,
    init_cash: result.value.init_cash,
    metrics: result.value.metrics,
    trades: result.value.trade_history
  }

  // 下载为 JSON 文件
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `backtest_report_${result.value.backtest_id}.json`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已导出')
}

const rerun = async () => {
  if (!backtest.value) return

  try {
    await backtestApi.run(backtest.value.backtest_id)
    ElMessage.success('回测任务已重新启动')
    router.push('/backtest')
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

onMounted(() => {
  fetchBacktestDetail()
})
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.backtest-detail-page {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
  }

  .card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 600;
  }

  h3 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .metrics {
    .metric-item {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      &.highlight {
        padding: 16px;
        background: linear-gradient(135deg, #5B8FF9 0%, #FF8C42 100%);
        border-radius: 8px;
        margin-bottom: 16px;
        border: none;

        .label,
        .value {
          color: #fff;
        }

        .value {
          font-size: 24px;
        }
      }

      .label {
        color: #8c8c8c;
        font-size: 14px;
      }

      .value {
        font-size: 16px;
        font-weight: 600;
      }
    }
  }

  .up {
    color: #FF7A7E;
  }

  .down {
    color: #73D13D;
  }

  .no-result {
    padding: 40px 0;
  }

  .loading-container {
    padding: 40px;
  }
}
</style>
