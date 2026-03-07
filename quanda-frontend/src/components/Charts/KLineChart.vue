<template>
  <div ref="chartRef" class="kline-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
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
        left: '10%',
        right: '10%',
        top: '12%',
        height: '58%'
      },
      {
        left: '10%',
        right: '10%',
        top: '75%',
        height: '15%'
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
        start: 80,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 80,
        end: 100
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
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
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
            color: '#f5222d'
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
            color: '#1890ff'
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
            color: '#52c41a'
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
            return values[dataIndex][1] > values[dataIndex][0] ? '#ef232a' : '#14b143'
          }
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<style lang="scss" scoped>
.kline-chart {
  width: 100%;
  height: v-bind(height);
}
</style>
