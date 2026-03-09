<template>
  <div class="futures-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <FutureSelector @change="handleFutureChange" />
        <DateRangePicker @change="handleDateChange" />
        
        <el-button-group>
          <el-button 
            v-for="period in quickPeriods" 
            :key="period.value"
            :type="frequence === period.value ? 'primary' : 'default'"
            @click="handlePeriodChange(period.value)"
          >
            {{ period.label }}
          </el-button>
        </el-button-group>
        
        <el-popover placement="bottom" :width="300" trigger="click">
          <template #reference>
            <el-button>
              <el-icon><Setting /></el-icon>
              自定义周期
            </el-button>
          </template>
          <div class="custom-period">
            <el-form :model="customPeriodForm" label-width="80px" size="small">
              <el-form-item label="周期类型">
                <el-select v-model="customPeriodForm.type" style="width: 100%;">
                  <el-option label="分钟" value="min" />
                  <el-option label="小时" value="hour" />
                  <el-option label="日" value="day" />
                  <el-option label="周" value="week" />
                  <el-option label="月" value="month" />
                </el-select>
              </el-form-item>
              <el-form-item label="周期数值" v-if="customPeriodForm.type !== 'day'">
                <el-input-number 
                  v-model="customPeriodForm.value" 
                  :min="1" 
                  :max="customPeriodForm.type === 'min' ? 60 : 24"
                  style="width: 100%;"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="applyCustomPeriod" size="small">
                  应用
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-popover>
        
        <el-button type="primary" @click="fetchData" :loading="loading" :disabled="loading">
          <el-icon><Refresh /></el-icon>
          {{ loading ? '加载中...' : '刷新' }}
        </el-button>
        
        <el-checkbox v-model="showBoll">显示BOLL</el-checkbox>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="18">
        <div class="card">
          <div class="chart-header">
            <h3>K线图 - {{ currentPeriodLabel }}</h3>
          </div>

          <!-- 加载提示 -->
          <div v-if="loading" class="loading-overlay">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在加载行情，请稍等。。</span>
          </div>

          <!-- K线图 -->
          <KLineChart v-else :data="klineData" :showBoll="showBoll" height="500px" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card">
          <h3>实时行情</h3>
          <div class="realtime-info" v-if="realtimeData">
            <div class="info-item">
              <span class="label">最新价:</span>
              <span class="value" :class="realtimeData.change >= 0 ? 'up' : 'down'">
                {{ realtimeData.price }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">涨跌幅:</span>
              <span class="value" :class="realtimeData.changePercent >= 0 ? 'up' : 'down'">
                {{ realtimeData.changePercent }}%
              </span>
            </div>
            <div class="info-item">
              <span class="label">开盘价:</span>
              <span class="value">{{ realtimeData.open }}</span>
            </div>
            <div class="info-item">
              <span class="label">最高价:</span>
              <span class="value up">{{ realtimeData.high }}</span>
            </div>
            <div class="info-item">
              <span class="label">最低价:</span>
              <span class="value down">{{ realtimeData.low }}</span>
            </div>
            <div class="info-item">
              <span class="label">成交量:</span>
              <span class="value">{{ realtimeData.volume }}</span>
            </div>
          </div>
        </div>

        <div class="card" style="margin-top: 20px;">
          <h3>技术指标</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="MA5">{{ indicators.ma5 }}</el-descriptions-item>
            <el-descriptions-item label="MA10">{{ indicators.ma10 }}</el-descriptions-item>
            <el-descriptions-item label="MA20">{{ indicators.ma20 }}</el-descriptions-item>
            <el-descriptions-item label="MACD">{{ indicators.macd }}</el-descriptions-item>
            <el-descriptions-item label="KDJ">{{ indicators.kdj }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { Refresh, Setting, Loading } from '@element-plus/icons-vue'
import FutureSelector from '@/components/Market/FutureSelector.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'
import KLineChart from '@/components/Charts/KLineChart.vue'
import type { KLineData, FutureData } from '@/types/market'

const marketStore = useMarketStore()

const loading = ref(true)  // 初始即为加载状态
const isInitialLoad = ref(true)  // 标记是否是首次加载
let fetchDataTimer: ReturnType<typeof setTimeout> | null = null  // 防抖定时器
const currentFuture = ref('')
const startDate = ref('')
const endDate = ref('')
const frequence = ref('day')
const showBoll = ref(false)  // 默认不显示BOLL，提升加载速度
const klineData = ref<KLineData[]>([])
const realtimeData = ref<any>(null)
const indicators = ref({
  ma5: '-',
  ma10: '-',
  ma20: '-',
  macd: '-',
  kdj: '-'
})

// 快捷周期选项
const quickPeriods = [
  { label: '1分', value: '1min' },
  { label: '5分', value: '5min' },
  { label: '15分', value: '15min' },
  { label: '30分', value: '30min' },
  { label: '60分', value: '60min' },
  { label: '日线', value: 'day' }
]

// 自定义周期表单
const customPeriodForm = ref({
  type: 'min',
  value: 1
})

// 当前周期标签
const currentPeriodLabel = computed(() => {
  const period = quickPeriods.find(p => p.value === frequence.value)
  return period ? period.label : frequence.value
})

const handleFutureChange = (code: string) => {
  currentFuture.value = code
  // watch 会自动触发加载
}

const handleDateChange = (start: string, end: string) => {
  startDate.value = start
  endDate.value = end
  // watch 会自动触发加载
}

const handlePeriodChange = (period: string) => {
  frequence.value = period
  // 周期改变立即重新加载
  if (currentFuture.value && startDate.value && endDate.value) {
    // 取消防抖，直接加载
    if (fetchDataTimer) {
      clearTimeout(fetchDataTimer)
      fetchDataTimer = null
    }
    fetchData()
  }
}

const applyCustomPeriod = () => {
  const { type, value } = customPeriodForm.value
  if (type === 'day') {
    frequence.value = 'day'
  } else if (type === 'week') {
    frequence.value = 'week'
  } else if (type === 'month') {
    frequence.value = 'month'
  } else if (type === 'hour') {
    frequence.value = `${value * 60}min`
  } else {
    frequence.value = `${value}min`
  }
  // 周期改变立即重新加载
  if (currentFuture.value && startDate.value && endDate.value) {
    // 取消防抖，直接加载
    if (fetchDataTimer) {
      clearTimeout(fetchDataTimer)
      fetchDataTimer = null
    }
    fetchData()
  }
}

const fetchData = async () => {
  if (!currentFuture.value || !startDate.value || !endDate.value) return

  // 清除之前的定时器
  if (fetchDataTimer) {
    clearTimeout(fetchDataTimer)
  }

  loading.value = true

  try {
    // 根据周期类型调用不同的 API
    const data: FutureData[] = await marketStore.fetchFutureData(
      currentFuture.value,
      startDate.value,
      endDate.value,
      frequence.value
    )

    // 转换数据格式
    klineData.value = data.map((item: FutureData) => ({
      time: item.date || item.datetime,
      open: item.open,
      close: item.close,
      high: item.high,
      low: item.low,
      volume: item.volume
    }))

    // 计算技术指标
    if (klineData.value.length > 0) {
      const closes = klineData.value.map((d: KLineData) => d.close)
      if (closes.length >= 5) {
        indicators.value.ma5 = (closes.slice(-5).reduce((a: number, b: number) => a + b, 0) / 5).toFixed(2)
      }
      if (closes.length >= 10) {
        indicators.value.ma10 = (closes.slice(-10).reduce((a: number, b: number) => a + b, 0) / 10).toFixed(2)
      }
      if (closes.length >= 20) {
        indicators.value.ma20 = (closes.slice(-20).reduce((a: number, b: number) => a + b, 0) / 20).toFixed(2)
      }
    }

    const realtime = await marketStore.fetchRealtimeData(currentFuture.value)
    realtimeData.value = realtime
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
    isInitialLoad.value = false
  }
}

// 防抖版本的 fetchData
const debouncedFetchData = () => {
  if (fetchDataTimer) {
    clearTimeout(fetchDataTimer)
  }
  fetchDataTimer = setTimeout(() => {
    fetchData()
  }, 100)  // 100ms 防抖
}

// 监听数据变化，自动加载
watch([currentFuture, startDate, endDate], () => {
  // 当所有必要的数据都准备好时，自动加载
  if (currentFuture.value && startDate.value && endDate.value) {
    debouncedFetchData()
  }
}, { immediate: true })

// 组件挂载时开始初始化
onMounted(async () => {
  // 确保期货列表开始加载（FutureSelector 已经在做了，这里只是确保）
  if (marketStore.futureList.length === 0) {
    marketStore.fetchFutureList()
  }
})
</script>

<style lang="scss" scoped>
.futures-page {
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }

  .loading-overlay {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 500px;
    color: #5B8FF9;
    font-size: 16px;

    .el-icon {
      font-size: 32px;
      margin-bottom: 12px;
    }
  }

  .custom-period {
    padding: 10px 0;
  }

  .realtime-info {
    .info-item {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .label {
        color: #595959;
        font-size: 14px;
      }

      .value {
        font-size: 16px;
        font-weight: 600;

        &.up {
          color: #FF7A7E;
        }

        &.down {
          color: #73D13D;
        }
      }
    }
  }
}
</style>
