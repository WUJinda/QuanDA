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
          <h2>{{ backtest.name }}</h2>
          <el-descriptions :column="3" border style="margin-top: 20px;">
            <el-descriptions-item label="策略名称">
              {{ backtest.strategy }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(backtest.status)">
                {{ backtest.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ backtest.createTime }}
            </el-descriptions-item>
            <el-descriptions-item label="回测周期">
              {{ backtest.startDate }} ~ {{ backtest.endDate }}
            </el-descriptions-item>
            <el-descriptions-item label="初始资金">
              {{ backtest.config?.initCash || 0 }} 元
            </el-descriptions-item>
            <el-descriptions-item label="手续费率">
              {{ (backtest.config?.commission || 0) * 100 }}%
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result">
          <h3>收益曲线</h3>
          <LineChart 
            :data="profitCurveData" 
            height="350px" 
            :options="{ color: '#0066ff' }"
          />
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result">
          <h3>回撤曲线</h3>
          <LineChart 
            :data="drawdownCurveData" 
            height="300px" 
            :options="{ color: '#f44336' }"
          />
        </div>

        <div class="card" style="margin-top: 20px;" v-if="result">
          <h3>交易记录</h3>
          <el-table :data="result.tradeList" stripe max-height="400">
            <el-table-column prop="time" label="时间" width="180" />
            <el-table-column prop="code" label="合约" width="120" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'buy' ? 'danger' : 'success'" size="small">
                  {{ row.direction === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="offset" label="开平" width="80">
              <template #default="{ row }">
                {{ row.offset === 'open' ? '开仓' : '平仓' }}
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="120" />
            <el-table-column prop="volume" label="数量" width="100" />
            <el-table-column prop="profit" label="盈亏" width="120">
              <template #default="{ row }">
                <span v-if="row.profit" :class="row.profit >= 0 ? 'up' : 'down'">
                  {{ row.profit >= 0 ? '+' : '' }}{{ row.profit }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="card">
          <h3>回测结果</h3>
          <div class="metrics" v-if="result">
            <div class="metric-item highlight">
              <span class="label">总收益率</span>
              <span class="value" :class="result.totalReturn >= 0 ? 'up' : 'down'">
                {{ result.totalReturn >= 0 ? '+' : '' }}{{ result.totalReturn }}%
              </span>
            </div>
            <div class="metric-item">
              <span class="label">年化收益率</span>
              <span class="value" :class="result.annualReturn >= 0 ? 'up' : 'down'">
                {{ result.annualReturn >= 0 ? '+' : '' }}{{ result.annualReturn }}%
              </span>
            </div>
            <div class="metric-item">
              <span class="label">夏普比率</span>
              <span class="value">{{ result.sharpeRatio }}</span>
            </div>
            <div class="metric-item">
              <span class="label">最大回撤</span>
              <span class="value down">{{ result.maxDrawdown }}%</span>
            </div>
            <div class="metric-item">
              <span class="label">胜率</span>
              <span class="value">{{ result.winRate }}%</span>
            </div>
            <div class="metric-item">
              <span class="label">交易次数</span>
              <span class="value">{{ result.trades }}</span>
            </div>
          </div>
          <div v-else class="no-result">
            <el-empty description="暂无回测结果" />
          </div>
        </div>

        <div class="card" style="margin-top: 20px;">
          <h3>操作</h3>
          <el-button type="primary" style="width: 100%;" @click="exportReport">
            导出报告
          </el-button>
          <el-button style="width: 100%; margin-top: 10px;" @click="rerun">
            重新运行
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { backtestApi } from '@/api/backtest'
import LineChart from '@/components/Charts/LineChart.vue'
import type { BacktestTask, BacktestResult } from '@/types/backtest'

const route = useRoute()

const backtest = ref<BacktestTask | null>(null)
const result = ref<BacktestResult | null>(null)

const profitCurveData = computed(() => {
  if (!result.value?.profitCurve) return []
  return result.value.profitCurve.map((value, index) => ({
    time: `Day ${index + 1}`,
    value
  }))
})

const drawdownCurveData = computed(() => {
  if (!result.value?.drawdownCurve) return []
  return result.value.drawdownCurve.map((value, index) => ({
    time: `Day ${index + 1}`,
    value
  }))
})

const fetchBacktestDetail = async () => {
  try {
    const id = Number(route.params.id)
    backtest.value = await backtestApi.getDetail(id)
    
    if (backtest.value && backtest.value.status === 'completed') {
      result.value = await backtestApi.getResult(id)
    }
  } catch (error) {
    ElMessage.error('获取回测详情失败')
  }
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

const exportReport = () => {
  ElMessage.info('导出功能开发中')
}

const rerun = () => {
  ElMessage.info('重新运行功能开发中')
}

onMounted(() => {
  fetchBacktestDetail()
})
</script>

<style lang="scss" scoped>
@import '@/styles/design-system.scss';

.backtest-detail-page {
  padding: spacing(lg);

  .page-header {
    margin-bottom: spacing(lg);
  }

  h2 {
    margin: 0 0 spacing(lg) 0;
    font-size: font-size(xxxl);
    font-weight: font-weight(bold);
  }

  h3 {
    margin: 0 0 spacing(md) 0;
    font-size: font-size(lg);
    font-weight: font-weight(semibold);
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

      &.highlight {
        padding: spacing(lg);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: radius(md);
        margin-bottom: spacing(md);
        border: none;

        .label,
        .value {
          color: #fff;
        }

        .value {
          font-size: font-size(xxl);
        }
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

  .no-result {
    padding: spacing(xl) 0;
  }
}
</style>
