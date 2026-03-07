<template>
  <div class="market-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索合约代码"
          style="width: 200px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="marketType" placeholder="市场类型" style="width: 150px;">
          <el-option label="全部" value="all" />
          <el-option label="期货" value="future" />
          <el-option label="股票" value="stock" />
          <el-option label="指数" value="index" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="refreshMarket" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新行情
        </el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="filteredMarketData" stripe height="600">
        <el-table-column prop="code" label="代码" width="120" fixed />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="price" label="最新价" width="100">
          <template #default="{ row }">
            <span :class="row.change >= 0 ? 'up' : 'down'">
              {{ row.price }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌" width="100">
          <template #default="{ row }">
            <span :class="row.change >= 0 ? 'up' : 'down'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="changePercent" label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="row.changePercent >= 0 ? 'up' : 'down'">
              {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="open" label="今开" width="100" />
        <el-table-column prop="high" label="最高" width="100" />
        <el-table-column prop="low" label="最低" width="100" />
        <el-table-column prop="volume" label="成交量" width="120" />
        <el-table-column prop="amount" label="成交额" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button link type="primary" @click="addToWatch(row)">
              自选
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const loading = ref(false)
const searchKeyword = ref('')
const marketType = ref('all')
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
  }
])

const filteredMarketData = computed(() => {
  return marketData.value.filter(item => {
    const matchKeyword = !searchKeyword.value || 
      item.code.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      item.name.includes(searchKeyword.value)
    return matchKeyword
  })
})

const refreshMarket = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
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
</script>

<style lang="scss" scoped>
.market-page {
  .up {
    color: #f5222d;
  }
  
  .down {
    color: #52c41a;
  }
}
</style>
