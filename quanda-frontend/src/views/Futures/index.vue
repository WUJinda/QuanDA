<template>
  <div class="futures-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="header-text">
            <h1>期货K线</h1>
            <p class="subtitle">
              <span class="code-badge" v-if="currentFuture">{{ currentFuture }}</span>
              <span v-else>请选择合约</span>
            </p>
          </div>
        </div>
        <div class="header-actions">
          <el-button class="action-btn" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
          <el-button class="action-btn" @click="handleAddWatch">
            <el-icon><Star /></el-icon>
            添加自选
          </el-button>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar-card">
      <div class="toolbar-section">
        <div class="section-title">
          <el-icon><Filter /></el-icon>
          数据筛选
        </div>
        <div class="toolbar-controls">
          <div class="control-group">
            <label>选择合约</label>
            <FutureSelector @change="handleFutureChange" class="future-selector" />
          </div>
          
          <div class="control-group">
            <label>时间范围</label>
            <DateRangePicker @change="handleDateChange" class="date-picker" />
          </div>
        </div>
      </div>

      <div class="toolbar-section">
        <div class="section-title">
          <el-icon><Clock /></el-icon>
          周期设置
        </div>
        <div class="period-controls">
          <el-button-group class="period-group">
            <el-button 
              v-for="period in quickPeriods" 
              :key="period.value"
              :type="frequence === period.value ? 'primary' : ''"
              @click="handlePeriodChange(period.value)"
              class="period-btn"
            >
              {{ period.label }}
            </el-button>
          </el-button-group>
          
          <el-popover placement="bottom" :width="320" trigger="click">
            <template #reference>
              <el-button class="custom-btn">
                <el-icon><Setting /></el-icon>
                自定义
              </el-button>
            </template>
            <div class="custom-period-panel">
              <div class="panel-title">自定义周期</div>
              <el-form :model="customPeriodForm" label-width="80px" size="default">
                <el-form-item label="周期类型">
                  <el-select v-model="customPeriodForm.type" style="width: 100%;">
                    <el-option label="分钟" value="min" />
                    <el-option label="小时" value="hour" />
                    <el-option label="日线" value="day" />
                    <el-option label="周线" value="week" />
                    <el-option label="月线" value="month" />
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
                  <el-button type="primary" @click="applyCustomPeriod" style="width: 100%;">
                    应用设置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-popover>
        </div>
      </div>

      <div class="toolbar-actions">
        <el-checkbox v-model="showBoll" class="boll-checkbox">
          <el-icon><DataLine /></el-icon>
          显示BOLL
        </el-checkbox>
        <el-button 
          type="primary" 
          class="refresh-btn" 
          @click="fetchData" 
          :loading="loading" 
          :disabled="loading"
        >
          <el-icon><Refresh /></el-icon>
          {{ loading ? '加载中...' : '刷新数据' }}
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <el-row :gutter="24" class="content-row">
      <!-- K线图表 -->
      <el-col :span="18">
        <div class="chart-card">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div>
                <h3>K线图表</h3>
                <p class="card-subtitle">{{ currentPeriodLabel }} · 共 {{ klineData.length }} 条数据</p>
              </div>
            </div>
            <div class="chart-legend" v-if="!loading && klineData.length > 0">
              <div class="legend-item">
                <span class="legend-dot open"></span>
                <span class="legend-label">开盘</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot high"></span>
                <span class="legend-label">最高</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot low"></span>
                <span class="legend-label">最低</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot close"></span>
                <span class="legend-label">收盘</span>
              </div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-overlay">
            <div class="loading-content">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p class="loading-text">正在加载K线数据...</p>
              <p class="loading-hint">请稍候，数据加载中</p>
            </div>
          </div>

          <!-- K线图 -->
          <div v-else-if="klineData.length > 0" class="chart-container">
            <KLineChart :data="klineData" :showBoll="showBoll" height="540px" />
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <el-icon :size="64" class="empty-icon"><DataLine /></el-icon>
            <p class="empty-text">暂无数据</p>
            <p class="empty-hint">请选择合约和时间范围后刷新</p>
          </div>
        </div>
      </el-col>

      <!-- 侧边栏 -->
      <el-col :span="6">
        <!-- 实时行情卡片 -->
        <div class="info-card realtime-card">
          <div class="card-header">
            <div class="header-icon orange">
              <el-icon><Odometer /></el-icon>
            </div>
            <h3>实时行情</h3>
          </div>
          
          <div v-if="realtimeData" class="realtime-content">
            <div class="price-display" :class="realtimeData.change >= 0 ? 'up' : 'down'">
              <div class="current-price">{{ realtimeData.price }}</div>
              <div class="price-change">
                <span class="change-value">
                  {{ realtimeData.change >= 0 ? '+' : '' }}{{ realtimeData.change }}
                </span>
                <span class="change-percent">
                  {{ realtimeData.changePercent >= 0 ? '+' : '' }}{{ realtimeData.changePercent }}%
                </span>
              </div>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <span class="label">开盘</span>
                <span class="value">{{ realtimeData.open }}</span>
              </div>
              <div class="info-item">
                <span class="label">最高</span>
                <span class="value high">{{ realtimeData.high }}</span>
              </div>
              <div class="info-item">
                <span class="label">最低</span>
                <span class="value low">{{ realtimeData.low }}</span>
              </div>
              <div class="info-item">
                <span class="label">成交量</span>
                <span class="value">{{ formatVolume(realtimeData.volume) }}</span>
              </div>
            </div>
          </div>

          <div v-else class="empty-realtime">
            <el-icon :size="48"><Odometer /></el-icon>
            <p>暂无实时数据</p>
          </div>
        </div>

        <!-- 技术指标卡片 -->
        <div class="info-card indicators-card">
          <div class="card-header">
            <div class="header-icon purple">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <h3>技术指标</h3>
          </div>
          
          <div class="indicators-content">
            <div class="indicator-item" v-for="(value, key) in indicators" :key="key">
              <div class="indicator-header">
                <span class="indicator-name">{{ key.toUpperCase() }}</span>
                <el-icon class="indicator-icon"><TrendCharts /></el-icon>
              </div>
              <div class="indicator-value">{{ value }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  Setting, 
  Loading,
  TrendCharts,
  Filter,
  Clock,
  Download,
  Star,
  DataLine,
  Odometer,
  DataAnalysis
} from '@element-plus/icons-vue'
import FutureSelector from '@/components/Market/FutureSelector.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'
import KLineChart from '@/components/Charts/KLineChart.vue'
import type { KLineData, FutureData } from '@/types/market'

const marketStore = useMarketStore()

const loading = ref(true)
const isInitialLoad = ref(true)
let fetchDataTimer: ReturnType<typeof setTimeout> | null = null
const currentFuture = ref('')
const startDate = ref('')
const endDate = ref('')
const frequence = ref('day')
const showBoll = ref(false)
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
}

const handleDateChange = (start: string, end: string) => {
  startDate.value = start
  endDate.value = end
}

const handlePeriodChange = (period: string) => {
  frequence.value = period
  if (currentFuture.value && startDate.value && endDate.value) {
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
  if (currentFuture.value && startDate.value && endDate.value) {
    if (fetchDataTimer) {
      clearTimeout(fetchDataTimer)
      fetchDataTimer = null
    }
    fetchData()
  }
}

const fetchData = async () => {
  if (!currentFuture.value || !startDate.value || !endDate.value) return

  if (fetchDataTimer) {
    clearTimeout(fetchDataTimer)
  }

  loading.value = true

  try {
    const data: FutureData[] = await marketStore.fetchFutureData(
      currentFuture.value,
      startDate.value,
      endDate.value,
      frequence.value
    )

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
    ElMessage.error('数据加载失败，请重试')
  } finally {
    loading.value = false
    isInitialLoad.value = false
  }
}

const debouncedFetchData = () => {
  if (fetchDataTimer) {
    clearTimeout(fetchDataTimer)
  }
  fetchDataTimer = setTimeout(() => {
    fetchData()
  }, 100)
}

const formatVolume = (volume: number) => {
  if (!volume) return '-'
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

const handleAddWatch = () => {
  if (currentFuture.value) {
    ElMessage.success(`已添加 ${currentFuture.value} 到自选`)
  } else {
    ElMessage.warning('请先选择合约')
  }
}

watch([currentFuture, startDate, endDate], () => {
  if (currentFuture.value && startDate.value && endDate.value) {
    debouncedFetchData()
  }
}, { immediate: true })

onMounted(async () => {
  if (marketStore.futureList.length === 0) {
    marketStore.fetchFutureList()
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/design-system.scss';

.futures-page {
  padding: spacing(lg);
  background: color(bg-secondary);
  min-height: 100vh;
  animation: fadeIn 0.5s easing(smooth);

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  // ==================== 页面头部 ====================
  .page-header {
    background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
    border-radius: radius(xl);
    padding: spacing(xl);
    margin-bottom: spacing(lg);
    box-shadow: shadow(lg);
    animation: slideDown 0.6s easing(smooth);

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: spacing(lg);

        .header-icon {
          width: 64px;
          height: 64px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: radius(xl);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #FFFFFF;
          backdrop-filter: blur(10px);
          box-shadow: shadow(sm);
        }

        .header-text {
          h1 {
            font-size: font-size(huge);
            font-weight: font-weight(bold);
            color: #FFFFFF;
            margin: 0 0 spacing(xs) 0;
          }

          .subtitle {
            font-size: font-size(base);
            color: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            gap: spacing(sm);
            margin: 0;

            .code-badge {
              font-family: $font-family-code;
              background: rgba(255, 255, 255, 0.2);
              padding: 4px spacing(base);
              border-radius: radius(md);
              font-weight: font-weight(semibold);
              backdrop-filter: blur(10px);
            }
          }
        }
      }

      .header-actions {
        display: flex;
        gap: spacing(base);

        .action-btn {
          padding: spacing(md) spacing(lg);
          background: rgba(255, 255, 255, 0.2);
          color: #FFFFFF;
          border: none;
          border-radius: radius(lg);
          font-weight: font-weight(semibold);
          display: flex;
          align-items: center;
          gap: spacing(sm);
          backdrop-filter: blur(10px);
          transition: all transition(base) easing(smooth);
          box-shadow: shadow(sm);

          &:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: shadow(md);
          }
        }
      }
    }
  }

  // ==================== 工具栏卡片 ====================
  .toolbar-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    margin-bottom: spacing(lg);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    display: flex;
    gap: spacing(xl);
    flex-wrap: wrap;
    animation: slideUp 0.6s easing(smooth) 0.1s both;

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .toolbar-section {
      flex: 1;
      min-width: 300px;

      .section-title {
        display: flex;
        align-items: center;
        gap: spacing(sm);
        font-size: font-size(base);
        font-weight: font-weight(semibold);
        color: color(text-secondary);
        margin-bottom: spacing(md);
      }

      .toolbar-controls {
        display: flex;
        gap: spacing(lg);
        flex-wrap: wrap;

        .control-group {
          display: flex;
          flex-direction: column;
          gap: spacing(xs);

          label {
            font-size: font-size(sm);
            color: color(text-tertiary);
            font-weight: font-weight(medium);
          }

          .future-selector,
          .date-picker {
            :deep(.el-input__wrapper),
            :deep(.el-select) {
              border-radius: radius(md);
            }
          }
        }
      }

      .period-controls {
        display: flex;
        gap: spacing(base);
        align-items: center;

        .period-group {
          display: flex;
          gap: spacing(xs);

          .period-btn {
            border-radius: radius(md);
            font-weight: font-weight(medium);
            transition: all transition(fast) easing(smooth);

            &:hover {
              transform: translateY(-1px);
            }
          }
        }

        .custom-btn {
          border-radius: radius(md);
          font-weight: font-weight(medium);
          display: flex;
          align-items: center;
          gap: spacing(xs);
        }
      }
    }

    .toolbar-actions {
      display: flex;
      gap: spacing(base);
      align-items: flex-end;

      .boll-checkbox {
        display: flex;
        align-items: center;
        gap: spacing(xs);
        padding: spacing(md) spacing(lg);
        background: color(bg-secondary);
        border-radius: radius(md);
        font-weight: font-weight(medium);
        transition: all transition(fast) easing(smooth);

        &:hover {
          background: color(bg-hover);
        }

        :deep(.el-checkbox__label) {
          display: flex;
          align-items: center;
          gap: spacing(xs);
        }
      }

      .refresh-btn {
        padding: spacing(md) spacing(xl);
        border-radius: radius(md);
        font-weight: font-weight(semibold);
        display: flex;
        align-items: center;
        gap: spacing(sm);
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        border: none;
        transition: all transition(base) easing(smooth);
        box-shadow: shadow(sm);

        &:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: shadow(md);
        }
      }
    }
  }

  // 自定义周期面板
  .custom-period-panel {
    padding: spacing(base);

    .panel-title {
      font-size: font-size(lg);
      font-weight: font-weight(semibold);
      color: color(text-primary);
      margin-bottom: spacing(md);
      padding-bottom: spacing(sm);
      border-bottom: 2px solid color(bg-secondary);
    }
  }

  // ==================== 主内容区 ====================
  .content-row {
    animation: slideUp 0.6s easing(smooth) 0.2s both;
  }

  // K线图表卡片
  .chart-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    min-height: 640px;
    display: flex;
    flex-direction: column;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: spacing(lg);
      padding-bottom: spacing(md);
      border-bottom: 2px solid color(bg-secondary);

      .header-left {
        display: flex;
        align-items: center;
        gap: spacing(md);

        .header-icon {
          width: 48px;
          height: 48px;
          border-radius: radius(lg);
          background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
          color: #FFFFFF;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: shadow(sm);
        }

        h3 {
          font-size: font-size(lg);
          font-weight: font-weight(bold);
          color: color(text-primary);
          margin: 0;
        }

        .card-subtitle {
          font-size: font-size(sm);
          color: color(text-tertiary);
          margin: spacing(xs) 0 0 0;
        }
      }

      .chart-legend {
        display: flex;
        gap: spacing(lg);

        .legend-item {
          display: flex;
          align-items: center;
          gap: spacing(xs);

          .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;

            &.open {
              background: color(primary);
            }

            &.high {
              background: color(danger);
            }

            &.low {
              background: color(success);
            }

            &.close {
              background: color(warning);
            }
          }

          .legend-label {
            font-size: font-size(sm);
            color: color(text-secondary);
          }
        }
      }
    }

    // 加载状态
    .loading-overlay {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 540px;

      .loading-content {
        text-align: center;

        .loading-icon {
          font-size: 64px;
          color: color(primary);
          margin-bottom: spacing(md);
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .loading-text {
          font-size: font-size(lg);
          font-weight: font-weight(semibold);
          color: color(text-primary);
          margin: 0 0 spacing(xs) 0;
        }

        .loading-hint {
          font-size: font-size(sm);
          color: color(text-tertiary);
          margin: 0;
        }
      }
    }

    // 图表容器
    .chart-container {
      flex: 1;
    }

    // 空状态
    .empty-state {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 540px;

      .empty-icon {
        color: color(border-dark);
        margin-bottom: spacing(md);
      }

      .empty-text {
        font-size: font-size(lg);
        font-weight: font-weight(semibold);
        color: color(text-secondary);
        margin: 0 0 spacing(xs) 0;
      }

      .empty-hint {
        font-size: font-size(sm);
        color: color(text-tertiary);
        margin: 0;
      }
    }
  }

  // ==================== 侧边栏信息卡片 ====================
  .info-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    margin-bottom: spacing(lg);
    transition: all transition(base) easing(smooth);

    &:hover {
      box-shadow: shadow(md);
      border-color: color(primary-light);
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: spacing(md);
      margin-bottom: spacing(lg);
      padding-bottom: spacing(md);
      border-bottom: 2px solid color(bg-secondary);

      .header-icon {
        width: 48px;
        height: 48px;
        border-radius: radius(lg);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        box-shadow: shadow(sm);

        &.orange {
          background: linear-gradient(135deg, #FFA940 0%, #FFD666 100%);
        }

        &.purple {
          background: linear-gradient(135deg, #9254DE 0%, #B37FEB 100%);
        }
      }

      h3 {
        font-size: font-size(lg);
        font-weight: font-weight(bold);
        color: color(text-primary);
        margin: 0;
      }
    }
  }

  // 实时行情卡片
  .realtime-card {
    .realtime-content {
      .price-display {
        text-align: center;
        padding: spacing(lg);
        background: color(bg-secondary);
        border-radius: radius(lg);
        margin-bottom: spacing(lg);

        .current-price {
          font-size: font-size(huge);
          font-weight: font-weight(bold);
          margin-bottom: spacing(sm);
        }

        .price-change {
          display: flex;
          justify-content: center;
          gap: spacing(base);
          font-size: font-size(base);
          font-weight: font-weight(semibold);

          .change-value,
          .change-percent {
            padding: 4px spacing(base);
            border-radius: radius(md);
          }
        }

        &.up {
          .current-price,
          .change-value,
          .change-percent {
            color: color(danger);
          }

          .change-value,
          .change-percent {
            background: rgba(255, 122, 126, 0.1);
          }
        }

        &.down {
          .current-price,
          .change-value,
          .change-percent {
            color: color(success);
          }

          .change-value,
          .change-percent {
            background: rgba(115, 209, 61, 0.1);
          }
        }
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: spacing(md);

        .info-item {
          display: flex;
          flex-direction: column;
          gap: spacing(xs);
          padding: spacing(md);
          background: color(bg-secondary);
          border-radius: radius(md);
          transition: all transition(fast) easing(smooth);

          &:hover {
            background: color(bg-hover);
            transform: translateY(-2px);
          }

          .label {
            font-size: font-size(xs);
            color: color(text-tertiary);
            font-weight: font-weight(medium);
          }

          .value {
            font-size: font-size(lg);
            font-weight: font-weight(bold);
            color: color(text-primary);

            &.high {
              color: color(danger);
            }

            &.low {
              color: color(success);
            }
          }
        }
      }
    }

    .empty-realtime {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: spacing(xxl) 0;
      color: color(text-tertiary);

      .el-icon {
        margin-bottom: spacing(md);
        opacity: 0.5;
      }

      p {
        margin: 0;
        font-size: font-size(sm);
      }
    }
  }

  // 技术指标卡片
  .indicators-card {
    .indicators-content {
      display: flex;
      flex-direction: column;
      gap: spacing(base);

      .indicator-item {
        padding: spacing(md);
        background: color(bg-secondary);
        border-radius: radius(md);
        transition: all transition(fast) easing(smooth);

        &:hover {
          background: color(bg-hover);
          transform: translateX(4px);
        }

        .indicator-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: spacing(xs);

          .indicator-name {
            font-size: font-size(sm);
            font-weight: font-weight(semibold);
            color: color(text-secondary);
          }

          .indicator-icon {
            color: color(primary);
            opacity: 0.5;
          }
        }

        .indicator-value {
          font-size: font-size(xl);
          font-weight: font-weight(bold);
          color: color(text-primary);
        }
      }
    }
  }

  // ==================== 响应式 ====================
  @media (max-width: 1200px) {
    .page-header {
      .header-content {
        flex-direction: column;
        gap: spacing(lg);

        .header-actions {
          width: 100%;
          justify-content: flex-end;
        }
      }
    }

    .toolbar-card {
      flex-direction: column;

      .toolbar-section {
        min-width: 100%;
      }

      .toolbar-actions {
        width: 100%;
        justify-content: space-between;
      }
    }
  }

  @media (max-width: 768px) {
    padding: spacing(base);

    .page-header {
      .header-content {
        .header-left {
          .header-icon {
            width: 48px;
            height: 48px;
          }

          .header-text {
            h1 {
              font-size: font-size(xxl);
            }
          }
        }

        .header-actions {
          flex-direction: column;
          width: 100%;

          .action-btn {
            width: 100%;
            justify-content: center;
          }
        }
      }
    }

    .toolbar-card {
      .toolbar-section {
        .toolbar-controls {
          flex-direction: column;

          .control-group {
            width: 100%;
          }
        }

        .period-controls {
          flex-direction: column;
          align-items: stretch;

          .period-group {
            flex-wrap: wrap;
          }

          .custom-btn {
            width: 100%;
            justify-content: center;
          }
        }
      }

      .toolbar-actions {
        flex-direction: column;

        .boll-checkbox,
        .refresh-btn {
          width: 100%;
          justify-content: center;
        }
      }
    }

    .content-row {
      .info-grid {
        grid-template-columns: 1fr !important;
      }
    }
  }
}
</style>
