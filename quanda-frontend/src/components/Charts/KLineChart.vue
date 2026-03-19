<template>
  <div class="kline-chart-wrapper">
    <div ref="chartRef" class="kline-chart"></div>
    <!-- 确认/取消按钮 -->
    <div v-if="showConfirmButtons" class="brush-confirm-buttons" :style="confirmButtonsStyle">
      <button class="confirm-btn" @click="handleConfirm" title="确认截取">
        ✓
      </button>
      <button class="cancel-btn" @click="handleCancel" title="取消截取">
        ✕
      </button>
    </div>
  </div>
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
  highlightRange?: {
    startTime: string
    endTime: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  showBoll: false,  // 默认不显示BOLL，提升加载速度
  enableBrush: false,
  highlightRange: undefined
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
  brushEnd: [data: {
    startTime: string
    endTime: string
    startIndex: number
    endIndex: number
    klineData: KLineData[]
  }]
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
let samplingStep = 1  // 数据抽样步长，用于反向映射到原始数据索引

// 确认按钮相关状态
const showConfirmButtons = ref(false)
const confirmButtonsStyle = ref({})
const pendingBrushArea = ref<any>(null)

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
      upper: Array.from({ length: data.length }, () => null),
      middle: Array.from({ length: data.length }, () => null),
      lower: Array.from({ length: data.length }, () => null)
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

const updateChart = (preserveZoom = false) => {
  if (!chartInstance || !props.data.length) return

  // 保存当前的缩放状态
  let savedZoomState: { start: number; end: number } | null = null
  if (preserveZoom && chartInstance) {
    const currentOption = chartInstance.getOption() as any
    if (currentOption?.dataZoom?.[0]) {
      savedZoomState = {
        start: currentOption.dataZoom[0].start,
        end: currentOption.dataZoom[0].end
      }
    }
  }

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
  
  // 计算高亮区间的索引范围
  let highlightStartIndex = -1
  let highlightEndIndex = -1
  if (props.highlightRange) {
    highlightStartIndex = dates.findIndex(time => time >= props.highlightRange!.startTime)
    highlightEndIndex = dates.findIndex(time => time >= props.highlightRange!.endTime)
    
    // 如果找不到结束时间，使用最后一个索引
    if (highlightEndIndex === -1) {
      highlightEndIndex = dates.length - 1
    }
    // 如果开始时间在结束时间之后，交换它们
    if (highlightStartIndex > highlightEndIndex) {
      [highlightStartIndex, highlightEndIndex] = [highlightEndIndex, highlightStartIndex]
    }
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
    // 完全禁用 toolbox
    toolbox: {
      show: false
    },
    // 添加视觉映射，用于高亮显示截取区间
    visualMap: props.highlightRange && highlightStartIndex >= 0 && highlightEndIndex >= 0 ? [
      {
        show: false,
        seriesIndex: 0, // 应用到K线系列
        dimension: 0,
        pieces: [
          {
            gte: 0,
            lt: highlightStartIndex,
            color: 'rgba(0, 0, 0, 0.3)' // 区间外的K线变暗
          },
          {
            gte: highlightStartIndex,
            lte: highlightEndIndex,
            color: '' // 区间内的K线保持原色
          },
          {
            gt: highlightEndIndex,
            lte: dates.length,
            color: 'rgba(0, 0, 0, 0.3)' // 区间外的K线变暗
          }
        ]
      }
    ] : undefined,
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
        max: 'dataMax',
        axisPointer: {
          label: {
            formatter: (params: any) => {
              const index = params.value
              // 在高亮区间内显示特殊标记
              if (props.highlightRange && highlightStartIndex >= 0 && highlightEndIndex >= 0 &&
                  index >= highlightStartIndex && index <= highlightEndIndex) {
                return `📍 ${dates[index]}`
              }
              return dates[index]
            }
          }
        }
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
        // 如果保持缩放状态，使用保存的值；否则使用默认值
        start: savedZoomState?.start ?? (props.highlightRange ? 0 : 70),
        end: savedZoomState?.end ?? 100,
        disabled: props.enableBrush  // 启用截取时禁用内部缩放，避免冲突
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '96%',
        // 如果保持缩放状态，使用保存的值；否则使用默认值
        start: savedZoomState?.start ?? (props.highlightRange ? 0 : 70),
        end: savedZoomState?.end ?? 100,
        height: 15
      }
    ],
    // 只在启用截取模式时才配置 brush（仅横向选择，无工具栏）
    ...(props.enableBrush ? {
      brush: {
        id: 'kline-brush',
        toolbox: [],  // 不显示工具栏
        xAxisIndex: [0],
        brushType: 'lineX',  // 固定为横向选择
        brushMode: 'single',
        transformable: false,
        removeOnClick: false,
        z: 100,
        brushStyle: {
          borderWidth: 2,
          color: 'rgba(91, 143, 249, 0.2)',
          borderColor: '#5B8FF9'
        },
        throttleType: 'debounce',
        throttleDelay: 100,
        inBrush: {
          opacity: 1
        },
        outOfBrush: {
          opacity: 0.3
        }
      }
    } : {}),
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
        // 高亮区间时禁用large模式，以便visualMap生效
        large: !props.highlightRange,
        largeThreshold: 1000,
        // 添加标记线显示截取区间
        markArea: props.highlightRange && highlightStartIndex >= 0 && highlightEndIndex >= 0 ? {
          silent: true,
          itemStyle: {
            color: 'rgba(91, 143, 249, 0.15)',
            borderColor: '#5B8FF9',
            borderWidth: 2,
            borderType: 'solid'
          },
          label: {
            show: true,
            position: 'top',
            formatter: '截取区间',
            color: '#5B8FF9',
            fontSize: 12,
            fontWeight: 'bold',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            padding: [4, 8],
            borderRadius: 4
          },
          data: [
            [
              {
                xAxis: highlightStartIndex,
                itemStyle: {
                  color: 'rgba(91, 143, 249, 0.15)'
                }
              },
              {
                xAxis: highlightEndIndex
              }
            ]
          ]
        } : undefined
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
  chartInstance.setOption(option, true)

  // 确保 brush 事件监听器正确设置
  if (props.enableBrush) {
    chartInstance.off('brushSelected')
    chartInstance.off('brushEnd')
    chartInstance.on('brushEnd', (params: any) => {
      handleBrushEnd(params)
    })
    
    // 自动激活横向选择模式
    nextTick(() => {
      if (chartInstance) {
        chartInstance.dispatchAction({
          type: 'takeGlobalCursor',
          key: 'brush',
          brushOption: {
            brushType: 'lineX',
            brushMode: 'single'
          }
        })
      }
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

// 监听showBoll变化，实时更新图表（保持缩放状态）
watch(() => props.showBoll, () => {
  updateChart(true)
})

// 监听enableBrush变化，实时更新图表
watch(() => props.enableBrush, async (enabled) => {
  if (chartInstance) {
    updateChart()
    // 在图表更新后设置事件监听
    if (enabled) {
      chartInstance.off('brushEnd')
      chartInstance.on('brushEnd', (params: any) => {
        handleBrushEnd(params)
      })
      
      // 自动激活横向选择模式
      await nextTick()
      chartInstance.dispatchAction({
        type: 'takeGlobalCursor',
        key: 'brush',
        brushOption: {
          brushType: 'lineX',
          brushMode: 'single'
        }
      })
    } else {
      chartInstance.off('brushEnd')
      // 退出截取模式时，清除brush状态
      chartInstance.dispatchAction({
        type: 'brush',
        areas: []
      })
    }
  }
})

// 处理区域选择结束事件（用户完成选择但未确认）
const handleBrushEnd = async (params: any) => {
  // 首先隐藏按钮
  showConfirmButtons.value = false
  pendingBrushArea.value = null

  if (!params || !params.areas || params.areas.length === 0) {
    return
  }

  const area = params.areas[0]

  if (!area.coordRange || area.coordRange.length < 2) {
    return
  }

  // 获取选中的数据索引范围
  let coordStart: number, coordEnd: number

  if (Array.isArray(area.coordRange[0])) {
    coordStart = (area.coordRange[0] as any[])[0]
    coordEnd = (area.coordRange[0] as any[])[1]
  } else {
    coordStart = (area.coordRange as any[])[0]
    coordEnd = (area.coordRange as any[])[1]
  }

  const minCoord = Math.min(coordStart, coordEnd)
  const maxCoord = Math.max(coordStart, coordEnd)

  // 将坐标转换为显示数据的索引
  const minDisplayIndex = Math.max(0, Math.floor(minCoord))
  const maxDisplayIndex = Math.min(Math.ceil(maxCoord), props.data.length / samplingStep - 1)

  // 反向映射到原始数据索引
  const startIndex = minDisplayIndex * samplingStep
  const endIndex = Math.min((maxDisplayIndex + 1) * samplingStep - 1, props.data.length - 1)

  // 验证索引范围
  if (endIndex <= startIndex || startIndex < 0 || endIndex >= props.data.length) {
    return
  }

  // 提取选中的K线数据
  const selectedKlineData = props.data.slice(startIndex, endIndex + 1)

  if (selectedKlineData.length === 0) {
    return
  }

  // 所有验证通过，保存当前选择区域并显示按钮
  pendingBrushArea.value = area

  // 计算按钮位置
  if (chartInstance && chartRef.value) {
    const containerWidth = chartRef.value.clientWidth
    const containerHeight = chartRef.value.clientHeight

    const xEnd = chartInstance.convertToPixel({ xAxisIndex: 0 }, maxCoord)

    // 直接使用图表高度的70%（K线图表区域）作为Y轴位置
    const buttonY = containerHeight * 0.7 - 40

    // 确保按钮不超出容器右边界（按钮宽度约80px）
    const maxButtonX = containerWidth - 90
    const buttonX = Math.min(xEnd + 10, maxButtonX)

    // 确保Y坐标不为负数
    const finalButtonY = Math.max(10, buttonY)

    if (typeof buttonX === 'number' && typeof finalButtonY === 'number') {
      confirmButtonsStyle.value = {
        left: `${buttonX}px`,
        top: `${finalButtonY}px`
      }
      showConfirmButtons.value = true
    }
  }

  // 获取时间范围
  const startTime = selectedKlineData[0].time
  const endTime = selectedKlineData[selectedKlineData.length - 1].time

  // 发送 brushEnd 事件
  emit('brushEnd', {
    startTime,
    endTime,
    startIndex,
    endIndex,
    klineData: selectedKlineData
  })
}

// 确认截取
const handleConfirm = async () => {
  showConfirmButtons.value = false
  
  if (!pendingBrushArea.value) {
    return
  }

  await confirmBrushSelection()
}

// 取消截取
const handleCancel = () => {
  showConfirmButtons.value = false
  pendingBrushArea.value = null
  clearBrush()
}

// 确认选择并生成截图
const confirmBrushSelection = async () => {
  if (!chartInstance) {
    return
  }

  // 使用保存的 pendingBrushArea 而不是从 getOption 获取
  if (!pendingBrushArea.value) {
    return
  }

  const area = pendingBrushArea.value
  let coordRange = area.coordRange

  if (!coordRange || coordRange.length < 2) {
    return
  }

  // 处理 coordRange 可能是 [[x1, x2]] 或 [x1, x2] 格式
  let coordStart: number, coordEnd: number

  if (Array.isArray(coordRange[0])) {
    coordStart = (coordRange[0] as any[])[0]
    coordEnd = (coordRange[0] as any[])[1]
  } else {
    coordStart = (coordRange as any[])[0]
    coordEnd = (coordRange as any[])[1]
  }

  // 获取选中的数据索引范围
  const minCoord = Math.min(coordStart, coordEnd)
  const maxCoord = Math.max(coordStart, coordEnd)
  
  // 将坐标转换为显示数据的索引
  const minDisplayIndex = Math.max(0, Math.floor(minCoord))
  const maxDisplayIndex = Math.min(Math.ceil(maxCoord), props.data.length / samplingStep - 1)

  const startIndex = minDisplayIndex * samplingStep
  const endIndex = Math.min((maxDisplayIndex + 1) * samplingStep - 1, props.data.length - 1)

  if (endIndex <= startIndex || startIndex < 0 || endIndex >= props.data.length) {
    return
  }

  const selectedKlineData = props.data.slice(startIndex, endIndex + 1)
  
  if (selectedKlineData.length === 0) {
    return
  }

  const startTime = selectedKlineData[0].time
  const endTime = selectedKlineData[selectedKlineData.length - 1].time

  // 生成截图
  const imageData = await captureSelectedArea({ areas: [area] })

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
const captureSelectedArea = async (params: any): Promise<string | undefined> => {
  if (!chartInstance || !chartRef.value) return undefined

  try {
    // 获取完整的图表截图
    const fullDataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    // 获取选中区域的坐标信息
    if (params.areas && params.areas.length > 0) {
      const area = params.areas[0]
      let coordRange = area.coordRange

      if (coordRange && coordRange.length >= 2) {
        // 处理 coordRange 可能是 [[x1, x2]] 或 [x1, x2] 格式
        let coordStart: number, coordEnd: number

        if (Array.isArray(coordRange[0])) {
          coordStart = (coordRange[0] as any[])[0]
          coordEnd = (coordRange[0] as any[])[1]
        } else {
          coordStart = (coordRange as any[])[0]
          coordEnd = (coordRange as any[])[1]
        }

        // 将数据索引转换为像素坐标
        const xStart = chartInstance.convertToPixel({ xAxisIndex: 0 }, coordStart)
        const xEnd = chartInstance.convertToPixel({ xAxisIndex: 0 }, coordEnd)

        if (typeof xStart === 'number' && typeof xEnd === 'number') {
          // 获取图表容器的尺寸信息
          const containerHeight = chartRef.value.clientHeight

          // 使用 canvas 进行精确裁剪
          const croppedData = await cropImageData(
            fullDataURL,
            Math.min(xStart, xEnd),
            Math.max(xStart, xEnd),
            containerHeight
          )
          return croppedData
        }
      }
    }

    return fullDataURL
  } catch (error) {
    console.error('[KLineChart] Screenshot failed:', error)
    return undefined
  }
}

// 使用 canvas 裁剪图片
const cropImageData = (dataURL: string, xStart: number, xEnd: number, containerHeight: number): Promise<string> => {
  return new Promise((resolve) => {
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
        
        // 裁剪高度为图表高度的70%（K线图表区域）
        const height = Math.floor(containerHeight * 0.7 * pixelRatio)
        const top = Math.floor(containerHeight * 0.12 * pixelRatio)

        // 验证裁剪参数
        if (width <= 0 || height <= 0 || left < 0 || top < 0 || left >= img.width || top >= img.height) {
          resolve(dataURL)
          return
        }

        // 设置canvas大小为裁剪区域大小
        canvas.width = width
        canvas.height = height

        // 从原图中裁剪出选中区域
        ctx.drawImage(
          img,
          left, top, width, height,
          0, 0, width, height
        )

        const croppedDataURL = canvas.toDataURL('image/png')
        resolve(croppedDataURL)
      } catch (error) {
        console.error('[KLineChart] Crop error:', error)
        resolve(dataURL)
      }
    }

    img.onerror = (error) => {
      console.error('[KLineChart] Image load error:', error)
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
  showConfirmButtons.value = false
  pendingBrushArea.value = null
}

// 暴露方法给父组件
defineExpose({
  clearBrush,
  confirmBrushSelection
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

<style lang="scss">
// 全局隐藏 ECharts brush 工具栏（不使用 scoped）
.kline-chart-wrapper {
  .echarts-brush-btn,
  div[class*="echarts"][class*="brush"],
  div[_echarts_instance_] > div > div[style*="position: absolute"][style*="cursor"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }
}
</style>

<style lang="scss" scoped>
.kline-chart-wrapper {
  position: relative;
  width: 100%;
  height: v-bind(height);
}

.kline-chart {
  width: 100%;
  height: 100%;
}

.brush-confirm-buttons {
  position: absolute;
  display: flex;
  gap: 8px;
  z-index: 9999;
  pointer-events: auto;
  animation: buttonFadeIn 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.1);

  @keyframes buttonFadeIn {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .confirm-btn,
  .cancel-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

    &:hover {
      transform: scale(1.1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    &:active {
      transform: scale(0.95);
    }
  }

  .confirm-btn {
    background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
    color: white;

    &:hover {
      background: linear-gradient(135deg, #73D13D 0%, #95DE64 100%);
    }
  }

  .cancel-btn {
    background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
    color: white;

    &:hover {
      background: linear-gradient(135deg, #FF7875 0%, #FFA39E 100%);
    }
  }
}
</style>
