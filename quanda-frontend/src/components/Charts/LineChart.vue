<template>
  <div ref="chartRef" class="line-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface DataPoint {
  time: string
  value: number
}

interface Props {
  data: DataPoint[]
  height?: string
  options?: {
    color?: string
    smooth?: boolean
    areaStyle?: boolean
    showSymbol?: boolean
  }
}

const props = withDefaults(defineProps<Props>(), {
  height: '300px',
  options: () => ({
    color: '#0066ff',
    smooth: true,
    areaStyle: true,
    showSymbol: false
  })
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data.length) return
  
  const times = props.data.map(item => item.time)
  const values = props.data.map(item => item.value)
  
  const option: any = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#d9d9d9'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#e8e8e8',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        type: 'line',
        data: values,
        smooth: props.options?.smooth !== false,
        showSymbol: props.options?.showSymbol || false,
        lineStyle: {
          color: props.options?.color || '#0066ff',
          width: 2
        },
        itemStyle: {
          color: props.options?.color || '#0066ff'
        },
        areaStyle: props.options?.areaStyle !== false ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: props.options?.color 
                ? `${props.options.color}40` 
                : 'rgba(0, 102, 255, 0.25)'
            },
            {
              offset: 1,
              color: props.options?.color 
                ? `${props.options.color}00` 
                : 'rgba(0, 102, 255, 0)'
            }
          ])
        } : undefined
      }
    ]
  }
  
  chartInstance.setOption(option)
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.options, () => {
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
.line-chart {
  width: 100%;
  height: v-bind(height);
}
</style>
