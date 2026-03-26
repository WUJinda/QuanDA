<template>
  <div class="backtest-chart">
    <!-- 账户信息面板 -->
    <div class="account-panel" v-if="account">
      <div class="account-item">
        <span class="label">总资产</span>
        <span class="value">{{ formatNumber(account.balance) }}</span>
      </div>
      <div class="account-item">
        <span class="label">可用资金</span>
        <span class="value">{{ formatNumber(account.available) }}</span>
      </div>
      <div class="account-item">
        <span class="label">浮动盈亏</span>
        <span class="value" :class="account.float_profit >= 0 ? 'profit' : 'loss'">
          {{ account.float_profit >= 0 ? '+' : '' }}{{ formatNumber(account.float_profit) }}
        </span>
      </div>
      <div class="account-item">
        <span class="label">平仓盈亏</span>
        <span class="value" :class="account.close_profit >= 0 ? 'profit' : 'loss'">
          {{ account.close_profit >= 0 ? '+' : '' }}{{ formatNumber(account.close_profit) }}
        </span>
      </div>
    </div>

    <!-- K线图表 -->
    <div ref="chartRef" class="chart-container"></div>

    <!-- 无数据提示 -->
    <div v-if="klines.length === 0" class="empty-chart">
      <el-icon :size="48"><TrendCharts /></el-icon>
      <p>等待K线数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { TrendCharts } from '@element-plus/icons-vue'
import type { BacktestKLine, BacktestAccount, BacktestSignal } from '@/types/backtest-visualization'

interface Props {
  klines: BacktestKLine[]
  account: BacktestAccount | null
  signals: BacktestSignal[]
}

const props = withDefaults(defineProps<Props>(), {
  klines: () => [],
  account: null,
  signals: () => []
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 格式化数字
const formatNumber = (num: number) => {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || props.klines.length === 0) return

  const times = props.klines.map(k => k.time)
  const ohlc = props.klines.map(k => [k.open, k.close, k.low, k.high])
  const volumes = props.klines.map(k => k.volume || 0)

  // 处理买卖信号
  const buySignals: any[] = []
  const sellSignals: any[] = []

  props.signals.forEach(signal => {
    const index = times.indexOf(signal.time)
    if (index !== -1) {
      const signalData = {
        name: signal.direction === 'buy' ? '买入' : '卖出',
        coord: [signal.time, signal.price],
        symbol: signal.direction === 'buy' ? 'arrow' : 'arrow',
        symbolRotate: signal.direction === 'buy' ? 0 : 180,
        itemStyle: {
          color: signal.direction === 'buy' ? '#A865F3' : '#FFEA5A'
        }
      }
      if (signal.direction === 'buy') {
        buySignals.push(signalData)
      } else {
        sellSignals.push(signalData)
      }
    }
  })

  const option: any = {
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: { data: ['K线', '成交量'], top: 0 },
    grid: [
      { left: '8%', right: '3%', top: '10%', height: '55%' },
      { left: '8%', right: '3%', top: '72%', height: '18%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: times,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: times,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      { scale: true, splitArea: { show: true } },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 80, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', top: '92%', start: 80, end: 100, height: 20 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#FF7A7E',
          color0: '#73D13D',
          borderColor: '#FF7A7E',
          borderColor0: '#73D13D'
        },
        markPoint: {
          data: [...buySignals, ...sellSignals],
          symbolSize: 15
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: (params: any) => {
            const dataIndex = params.dataIndex
            if (dataIndex >= 0 && dataIndex < ohlc.length) {
              return ohlc[dataIndex][1] >= ohlc[dataIndex][0] ? '#FF7A7E' : '#73D13D'
            }
            return '#909399'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option, true)
}

// 监听数据变化
watch(() => props.klines, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.signals, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

// 窗口大小变化
const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.backtest-chart {
  height: 100%;
  display: flex;
  flex-direction: column;

  .account-panel {
    display: flex;
    gap: 24px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-bottom: 12px;

    .account-item {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .label {
        font-size: 12px;
        color: #909399;
      }

      .value {
        font-size: 16px;
        font-weight: 600;
        color: #303133;

        &.profit {
          color: #f5222d;
        }

        &.loss {
          color: #52c41a;
        }
      }
    }
  }

  .chart-container {
    flex: 1;
    min-height: 400px;
  }

  .empty-chart {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;

    .el-icon {
      margin-bottom: 12px;
      opacity: 0.5;
    }

    p {
      margin: 0;
      font-size: 14px;
    }
  }
}
</style>
