<template>
  <div class="strategy-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建策略
        </el-button>
        <el-button @click="importStrategy">
          <el-icon><Upload /></el-icon>
          导入策略
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索策略"
          style="width: 200px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="strategy in filteredStrategies" :key="strategy.id">
        <el-card class="strategy-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="strategy-name">{{ strategy.name }}</span>
              <el-tag :type="strategy.status === '运行中' ? 'success' : 'info'">
                {{ strategy.status }}
              </el-tag>
            </div>
          </template>
          <div class="strategy-info">
            <p><strong>类型:</strong> {{ strategy.type }}</p>
            <p><strong>创建时间:</strong> {{ strategy.createTime }}</p>
            <p><strong>累计收益:</strong> 
              <span :class="strategy.profit >= 0 ? 'up' : 'down'">
                {{ strategy.profit }}%
              </span>
            </p>
            <p class="description">{{ strategy.description }}</p>
          </div>
          <template #footer>
            <div class="card-footer">
              <el-button link type="primary" @click="editStrategy(strategy)">
                编辑
              </el-button>
              <el-button link type="primary" @click="viewDetail(strategy)">
                详情
              </el-button>
              <el-button link type="danger" @click="deleteStrategy(strategy)">
                删除
              </el-button>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showCreateDialog" title="新建策略" width="600px">
      <el-form :model="strategyForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="strategyForm.type" placeholder="选择策略类型">
            <el-option label="趋势跟踪" value="trend" />
            <el-option label="均值回归" value="mean_reversion" />
            <el-option label="套利策略" value="arbitrage" />
            <el-option label="高频交易" value="hft" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略描述">
          <el-input
            v-model="strategyForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入策略描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createStrategy">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const searchKeyword = ref('')
const showCreateDialog = ref(false)

const strategies = ref([
  {
    id: 1,
    name: '双均线策略',
    type: '趋势跟踪',
    status: '运行中',
    createTime: '2024-01-15',
    profit: 15.6,
    description: '基于5日和20日均线的交叉策略'
  },
  {
    id: 2,
    name: 'MACD策略',
    type: '趋势跟踪',
    status: '已停止',
    createTime: '2024-02-10',
    profit: -3.2,
    description: 'MACD指标金叉死叉策略'
  }
])

const strategyForm = ref({
  name: '',
  type: '',
  description: ''
})

const filteredStrategies = computed(() => {
  if (!searchKeyword.value) return strategies.value
  return strategies.value.filter(s => 
    s.name.includes(searchKeyword.value) || 
    s.description.includes(searchKeyword.value)
  )
})

const editStrategy = (strategy: any) => {
  ElMessage.info(`编辑策略: ${strategy.name}`)
}

const viewDetail = (strategy: any) => {
  ElMessage.info(`查看详情: ${strategy.name}`)
}

const deleteStrategy = (strategy: any) => {
  ElMessage.warning(`删除策略: ${strategy.name}`)
}

const importStrategy = () => {
  ElMessage.info('导入策略')
}

const createStrategy = () => {
  if (!strategyForm.value.name || !strategyForm.value.type) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  ElMessage.success('策略创建成功')
  showCreateDialog.value = false
}
</script>

<style lang="scss" scoped>
.strategy-page {
  .strategy-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .strategy-name {
        font-size: 16px;
        font-weight: 600;
      }
    }
    
    .strategy-info {
      p {
        margin: 8px 0;
        font-size: 14px;
        
        &.description {
          color: #666;
          margin-top: 12px;
        }
      }
      
      .up {
        color: #f5222d;
      }
      
      .down {
        color: #52c41a;
      }
    }
    
    .card-footer {
      display: flex;
      justify-content: space-around;
    }
  }
}
</style>
