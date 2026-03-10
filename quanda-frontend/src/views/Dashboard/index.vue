<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="welcome-text">
          <h1 class="greeting">
            <span class="wave">👋</span>
            欢迎回来
          </h1>
          <p class="subtitle">今天也要加油交易哦！</p>
        </div>
        <div class="quick-actions">
          <el-button type="primary" class="action-btn" @click="handleQuickTrade">
            <el-icon><TrendCharts /></el-icon>
            快速交易
          </el-button>
          <el-button class="action-btn secondary" @click="handleViewStrategy">
            <el-icon><DataAnalysis /></el-icon>
            策略分析
          </el-button>
        </div>
      </div>
      <div class="banner-decoration">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>

    <!-- 核心数据卡片 -->
    <div class="stats-grid">
      <div 
        v-for="(stat, index) in stats" 
        :key="stat.title"
        class="stat-card"
        :class="`stat-card-${index + 1}`"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <div class="stat-icon" :class="stat.iconClass">
          <el-icon :size="28">
            <component :is="stat.icon" />
          </el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-footer">
            <span class="stat-change" :class="stat.trend">
              <el-icon :size="14">
                <component :is="stat.trend === 'up' ? 'CaretTop' : 'CaretBottom'" />
              </el-icon>
              {{ stat.change }}
            </span>
            <span class="stat-label">较昨日</span>
          </div>
        </div>
        <div class="stat-bg-icon">
          <el-icon :size="80">
            <component :is="stat.icon" />
          </el-icon>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="24" class="charts-row">
      <el-col :span="16">
        <div class="chart-card main-chart">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div>
                <h3>账户资产趋势</h3>
                <p class="card-subtitle">近30天资产变化曲线</p>
              </div>
            </div>
            <div class="header-actions">
              <el-button-group size="small">
                <el-button :type="timeRange === '7d' ? 'primary' : ''" @click="timeRange = '7d'">7天</el-button>
                <el-button :type="timeRange === '30d' ? 'primary' : ''" @click="timeRange = '30d'">30天</el-button>
                <el-button :type="timeRange === '90d' ? 'primary' : ''" @click="timeRange = '90d'">90天</el-button>
              </el-button-group>
            </div>
          </div>
          <div class="chart-container">
            <LineChart :data="accountHistory" height="320px" />
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="chart-card profit-chart">
          <div class="card-header">
            <div class="header-left">
              <div class="header-icon orange">
                <el-icon><Histogram /></el-icon>
              </div>
              <div>
                <h3>月度收益</h3>
                <p class="card-subtitle">本月累计收益统计</p>
              </div>
            </div>
          </div>
          <div class="chart-container">
            <LineChart :data="monthProfit" height="320px" color="#FFA940" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 交易记录 -->
    <div class="trades-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon purple">
            <el-icon><List /></el-icon>
          </div>
          <div>
            <h3>最近交易</h3>
            <p class="card-subtitle">最新10条交易记录</p>
          </div>
        </div>
        <el-button text type="primary" @click="handleViewAll">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="table-container">
        <el-table 
          :data="recentTrades" 
          class="modern-table"
          :header-cell-style="{ background: '#F5F7FA', color: '#595959', fontWeight: '600' }"
        >
          <el-table-column prop="datetime" label="时间" width="180">
            <template #default="{ row }">
              <div class="table-time">
                <el-icon><Clock /></el-icon>
                {{ row.datetime }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="合约" width="120">
            <template #default="{ row }">
              <span class="table-code">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="direction" label="方向" width="100">
            <template #default="{ row }">
              <el-tag 
                :type="row.direction === 'BUY' ? 'danger' : 'success'" 
                effect="light"
                round
              >
                {{ row.direction === 'BUY' ? '买入' : '卖出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="offset" label="开平" width="100">
            <template #default="{ row }">
              <el-tag effect="plain" round>{{ row.offset }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="120" align="right">
            <template #default="{ row }">
              <span class="table-price">¥{{ row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="数量" width="100" align="right" />
          <el-table-column prop="commission" label="手续费" width="120" align="right">
            <template #default="{ row }">
              <span class="table-commission">¥{{ row.commission }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/account'
import { 
  TrendCharts, 
  DataAnalysis, 
  Histogram,
  List,
  ArrowRight,
  Clock} from '@element-plus/icons-vue'
import LineChart from '@/components/Charts/LineChart.vue'

const router = useRouter()
const accountStore = useAccountStore()

const timeRange = ref('30d')

const stats = ref([
  { 
    title: '总资产', 
    value: '¥1,234,567', 
    change: '+12.5%', 
    trend: 'up',
    icon: 'Wallet',
    iconClass: 'blue'
  },
  { 
    title: '可用资金', 
    value: '¥987,654', 
    change: '+8.3%', 
    trend: 'up',
    icon: 'Money',
    iconClass: 'orange'
  },
  { 
    title: '持仓市值', 
    value: '¥246,913', 
    change: '-3.2%', 
    trend: 'down',
    icon: 'PieChart',
    iconClass: 'purple'
  },
  { 
    title: '今日收益', 
    value: '¥12,345', 
    change: '+5.6%', 
    trend: 'up',
    icon: 'TrendCharts',
    iconClass: 'green'
  }
])

const accountHistory = ref([])
const monthProfit = ref([])
const recentTrades = ref([])

const handleQuickTrade = () => {
  router.push('/futures')
}

const handleViewStrategy = () => {
  router.push('/strategy')
}

const handleViewAll = () => {
  router.push('/account')
}

onMounted(async () => {
  await accountStore.fetchAccountList()
  if (accountStore.accountList.length > 0) {
    const account = accountStore.accountList[0]
    accountHistory.value = await accountStore.fetchAccountHistory(account)
    monthProfit.value = await accountStore.fetchMonthProfit(account)
    recentTrades.value = (await accountStore.fetchTradeRecords(account)).slice(0, 10)
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/design-system.scss';

.dashboard {
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

  // ==================== 欢迎横幅 ====================
  .welcome-banner {
    position: relative;
    background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
    border-radius: radius(xl);
    padding: spacing(xxl) spacing(xl);
    margin-bottom: spacing(xl);
    overflow: hidden;
    box-shadow: shadow(lg);

    .banner-content {
      position: relative;
      z-index: 2;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .welcome-text {
      .greeting {
        font-size: font-size(huge);
        font-weight: font-weight(bold);
        color: #FFFFFF;
        margin: 0 0 spacing(sm) 0;
        display: flex;
        align-items: center;
        gap: spacing(base);

        .wave {
          display: inline-block;
          animation: wave 2s ease-in-out infinite;
        }

        @keyframes wave {
          0%, 100% { transform: rotate(0deg); }
          25% { transform: rotate(20deg); }
          75% { transform: rotate(-20deg); }
        }
      }

      .subtitle {
        font-size: font-size(lg);
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
      }
    }

    .quick-actions {
      display: flex;
      gap: spacing(base);

      .action-btn {
        padding: spacing(md) spacing(xl);
        font-size: font-size(base);
        font-weight: font-weight(semibold);
        border-radius: radius(lg);
        border: none;
        display: flex;
        align-items: center;
        gap: spacing(sm);
        transition: all transition(base) easing(smooth);
        box-shadow: shadow(sm);

        &:hover {
          transform: translateY(-2px);
          box-shadow: shadow(md);
        }

        &.secondary {
          background: rgba(255, 255, 255, 0.2);
          color: #FFFFFF;
          backdrop-filter: blur(10px);

          &:hover {
            background: rgba(255, 255, 255, 0.3);
          }
        }
      }
    }

    .banner-decoration {
      position: absolute;
      top: 0;
      right: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      overflow: hidden;

      .circle {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        animation: float 6s ease-in-out infinite;

        &.circle-1 {
          width: 200px;
          height: 200px;
          top: -50px;
          right: 100px;
          animation-delay: 0s;
        }

        &.circle-2 {
          width: 150px;
          height: 150px;
          top: 50px;
          right: -30px;
          animation-delay: 2s;
        }

        &.circle-3 {
          width: 100px;
          height: 100px;
          bottom: -20px;
          right: 200px;
          animation-delay: 4s;
        }
      }

      @keyframes float {
        0%, 100% {
          transform: translateY(0) scale(1);
        }
        50% {
          transform: translateY(-20px) scale(1.05);
        }
      }
    }
  }

  // ==================== 统计卡片网格 ====================
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: spacing(lg);
    margin-bottom: spacing(xl);

    @media (max-width: 1400px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }

  .stat-card {
    position: relative;
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    transition: all transition(base) easing(smooth);
    overflow: hidden;
    animation: slideUp 0.6s easing(smooth) both;

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

    &:hover {
      box-shadow: shadow(lg);
      transform: translateY(-4px);
      border-color: color(primary-light);

      .stat-icon {
        transform: scale(1.1) rotate(5deg);
      }

      .stat-bg-icon {
        opacity: 0.15;
        transform: translate(10px, -10px) rotate(15deg);
      }
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: radius(lg);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: spacing(md);
      transition: all transition(base) easing(bouncy);
      box-shadow: shadow(sm);

      &.blue {
        background: linear-gradient(135deg, #5B8FF9 0%, #7AA5FF 100%);
        color: #FFFFFF;
      }

      &.orange {
        background: linear-gradient(135deg, #FFA940 0%, #FFD666 100%);
        color: #FFFFFF;
      }

      &.purple {
        background: linear-gradient(135deg, #9254DE 0%, #B37FEB 100%);
        color: #FFFFFF;
      }

      &.green {
        background: linear-gradient(135deg, #73D13D 0%, #95DE64 100%);
        color: #FFFFFF;
      }
    }

    .stat-content {
      position: relative;
      z-index: 2;

      .stat-title {
        font-size: font-size(sm);
        color: color(text-secondary);
        margin-bottom: spacing(xs);
        font-weight: font-weight(medium);
      }

      .stat-value {
        font-size: font-size(xxxl);
        font-weight: font-weight(bold);
        color: color(text-primary);
        margin-bottom: spacing(sm);
        letter-spacing: -0.5px;
      }

      .stat-footer {
        display: flex;
        align-items: center;
        gap: spacing(sm);

        .stat-change {
          display: inline-flex;
          align-items: center;
          gap: 2px;
          font-size: font-size(sm);
          font-weight: font-weight(semibold);
          padding: 2px spacing(sm);
          border-radius: radius(circle);

          &.up {
            color: color(danger);
            background: rgba(255, 122, 126, 0.1);
          }

          &.down {
            color: color(success);
            background: rgba(115, 209, 61, 0.1);
          }
        }

        .stat-label {
          font-size: font-size(xs);
          color: color(text-tertiary);
        }
      }
    }

    .stat-bg-icon {
      position: absolute;
      right: -10px;
      bottom: -10px;
      opacity: 0.05;
      transition: all transition(slow) easing(smooth);
      color: color(primary);
    }
  }

  // ==================== 图表区域 ====================
  .charts-row {
    margin-bottom: spacing(xl);
  }

  .chart-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    height: 100%;
    transition: all transition(base) easing(smooth);

    &:hover {
      box-shadow: shadow(md);
      border-color: color(primary-light);
    }

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

        .card-subtitle {
          font-size: font-size(sm);
          color: color(text-tertiary);
          margin: spacing(xs) 0 0 0;
        }
      }

      .header-actions {
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

    .chart-container {
      position: relative;
    }
  }

  // ==================== 交易记录卡片 ====================
  .trades-card {
    background: #FFFFFF;
    border-radius: radius(xl);
    padding: spacing(xl);
    box-shadow: shadow(sm);
    border: 1px solid color(border-light);
    transition: all transition(base) easing(smooth);

    &:hover {
      box-shadow: shadow(md);
      border-color: color(primary-light);
    }

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
          background: linear-gradient(135deg, #9254DE 0%, #B37FEB 100%);
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
    }

    .table-container {
      :deep(.modern-table) {
        .el-table__header {
          th {
            border-bottom: 2px solid color(border-light);
          }
        }

        .el-table__row {
          transition: all transition(fast) easing(smooth);

          &:hover {
            background: color(bg-hover) !important;
            transform: scale(1.01);
          }
        }

        .table-time {
          display: flex;
          align-items: center;
          gap: spacing(xs);
          color: color(text-secondary);
          font-size: font-size(sm);
        }

        .table-code {
          font-family: $font-family-code;
          font-weight: font-weight(semibold);
          color: color(primary);
          background: rgba(91, 143, 249, 0.1);
          padding: 2px spacing(sm);
          border-radius: radius(sm);
        }

        .table-price {
          font-weight: font-weight(semibold);
          color: color(text-primary);
        }

        .table-commission {
          color: color(text-tertiary);
          font-size: font-size(sm);
        }

        .el-tag {
          font-weight: font-weight(medium);
          border: none;
        }
      }
    }
  }
}
</style>
