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
  showBoll: false  // 默认不显示BOLL，提升加载速度
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 优化的布林带计算（使用滑动窗口，避免重复计算）
const calculateBOLL = (data: number[], period = 20, multiplier = 2) => {
  const result = {
    upper: [] as (number | null)[],
    middle: [] as (number | null)[],
    lower: [] as (number | null)[]
  }
  
  if (data.length < period) {
    // 数据不足，全部返回null
    return {
      upper: new Array(data.length).fill(null),
      middle: new Array(data.length).fill(null),
      lower: new Array(data.length).fill(null)
    }
  }
  
  // 使用滑动窗口优化计算
  let sum = 0
  let sumSq = 0
  
  // 初始化第一个窗口
  for (let i = 0; i < period; i++) {
    sum += data[i]
    sumSq += data[i] * data[i]
  }
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.upper.push(null)
      result.middle.push(null)
      result.lower.push(null)
      continue
    }
    
    // 计算均值和标准差
    const mean = sum / period
    const variance = (sumSq / period) - (mean * mean)
    const std = Math.sqrt(Math.max(0, variance))
    
    result.middle.push(mean)
    result.upper.push(mean + multiplier * std)
    result.lower.push(mean - multiplier * std)
    
    // 滑动窗口：移除最旧的值，添加新值
    if (i < data.length - 1) {
      const oldVal = data[i - period + 1]
      const newVal = data[i + 1]
      sum = sum - oldVal + newVal
      sumSq = sumSq - oldVal * oldVal + newVal * newVal
    }
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
  
  // 数据抽样优化：当数据量过大时，进行抽样显示
  let displayData = props.data
  const MAX_DISPLAY_POINTS = 5000
  
  if (props.data.length > MAX_DISPLAY_POINTS) {
    // 使用等间隔抽样
    const step = Math.ceil(props.data.length / MAX_DISPLAY_POINTS)
    displayData = props.data.filter((_, index) => index % step === 0)
  }
  
  const dates = displayData.map((item: KLineData) => item.time)
  const values = displayData.map((item: KLineData) => [item.open, item.close, item.low, item.high])
  const volumes = displayData.map((item: KLineData) => item.volume)
  const closePrices = displayData.map((item: KLineData) => item.close)
  
  // 只在用户勾选时才计算 BOLL 指标，避免不必要的计算
  const boll = props.showBoll ? calculateBOLL(closePrices) : null
  
  // 构建图例数据
  const legendData = ['K线', '成交量']
  if (props.showBoll) {
    legendData.push('BOLL上轨', 'BOLL中轨', 'BOLL下轨')
  }
  
  const option: any = {
    animation: false, // 关闭动画，提升性能
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
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '96%',
        start: 70,
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
        },
        large: true, // 开启大数据量优化
        largeThreshold: 1000 // 数据量大于1000时启用优化
      },
      ...(props.showBoll && boll ? [
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
          connectNulls: false,
          sampling: 'lttb' // 使用LTTB算法进行数据抽样
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
          connectNulls: false,
          sampling: 'lttb'
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
          connectNulls: false,
          sampling: 'lttb'
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
        },
        large: true,
        largeThreshold: 1000
      }
    ]
  }

  chartInstance.setOption(option, true) // 使用notMerge模式，提升性能
}

// 监听数据变化
watch(() => props.data, async (newData) => {
  if (newData && newData.length > 0) {
    await nextTick()
    updateChart()
  }
}, { deep: true, immediate: true })

// 监听showBoll变化，实时更新图表
watch(() => props.showBoll, () => {
  updateChart()
})

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
