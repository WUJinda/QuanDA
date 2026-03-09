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
      id: 'kline-brush',
      geoIndex: [],
      xAxisIndex: [0],
      yAxisIndex: [0],
      brushType: 'rect',
      brushMode: 'single',
      transformable: true,
      removeOnClick: true,
      z: 100,
      brushStyle: {
        borderWidth: 2,
        color: 'rgba(91, 143, 249, 0.2)',
        borderColor: '#5B8FF9'
      },
      throttleType: 'debounce',
      throttleDelay: 100
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

  // 根据是否有 brush 配置来决定是否使用 notMerge
  if (props.enableBrush) {
    chartInstance.setOption(option, true)
  } else {
    chartInstance.setOption(option, true)
  }

  // 确保 brush 事件监听器正确设置
  if (props.enableBrush) {
    chartInstance.off('brushSelected')
    chartInstance.on('brushSelected', (params: any) => {
      handleBrushSelected(params)
    })
  }
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
  console.log('[KLineChart] enableBrush changed:', enabled)
  if (chartInstance) {
    updateChart()
    // 在图表更新后设置事件监听
    if (enabled) {
      chartInstance.off('brushSelected') // 先移除旧的监听器
      chartInstance.on('brushSelected', (params: any) => {
        console.log('[KLineChart] brushSelected event:', params)
        handleBrushSelected(params)
      })
      console.log('[KLineChart] Brush event listener attached')
    } else {
      chartInstance.off('brushSelected')
      console.log('[KLineChart] Brush event listener removed')
    }
  }
})

// 处理区域选择事件
const handleBrushSelected = async (params: any) => {
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

  // 生成截图（异步）
  const imageData = await captureSelectedArea(params, startIndex, endIndex)

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
const captureSelectedArea = async (params: any, startIndex: number, endIndex: number): Promise<string | undefined> => {
  if (!chartInstance || !chartRef.value) return undefined

  try {
    // 获取完整的图表截图
    const fullDataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    // 获取选中区域的坐标信息
    if (params.batch && params.batch[0] && params.batch[0].areas && params.batch[0].areas.length > 0) {
      const area = params.batch[0].areas[0]
      const coordRange = area.coordRange

      if (coordRange && coordRange.length >= 2) {
        // 获取图表的grid信息
        const gridModel = chartInstance.getModel().getComponent('grid', 0)
        const gridRect = gridModel.coordinateSystem.getRect()

        // 将数据索引转换为像素坐标
        const xStart = chartInstance.convertToPixel({ xAxisIndex: 0 }, coordRange[0])
        const xEnd = chartInstance.convertToPixel({ xAxisIndex: 0 }, coordRange[coordRange.length - 1])

        if (typeof xStart === 'number' && typeof xEnd === 'number') {
          // 使用 canvas 进行精确裁剪
          return await cropImageData(fullDataURL, xStart, xEnd, gridRect)
        }
      }
    }

    return fullDataURL
  } catch (error) {
    console.error('Screenshot failed:', error)
    return undefined
  }
}

// 使用 canvas 裁剪图片
const cropImageData = (dataURL: string, xStart: number, xEnd: number, gridRect: any): Promise<string> => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        if (!ctx) {
          resolve(dataURL)
          return
        }

        // 计算裁剪区域（考虑pixelRatio=2）
        const pixelRatio = 2
        const left = Math.floor(xStart * pixelRatio)
        const right = Math.ceil(xEnd * pixelRatio)
        const width = right - left
        const height = Math.floor(gridRect.height * pixelRatio)
        const top = Math.floor(gridRect.y * pixelRatio)

        // 设置canvas大小为裁剪区域大小
        canvas.width = width
        canvas.height = height

        // 从原图中裁剪出选中区域
        ctx.drawImage(
          img,
          left, top, width, height,  // 源区域
          0, 0, width, height         // 目标区域
        )

        resolve(canvas.toDataURL('image/png'))
      } catch (error) {
        console.error('Crop error:', error)
        resolve(dataURL)
      }
    }

    img.onerror = () => {
      resolve(dataURL)
    }

    img.src = dataURL
  })
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
