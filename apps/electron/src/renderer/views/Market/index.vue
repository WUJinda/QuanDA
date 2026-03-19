<template>
  <div class="market-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="header-text">
            <h1>实时行情</h1>
            <p class="subtitle">
              <span class="pulse-dot"></span>
              实时更新中
              <span class="update-time">最后更新: {{ lastUpdateTime }}</span>
            </p>
          </div>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-label">上涨</span>
            <span class="stat-value up">{{ upCount }}</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-label">下跌</span>
            <span class="stat-value down">{{ downCount }}</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-label">平盘</span>
            <span class="stat-value">{{ flatCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 演示模式提示 -->
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="demo-alert"
    >
      <template #title>
        <span class="alert-title">
          <el-icon><InfoFilled /></el-icon>
          演示模式
        </span>
      </template>
      当前使用模拟数据，仅供演示使用。如需使用真实数据，请前往系统设置中配置数据源。
    </el-alert>

    <!-- 工具栏 -->
    <div class="toolbar-card">
      <div class="toolbar-section">
        <div class="section-title">
          <el-icon><Filter /></el-icon>
          筛选条件
        </div>
        <div class="toolbar-controls">
          <div class="control-group">
            <label>搜索</label>
            <el-input
              v-model="searchKeyword"
              placeholder="输入代码或名称"
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div class="control-group">
            <label>市场类型</label>
            <el-select v-model="marketType" placeholder="选择市场" class="market-select">
              <el-option label="全部市场" value="all">
                <span class="option-content">
                  <el-icon><Grid /></el-icon>
                  全部市场
                </span>
              </el-option>
              <el-option label="期货" value="future">
                <span class="option-content">
                  <el-icon><TrendCharts /></el-icon>
                  期货
                </span>
              </el-option>
              <el-option label="股票" value="stock">
                <span class="option-content">
                  <el-icon><PieChart /></el-icon>
                  股票
                </span>
              </el-option>
              <el-option label="指数" value="index">
                <span class="option-content">
                  <el-icon><DataLine /></el-icon>
                  指数
                </span>
              </el-option>
            </el-select>
          </div>

          <div class="control-group">
            <label>涨跌幅</label>
            <el-select v-model="changeFilter" placeholder="涨跌筛选" class="change-select">
              <el-option label="全部" value="all" />
              <el-option label="上涨" value="up" />
              <el-option label="下跌" value="down" />
              <el-option label="平盘" value="flat" />
            </el-select>
          </div>
        </div>
      </div>

      <div class="toolbar-actions">
        <el-button class="action-btn" @click="exportData">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="primary" class="action-btn primary" @click="refreshMarket" :loading="loading">
          <el-icon><Refresh /></el-icon>
          {{ loading ? '刷新中...' : '刷新行情' }}
        </el-button>
      </div>
    </div>

    <!-- 行情表格 -->
    <div class="market-table-card">
      <div class="table-header">
        <div class="header-left">
          <h3>
            <el-icon><List /></el-icon>
            行情列表
          </h3>
          <span class="result-count">共 {{ filteredMarketData.length }} 条结果</span>
        </div>
        <div class="view-toggle">
          <el-button-group>
            <el-button :type="viewMode === 'table' ? 'primary' : ''" @click="viewMode = 'table'">
              <el-icon><Grid /></el-icon>
              表格
            </el-button>
            <el-button :type="viewMode === 'card' ? 'primary' : ''" @click="viewMode = 'card'">
              <el-icon><Tickets /></el-icon>
              卡片
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="table-container">
        <el-table 
          :data="filteredMarketData" 
          class="modern-market-table"
          :header-cell-style="{ background: '#F5F7FA', color: '#595959', fontWeight: '600' }"
          height="600"
          @row-click="handleRowClick"
        >
          <el-table-column prop="code" label="代码" width="140" fixed>
            <template #default="{ row }">
              <div class="code-cell">
                <span class="code-badge">{{ row.code }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="name" label="名称" width="160">
            <template #default="{ row }">
              <div class="name-cell">
                <span class="name-text">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="price" label="最新价" width="120" align="right">
            <template #default="{ row }">
              <div class="price-cell" :class="row.change >= 0 ? 'up' : 'down'">
                <span class="price-value">{{ row.price.toFixed(2) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="change" label="涨跌" width="110" align="right">
            <template #default="{ row }">
              <div class="change-cell" :class="row.change >= 0 ? 'up' : 'down'">
                <el-icon v-if="row.change > 0"><CaretTop /></el-icon>
                <el-icon v-else-if="row.change < 0"><CaretBottom /></el-icon>
                <span>{{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(2) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="changePercent" label="涨跌幅" width="120" align="right">
            <template #default="{ row }">
              <el-tag 
                :type="row.changePercent >= 0 ? 'danger' : 'success'" 
                effect="light"
                class="percent-tag"
              >
                {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="open" label="今开" width="110" align="right">
            <template #default="{ row }">
              <span class="data-value">{{ row.open.toFixed(2) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="high" label="最高" width="110" align="right">
            <template #default="{ row }">
              <span class="data-value high">{{ row.high.toFixed(2) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="low" label="最低" width="110" align="right">
            <template #default="{ row }">
              <span class="data-value low">{{ row.low.toFixed(2) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="volume" label="成交量" width="130" align="right">
            <template #default="{ row }">
              <span class="volume-value">{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="amount" label="成交额" width="140" align="right">
            <template #default="{ row }">
              <span class="amount-value">{{ formatAmount(row.amount) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button link type="primary" @click.stop="viewDetail(row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button link type="warning" @click.stop="addToWatch(row)">
                  <el-icon><Star /></el-icon>
                  自选
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 卡片视图 -->
      <div v-else class="card-view-container">
        <div class="market-cards-grid">
          <div 
            v-for="item in filteredMarketData" 
            :key="item.code"
            class="market-card"
            @click="viewDetail(item)"
          >
            <div class="card-header">
              <div class="card-title">
                <span class="code">{{ item.code }}</span>
                <span class="name">{{ item.name }}</span>
              </div>
              <el-button 
                circle 
                size="small" 
                @click.stop="addToWatch(item)"
                class="watch-btn"
              >
                <el-icon><Star /></el-icon>
              </el-button>
            </div>
            
            <div class="card-price" :class="item.change >= 0 ? 'up' : 'down'">
              <div class="price">{{ item.price.toFixed(2) }}</div>
              <div class="change-info">
                <span class="change">
                  {{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}
                </span>
                <span class="percent">
                  {{ item.changePercent >= 0 ? '+' : '' }}{{ item.changePercent.toFixed(2) }}%
                </span>
              </div>
            </div>
            
            <div class="card-stats">
              <div class="stat">
                <span class="label">今开</span>
                <span class="value">{{ item.open.toFixed(2) }}</span>
              </div>
              <div class="stat">
                <span class="label">最高</span>
                <span class="value high">{{ item.high.toFixed(2) }}</span>
              </div>
              <div class="stat">
                <span class="label">最低</span>
                <span class="value low">{{ item.low.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="footer-item">
                <el-icon><TrendCharts /></el-icon>
                <span>{{ formatVolume(item.volume) }}</span>
              </div>
              <div class="footer-item">
                <el-icon><Money /></el-icon>
                <span>{{ formatAmount(item.amount) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search,
  Refresh,
  Filter,
  Download,
  Grid,
  List,
  Tickets,
  TrendCharts,
  PieChart,
  DataLine,
  View,
  Star,
  CaretTop,
  CaretBottom,
  Money,
  InfoFilled
} from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const searchKeyword = ref('')
const marketType = ref('all')
const changeFilter = ref('all')
const viewMode = ref<'table' | 'card'>('table')
const lastUpdateTime = ref('')

const marketData = ref([
  {
    code: 'IF2512',
    name: '沪深300',
    price: 4520.5,
    change: 45.2,
    changePercent: 1.01,
    open: 4480.0,
    high: 4530.0,
    low: 4475.0,
    volume: 125000,
    amount: 5625000000
  },
  {
    code: 'IC2512',
    name: '中证500',
    price: 6820.3,
    change: -32.5,
    changePercent: -0.47,
    open: 6850.0,
    high: 6865.0,
    low: 6810.0,
    volume: 98000,
    amount: 6683940000
  },
  {
    code: 'IH2512',
    name: '上证50',
    price: 2680.8,
    change: 12.3,
    changePercent: 0.46,
    open: 2670.0,
    high: 2685.0,
    low: 2668.0,
    volume: 78000,
    amount: 2090624000
  },
  {
    code: 'IM2512',
    name: '中证1000',
    price: 7250.2,
    change: -18.6,
    changePercent: -0.26,
    open: 7268.0,
    high: 7275.0,
    low: 7245.0,
    volume: 65000,
    amount: 4712630000
  }
])

const upCount = computed(() => 
  marketData.value.filter(item => item.change > 0).length
)

const downCount = computed(() => 
  marketData.value.filter(item => item.change < 0).length
)

const flatCount = computed(() => 
  marketData.value.filter(item => item.change === 0).length
)

const filteredMarketData = computed(() => {
  return marketData.value.filter(item => {
    const matchKeyword = !searchKeyword.value || 
      item.code.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      item.name.includes(searchKeyword.value)
    
    const matchChange = changeFilter.value === 'all' ||
      (changeFilter.value === 'up' && item.change > 0) ||
      (changeFilter.value === 'down' && item.change < 0) ||
      (changeFilter.value === 'flat' && item.change === 0)
    
    return matchKeyword && matchChange
  })
})

const updateTime = () => {
  const now = new Date()
  lastUpdateTime.value = now.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

const refreshMarket = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateTime()
    ElMessage.success('行情已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row: any) => {
  router.push({
    path: '/futures',
    query: { code: row.code }
  })
}

const addToWatch = (row: any) => {
  ElMessage.success(`已添加 ${row.name} 到自选`)
}

const exportData = () => {
  ElMessage.info('导出功能开发中')
}

const handleRowClick = (row: any) => {
  viewDetail(row)
}

const formatVolume = (volume: number) => {
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatAmount = (amount: number) => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.market-page {
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

  // ==================== 演示模式提示 ====================
  .demo-alert {
    margin-bottom: spacing(lg);
    border-radius: radius(lg);
    box-shadow: shadow(sm);

    .alert-title {
      display: flex;
      align-items: center;
      gap: spacing(sm);
      font-weight: font-weight(bold);
      font-size: font-size(base);
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

            .pulse-dot {
              width: 8px;
              height: 8px;
              background: #73D13D;
              border-radius: 50%;
              animation: pulse 2s ease-in-out infinite;
              box-shadow: 0 0 0 0 rgba(115, 209, 61, 0.7);
            }

            @keyframes pulse {
              0%, 100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(115, 209, 61, 0.7);
              }
              50% {
                transform: scale(1.1);
                box-shadow: 0 0 0 6px rgba(115, 209, 61, 0);
              }
            }

            .update-time {
              margin-left: spacing(sm);
              font-size: font-size(sm);
              opacity: 0.8;
            }
          }
        }
      }

      .header-stats {
        display: flex;
        align-items: center;
        gap: spacing(lg);
        background: rgba(255, 255, 255, 0.15);
        padding: spacing(md) spacing(xl);
        border-radius: radius(lg);
        backdrop-filter: blur(10px);

        .stat-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: spacing(xs);

          .stat-label {
            font-size: font-size(sm);
            color: rgba(255, 255, 255, 0.8);
          }

          .stat-value {
            font-size: font-size(xxl);
            font-weight: font-weight(bold);
            color: #FFFFFF;

            &.up {
              color: #FF7A7E;
            }

            &.down {
              color: #73D13D;
            }
          }
        }

        .stat-divider {
          width: 1px;
          height: 40px;
          background: rgba(255, 255, 255, 0.2);
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
    justify-content: space-between;
    align-items: flex-start;
    gap: spacing(xl);
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

          .search-input,
          .market-select,
          .change-select {
            width: 200px;

            :deep(.el-input__wrapper) {
              border-radius: radius(md);
              transition: all transition(fast) easing(smooth);

              &:hover {
                box-shadow: 0 0 0 1px color(primary-light);
              }
            }
          }

          .option-content {
            display: flex;
            align-items: center;
            gap: spacing(sm);
          }
        }
      }
    }

    .toolbar-actions {
      display: flex;
      gap: spacing(base);
      align-items: flex-end;

      .action-btn {
        padding: spacing(md) spacing(lg);
        border-radius: radius(md);
        font-weight: font-weight(semibold);
        display: flex;
        align-items: center;
        gap: spacing(sm);
        transition: all transition(base) easing(smooth);
        box-shadow: shadow(xs);

        &:hover {
          transform: translateY(-2px);
          box-shadow: shadow(md);
        }

        &.primary {
          background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
          border: none;
          color: #FFFFFF;
        }
      }
    }
  }

  // ==================== 表格卡片 ====================
  .market-table-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    animation: slideUp 0.6s easing(smooth) 0.2s both;

    .table-header {
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

        h3 {
          font-size: font-size(lg);
          font-weight: font-weight(bold);
          color: color(text-primary);
          margin: 0;
          display: flex;
          align-items: center;
          gap: spacing(sm);
        }

        .result-count {
          font-size: font-size(sm);
          color: color(text-tertiary);
          background: color(bg-secondary);
          padding: 2px spacing(base);
          border-radius: radius(circle);
        }
      }

      .view-toggle {
        :deep(.el-button-group) {
          .el-button {
            border-radius: radius(md);
            font-weight: font-weight(medium);
            transition: all transition(fast) easing(smooth);

            &:hover {
              transform: translateY(-1px);
            }
          }
        }
      }
    }

    // 表格容器
    .table-container {
      :deep(.modern-market-table) {
        border-radius: radius(md);
        overflow: hidden;

        .el-table__header {
          th {
            border-bottom: 2px solid color(border-light);
          }
        }

        .el-table__row {
          cursor: pointer;
          transition: all transition(fast) easing(smooth);

          &:hover {
            background: color(bg-hover) !important;
            transform: scale(1.002);
          }
        }

        // 代码单元格
        .code-cell {
          .code-badge {
            font-family: $font-family-code;
            font-weight: font-weight(semibold);
            color: color(primary);
            background: rgba(91, 143, 249, 0.1);
            padding: 4px spacing(base);
            border-radius: radius(sm);
            font-size: font-size(sm);
          }
        }

        // 名称单元格
        .name-cell {
          .name-text {
            font-weight: font-weight(medium);
            color: color(text-primary);
          }
        }

        // 价格单元格
        .price-cell {
          font-size: font-size(lg);
          font-weight: font-weight(bold);

          &.up {
            color: color(danger);
          }

          &.down {
            color: color(success);
          }
        }

        // 涨跌单元格
        .change-cell {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 2px;
          font-weight: font-weight(semibold);

          &.up {
            color: color(danger);
          }

          &.down {
            color: color(success);
          }
        }

        // 涨跌幅标签
        .percent-tag {
          font-weight: font-weight(semibold);
          border: none;
          padding: 4px spacing(base);
        }

        // 数据值
        .data-value {
          color: color(text-secondary);
          font-weight: font-weight(medium);

          &.high {
            color: color(danger);
          }

          &.low {
            color: color(success);
          }
        }

        // 成交量
        .volume-value {
          color: color(text-secondary);
          font-weight: font-weight(medium);
        }

        // 成交额
        .amount-value {
          color: color(text-tertiary);
          font-size: font-size(sm);
        }

        // 操作按钮
        .action-buttons {
          display: flex;
          gap: spacing(sm);

          .el-button {
            font-weight: font-weight(medium);
            transition: all transition(fast) easing(smooth);

            &:hover {
              transform: scale(1.05);
            }
          }
        }
      }
    }

    // 卡片视图容器
    .card-view-container {
      .market-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: spacing(lg);

        .market-card {
          background: #FFFFFF;
          border: 2px solid color(border-light);
          border-radius: radius(xl);
          padding: spacing(lg);
          cursor: pointer;
          transition: all transition(base) easing(smooth);
          position: relative;
          overflow: hidden;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #5B8FF9 0%, #7AA5FF 100%);
            transform: scaleX(0);
            transition: transform transition(base) easing(smooth);
          }

          &:hover {
            border-color: color(primary);
            box-shadow: shadow(lg);
            transform: translateY(-4px);

            &::before {
              transform: scaleX(1);
            }

            .watch-btn {
              opacity: 1;
            }
          }

          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: spacing(md);

            .card-title {
              display: flex;
              flex-direction: column;
              gap: spacing(xs);

              .code {
                font-family: $font-family-code;
                font-size: font-size(base);
                font-weight: font-weight(bold);
                color: color(primary);
              }

              .name {
                font-size: font-size(sm);
                color: color(text-secondary);
              }
            }

            .watch-btn {
              opacity: 0;
              transition: all transition(base) easing(smooth);

              &:hover {
                color: color(warning);
                transform: scale(1.1);
              }
            }
          }

          .card-price {
            margin-bottom: spacing(md);
            padding-bottom: spacing(md);
            border-bottom: 1px solid color(border-light);

            .price {
              font-size: font-size(xxxl);
              font-weight: font-weight(bold);
              margin-bottom: spacing(xs);
            }

            .change-info {
              display: flex;
              gap: spacing(sm);
              font-size: font-size(sm);
              font-weight: font-weight(semibold);

              .change,
              .percent {
                padding: 2px spacing(sm);
                border-radius: radius(sm);
              }
            }

            &.up {
              .price,
              .change,
              .percent {
                color: color(danger);
              }

              .change,
              .percent {
                background: rgba(255, 122, 126, 0.1);
              }
            }

            &.down {
              .price,
              .change,
              .percent {
                color: color(success);
              }

              .change,
              .percent {
                background: rgba(115, 209, 61, 0.1);
              }
            }
          }

          .card-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: spacing(sm);
            margin-bottom: spacing(md);

            .stat {
              display: flex;
              flex-direction: column;
              gap: 2px;

              .label {
                font-size: font-size(xs);
                color: color(text-tertiary);
              }

              .value {
                font-size: font-size(base);
                font-weight: font-weight(semibold);
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

          .card-footer {
            display: flex;
            justify-content: space-between;
            padding-top: spacing(md);
            border-top: 1px solid color(border-light);

            .footer-item {
              display: flex;
              align-items: center;
              gap: spacing(xs);
              font-size: font-size(sm);
              color: color(text-tertiary);
            }
          }
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

        .header-stats {
          width: 100%;
          justify-content: space-around;
        }
      }
    }

    .toolbar-card {
      flex-direction: column;

      .toolbar-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }
  }

  @media (max-width: 768px) {
    padding: spacing(base);

    .toolbar-card {
      .toolbar-section {
        .toolbar-controls {
          flex-direction: column;

          .control-group {
            .search-input,
            .market-select,
            .change-select {
              width: 100%;
            }
          }
        }
      }
    }

    .market-table-card {
      .card-view-container {
        .market-cards-grid {
          grid-template-columns: 1fr;
        }
      }
    }
  }
}
</style>
