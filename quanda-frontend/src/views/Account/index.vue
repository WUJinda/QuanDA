<template>
  <div class="account-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <AccountSelector @change="handleAccountChange" />
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button type="danger" @click="handleDeleteAccount">
          <el-icon><Delete /></el-icon>
          删除账户
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in accountStats" :key="stat.label">
        <div class="stat-card">
          <div class="stat-title">{{ stat.label }}</div>
          <div class="stat-value" :class="stat.trend">{{ stat.value }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <div class="card">
          <h3>账户资产曲线</h3>
          <LineChart :data="accountHistory" height="300px" />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <h3>月度收益</h3>
          <LineChart :data="monthProfit" height="300px" color="#52c41a" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="card">
          <h3>交易记录</h3>
          <el-table :data="tradeRecords" stripe max-height="400">
            <el-table-column prop="datetime" label="交易时间" width="180" />
            <el-table-column prop="code" label="合约代码" width="120" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'BUY' ? 'danger' : 'success'">
                  {{ row.direction }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="offset" label="开平" width="80">
              <template #default="{ row }">
                <el-tag :type="row.offset === 'OPEN' ? 'warning' : 'info'">
                  {{ row.offset }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="成交价格" width="120" />
            <el-table-column prop="volume" label="成交数量" width="100" />
            <el-table-column prop="commission" label="手续费" width="100" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountStore } from '@/stores/account'
import AccountSelector from '@/components/Account/AccountSelector.vue'
import LineChart from '@/components/Charts/LineChart.vue'
import { accountApi } from '@/api/account'

const accountStore = useAccountStore()

const loading = ref(false)
const currentAccount = ref('')
const accountHistory = ref({})
const monthProfit = ref({})
const tradeRecords = ref([])
const accountStats = ref([
  { label: '账户余额', value: '¥0', trend: '' },
  { label: '可用资金', value: '¥0', trend: '' },
  { label: '持仓盈亏', value: '¥0', trend: 'up' },
  { label: '累计收益', value: '¥0', trend: 'up' }
])

const handleAccountChange = async (account: string) => {
  currentAccount.value = account
  await refreshData()
}

const refreshData = async () => {
  if (!currentAccount.value) return
  
  loading.value = true
  try {
    accountHistory.value = await accountStore.fetchAccountHistory(currentAccount.value)
    monthProfit.value = await accountStore.fetchMonthProfit(currentAccount.value)
    tradeRecords.value = await accountStore.fetchTradeRecords(currentAccount.value)
    
    const historyValues = Object.values(accountHistory.value)
    if (historyValues.length > 0) {
      const latestBalance = historyValues[historyValues.length - 1] as number
      accountStats.value[0].value = `¥${latestBalance.toLocaleString()}`
    }
  } catch (error) {
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

const handleDeleteAccount = async () => {
  if (!currentAccount.value) {
    ElMessage.warning('请先选择账户')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要删除该账户吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await accountApi.dropAccount(currentAccount.value)
    ElMessage.success('删除成功')
    await accountStore.fetchAccountList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.account-page {
  h3 {
    margin-bottom: 20px;
    font-size: 16px;
    font-weight: 600;
  }
}
</style>
