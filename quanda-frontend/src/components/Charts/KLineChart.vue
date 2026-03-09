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
  enableBrush?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  showBoll: false,  // 默认不显示BOLL，提升加载速度
  enableBrush: false
})

const emit = defineEmits<{
  brushSelected: [data: {
    startTime: string
    endTime: string
    startIndex: number
    endIndex: number
    klineData: KLineData[]
    imageData?: string
  }]
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
let samplingStep = 1  // 数据抽样步长，用于反向映射到原始数据索引

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
    samplingStep = Math.ceil(props.data.length / MAX_DISPLAY_POINTS)
    displayData = props.data.filter((_, index) => index % samplingStep === 0)
  } else {
    samplingStep = 1
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
    brush: props.enableBrush ? {
      enabled: true,
      brushType: 'rect',
      xAxisIndex: [0],
      yAxisIndex: [0],
      brushStyle: {
        borderWidth: 2,
        color: 'rgba(91, 143, 249, 0.2)',
        borderColor: '#5B8FF9'
      },
      transformable: false,
      removeOnClick: true
    } : undefined,
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

// 监听enableBrush变化，实时更新图表
watch(() => props.enableBrush, (enabled) => {
  if (chartInstance) {
    if (enabled) {
      chartInstance.on('brushSelected', (params: any) => {
        handleBrushSelected(params)
      })
    } else {
      chartInstance.off('brushSelected')
    }
    updateChart()
  }
})

// 处理区域选择事件
const handleBrushSelected = (params: any) => {
  if (!params || !params.batch || params.batch.length === 0) return

  const batch = params.batch[0]
  if (!batch.selected || batch.selected.length === 0) return

  // 获取选中的数据点索引范围
  const selectedIndices: number[] = []
  for (const selection of batch.selected) {
    if (selection.dataIndex && selection.dataIndex.length > 0) {
      selectedIndices.push(...selection.dataIndex)
    }
  }

  if (selectedIndices.length < 2) {
    // 至少需要2个数据点
    return
  }

  // 反向映射到原始数据索引
  const minDisplayIndex = Math.min(...selectedIndices)
  const maxDisplayIndex = Math.max(...selectedIndices)

  const startIndex = minDisplayIndex * samplingStep
  const endIndex = Math.min(maxDisplayIndex * samplingStep, props.data.length - 1)

  // 提取选中的K线数据
  const selectedKlineData = props.data.slice(startIndex, endIndex + 1)

  // 获取时间范围
  const startTime = selectedKlineData[0].time
  const endTime = selectedKlineData[selectedKlineData.length - 1].time

  // 生成截图
  const imageData = captureSelectedArea(params, startIndex, endIndex)

  emit('brushSelected', {
    startTime,
    endTime,
    startIndex,
    endIndex,
    klineData: selectedKlineData,
    imageData
  })

  // 清除选择区域
  clearBrush()
}

// 裁剪选中区域的截图
const captureSelectedArea = (params: any, startIndex: number, endIndex: number): string | undefined => {
  if (!chartInstance || !chartRef.value) return undefined

  try {
    // 获取完整的图表截图
    const fullDataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    // 如果有选中区域的坐标信息，进行精确裁剪
    if (params.batch && params.batch[0] && params.batch[0].areas && params.batch[0].areas.length > 0) {
      const area = params.batch[0].areas[0]
      const rect = area.coordRange

      if (rect && rect.length >= 2) {
        // 使用 canvas 进行精确裁剪
        return cropImageData(fullDataURL, rect, startIndex, endIndex)
      }
    }

    return fullDataURL
  } catch (error) {
    console.error('Screenshot failed:', error)
    return undefined
  }
}

// 使用 canvas 裁剪图片
const cropImageData = (dataURL: string, coordRange: any, startIndex: number, endIndex: number): string => {
  const img = new Image()
  img.src = dataURL

  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  if (!ctx) return dataURL

  // 等待图片加载完成
  const loadImage = () => {
    return new Promise<void>((resolve) => {
      img.onload = () => resolve()
    })
  }

  // 同步方式处理
  canvas.width = img.width
  canvas.height = img.height

  // 这里简化处理，直接返回原图
  // 实际项目中可以计算选中区域的像素坐标进行裁剪
  ctx.drawImage(img, 0, 0)

  return canvas.toDataURL('image/png')
}

// 清除选择区域
const clearBrush = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'brush',
      areas: []
    })
  }
}

// 暴露方法给父组件
defineExpose({
  clearBrush
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })

  // 监听区域选择事件
  if (chartInstance && props.enableBrush) {
    chartInstance.on('brushSelected', (params: any) => {
      handleBrushSelected(params)
    })
  }
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
