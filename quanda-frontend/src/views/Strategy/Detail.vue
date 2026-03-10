<template>
  <div class="strategy-detail-page">
    <div class="page-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-row :gutter="20" v-if="strategy">
      <el-col :span="16">
        <div class="card">
          <div class="strategy-header">
            <div>
              <h2>{{ strategy.name }}</h2>
              <p class="description">{{ strategy.description }}</p>
            </div>
            <div class="actions">
              <el-button 
                v-if="strategy.status === 'stopped'" 
                type="primary" 
                @click="startStrategy"
              >
                启动策略
              </el-button>
              <el-button 
                v-else 
                type="danger" 
                @click="stopStrategy"
              >
                停止策略
              </el-button>
              <el-button @click="showBacktestDialog = true">
                运行回测
              </el-button>
            </div>
          </div>

          <el-descriptions :column="2" border style="margin-top: 20px;">
            <el-descriptions-item label="策略类型">
              {{ getStrategyTypeLabel(strategy.type) }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="strategy.status === 'running' ? 'success' : 'info'">
                {{ strategy.status === 'running' ? '运行中' : '已停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ strategy.createTime }}
            </el-descriptions-item>
            <el-descriptions-item label="累计收益">
              <span :class="strategy.profit >= 0 ? 'up' : 'down'">
                {{ strategy.profit }}%
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="策略文件" :span="2">
              {{ strategy.filePath || '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="code-section" v-if="strategy.code">
            <h3>策略代码</h3>
            <pre class="code-block"><code>{{ strategy.code }}</code></pre>
          </div>
        </div>

        <div class="card" style="margin-top: 20px;">
          <h3>回测历史</h3>
          <el-table :data="backtestHistory" stripe>
            <el-table-column prop="name" label="回测名称" width="200" />
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="profit" label="收益率" width="120">
              <template #default="{ row }">
                <span :class="row.profit >= 0 ? 'up' : 'down'">
                  {{ row.profit }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="sharpeRatio" label="夏普比率" width="120" />
            <el-table-column prop="maxDrawdown" label="最大回撤" width="120">
              <template #default="{ row }">
                <span class="down">{{ row.maxDrawdown }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewBacktestResult(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="card">
          <h3>性能指标</h3>
          <div class="metrics">
            <div class="metric-item">
              <span class="label">总收益率</span>
              <span class="value up">+15.6%</span>
            </div>
            <div class="metric-item">
              <span class="label">年化收益率</span>
              <span class="value up">+28.3%</span>
            </div>
            <div class="metric-item">
              <span class="label">夏普比率</span>
              <span class="value">1.85</span>
            </div>
            <div class="metric-item">
              <span class="label">最大回撤</span>
              <span class="value down">-8.2%</span>
            </div>
            <div class="metric-item">
              <span class="label">胜率</span>
              <span class="value">62.5%</span>
            </div>
            <div class="metric-item">
              <span class="label">交易次数</span>
              <span class="value">156</span>
            </div>
          </div>
        </div>

        <div class="card" style="margin-top: 20px;">
          <h3>收益曲线</h3>
          <LineChart :data="profitCurve" height="250px" />
        </div>
      </el-col>
    </el-row>

    <!-- 回测对话框 -->
    <el-dialog 
      v-model="showBacktestDialog" 
      title="运行回测" 
      width="600px"
    >
      <el-form :model="backtestForm" label-width="100px">
        <el-form-item label="回测名称">
          <el-input v-model="backtestForm.name" placeholder="请输入回测名称" />
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
        <el-form-item label="手续费率">
          <el-input-number 
            v-model="backtestForm.commission" 
            :min="0" 
            :max="1" 
            :step="0.0001" 
            :precision="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBacktestDialog = false">取消</el-button>
        <el-button type="primary" @click="runBacktest">运行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api/strategy'
import { backtestApi } from '@/api/backtest'
import LineChart from '@/components/Charts/LineChart.vue'
import type { Strategy, BacktestSummary } from '@/types/strategy'

const route = useRoute()
const router = useRouter()

const strategy = ref<Strategy | null>(null)
const backtestHistory = ref<BacktestSummary[]>([])
const showBacktestDialog = ref(false)
const profitCurve = ref([])

const backtestForm = ref({
  name: '',
  dateRange: [],
  initCash: 100000,
  commission: 0.0003
})

const fetchStrategyDetail = async () => {
  try {
    const id = Number(route.params.id)
    strategy.value = await strategyApi.getDetail(id)
    backtestHistory.value = await strategyApi.getBacktestHistory(id)
  } catch (error) {
    ElMessage.error('获取策略详情失败')
  }
}

const startStrategy = async () => {
  try {
    await strategyApi.start(strategy.value!.id)
    ElMessage.success('策略已启动')
    fetchStrategyDetail()
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

const stopStrategy = async () => {
  try {
    await strategyApi.stop(strategy.value!.id)
    ElMessage.success('策略已停止')
    fetchStrategyDetail()
  } catch (error) {
    ElMessage.error('停止失败')
  }
}

const runBacktest = async () => {
  if (!backtestForm.value.name || !backtestForm.value.dateRange.length) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    await backtestApi.create({
      ...backtestForm.value,
      strategyId: strategy.value!.id,
      strategyPath: strategy.value!.filePath
    })
    ElMessage.success('回测任务已创建')
    showBacktestDialog.value = false
    fetchStrategyDetail()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const viewBacktestResult = (row: BacktestSummary) => {
  router.push(`/backtest/${row.id}`)
}

const getStrategyTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    trend: '趋势策略',
    mean_reversion: '均值回归',
    arbitrage: '套利策略',
    hft: '高频交易'
  }
  return map[type] || type
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    '已完成': 'success',
    '运行中': 'warning',
    '失败': 'danger',
    '待运行': 'info'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchStrategyDetail()
})
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.strategy-detail-page {
  padding: spacing(lg);

  .page-header {
    margin-bottom: spacing(lg);
  }

  .strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: spacing(lg);

    h2 {
      margin: 0 0 spacing(sm) 0;
      font-size: font-size(xxxl);
      font-weight: font-weight(bold);
    }

    .description {
      color: color(text-secondary);
      margin: 0;
    }

    .actions {
      display: flex;
      gap: spacing(sm);
    }
  }

  .code-section {
    margin-top: spacing(xl);

    h3 {
      margin-bottom: spacing(md);
    }

    .code-block {
      background: color(bg-secondary);
      padding: spacing(md);
      border-radius: radius(md);
      overflow-x: auto;
      font-family: $font-family-code;
      font-size: font-size(sm);
      line-height: 1.6;
    }
  }

  .metrics {
    .metric-item {
      display: flex;
      justify-content: space-between;
      padding: spacing(md) 0;
      border-bottom: 1px solid color(border-light);

      &:last-child {
        border-bottom: none;
      }

      .label {
        color: color(text-secondary);
        font-size: font-size(base);
      }

      .value {
        font-size: font-size(lg);
        font-weight: font-weight(semibold);
      }
    }
  }
}
</style>
