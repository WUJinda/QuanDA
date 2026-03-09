<template>
  <div ref="chartRef" class="kline-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { KLineData } from '@/types/market'

interface Props {
  data: KLineData[]
  height?: string
  showBoll?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  showBoll: true
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 计算布林带指标
const calculateBOLL = (data: number[], period = 20, multiplier = 2) => {
  const result = {
    upper: [] as (number | null)[],
    middle: [] as (number | null)[],
    lower: [] as (number | null)[]
  }
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      // 前面不足20个数据点时，用null填充（不显示）
      result.upper.push(null)
      result.middle.push(null)
      result.lower.push(null)
      continue
    }
    
    const slice = data.slice(i - period + 1, i + 1)
    const sum = slice.reduce((a, b) => a + b, 0)
    const mean = sum / period
    
    const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / period
    const std = Math.sqrt(variance)
    
    result.middle.push(mean)
    result.upper.push(mean + multiplier * std)
    result.lower.push(mean - multiplier * std)
  }
  
  return result
}

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 清理旧的 chartInstance，防止重新渲染时出错
const cleanup = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

const updateChart = () => {
  if (!chartInstance || !props.data.length) return
  
  const dates = props.data.map((item: KLineData) => item.time)
  const values = props.data.map((item: KLineData) => [item.open, item.close, item.low, item.high])
  const volumes = props.data.map((item: KLineData) => item.volume)
  const closePrices = props.data.map((item: KLineData) => item.close)
  
  // 计算 BOLL 指标
  const boll = calculateBOLL(closePrices)
  
  // 构建图例数据
  const legendData = ['K线', '成交量']
  if (props.showBoll) {
    legendData.push('BOLL上轨', 'BOLL中轨', 'BOLL下轨')
  }
  
  const option: any = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: legendData,
      top: 0
    },
    grid: [
      {
        left: '5%',
        right: '5%',
        top: '12%',
        height: '70%'
      },
      {
        left: '5%',
        right: '5%',
        top: '84%',
        height: '10%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
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
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '96%',
        start: 0,
        end: 100,
        height: 15
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: values,
        barWidth: '60%',
        barMaxWidth: 8,
        itemStyle: {
          color: '#FF7A7E',
          color0: '#73D13D',
          borderColor: '#FF7A7E',
          borderColor0: '#73D13D'
        }
      },
      ...(props.showBoll ? [
        {
          name: 'BOLL上轨',
          type: 'line' as const,
          data: boll.upper,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1.5,
            color: '#FF7A7E'
          },
          showSymbol: false,
          connectNulls: false
        },
        {
          name: 'BOLL中轨',
          type: 'line' as const,
          data: boll.middle,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1.5,
            color: '#5B8FF9'
          },
          showSymbol: false,
          connectNulls: false
        },
        {
          name: 'BOLL下轨',
          type: 'line' as const,
          data: boll.lower,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1.5,
            color: '#73D13D'
          },
          showSymbol: false,
          connectNulls: false
        }
      ] : []),
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        barWidth: '60%',
        barMaxWidth: 8,
        itemStyle: {
          color: (params: any) => {
            const dataIndex = params.dataIndex
            return values[dataIndex][1] > values[dataIndex][0] ? '#FF7A7E' : '#73D13D'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

watch(() => props.data, async (newData) => {
  if (newData && newData.length > 0) {
    await nextTick()
    updateChart()
  }
}, { deep: true, immediate: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})

onUnmounted(() => {
  cleanup()
})
</script>

<style lang="scss" scoped>
.kline-chart {
  width: 100%;
  height: v-bind(height);
}
</style>
