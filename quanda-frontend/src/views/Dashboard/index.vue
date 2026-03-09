<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <div class="stat-card">
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-value" :class="stat.trend">{{ stat.value }}</div>
          <div class="stat-change" :class="stat.trend">
            <el-icon><component :is="stat.trend === 'up' ? 'CaretTop' : 'CaretBottom'" /></el-icon>
            {{ stat.change }}
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <div class="card">
          <h3>账户资产趋势</h3>
          <LineChart :data="accountHistory" height="350px" />
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card">
          <h3>月度收益</h3>
          <LineChart :data="monthProfit" height="350px" color="#52c41a" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="card">
          <h3>最近交易</h3>
          <el-table :data="recentTrades" stripe>
            <el-table-column prop="datetime" label="时间" width="180" />
            <el-table-column prop="code" label="合约" width="120" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'BUY' ? 'danger' : 'success'">
                  {{ row.direction }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="offset" label="开平" width="80" />
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column prop="volume" label="数量" width="80" />
            <el-table-column prop="commission" label="手续费" width="100" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAccountStore } from '@/stores/account'
import LineChart from '@/components/Charts/LineChart.vue'

const accountStore = useAccountStore()

const stats = ref([
  { title: '总资产', value: '¥1,234,567', change: '+12.5%', trend: 'up' },
  { title: '可用资金', value: '¥987,654', change: '+8.3%', trend: 'up' },
  { title: '持仓市值', value: '¥246,913', change: '-3.2%', trend: 'down' },
  { title: '今日收益', value: '¥12,345', change: '+5.6%', trend: 'up' }
])

const accountHistory = ref([])
const monthProfit = ref([])
const recentTrades = ref([])

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
.dashboard {
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
    font-weight: 600;
  }
}
</style>
