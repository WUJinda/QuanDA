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
              <button class="action-btn detail-btn" @click.stop="viewDetail(strategy)">
                <el-icon><View /></el-icon>
                详情
              </button>
              <button class="action-btn edit-btn" @click.stop="editStrategy(strategy)">
                <el-icon><Edit /></el-icon>
                编辑
              </button>
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

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑策略" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="editForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="editForm.type" placeholder="选择策略类型">
            <el-option label="趋势跟踪" value="趋势跟踪" />
            <el-option label="均值回归" value="均值回归" />
            <el-option label="套利策略" value="套利策略" />
            <el-option label="高频交易" value="高频交易" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略状态">
          <el-select v-model="editForm.status" placeholder="选择策略状态">
            <el-option label="运行中" value="运行中" />
            <el-option label="已停止" value="已停止" />
            <el-option label="测试中" value="测试中" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入策略描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="danger" @click="deleteStrategy(currentEditStrategy)">删除</el-button>
        <el-button type="primary" @click="updateStrategy">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="策略详情" width="800px">
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">
            {{ currentDetail.name }}
          </el-descriptions-item>
          <el-descriptions-item label="策略类型">
            {{ currentDetail.type }}
          </el-descriptions-item>
          <el-descriptions-item label="策略状态">
            <el-tag :type="currentDetail.status === '运行中' ? 'success' : 'info'">
              {{ currentDetail.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentDetail.createTime }}
          </el-descriptions-item>
          <el-descriptions-item label="累计收益">
            <span :class="currentDetail.profit >= 0 ? 'profit-up' : 'profit-down'">
              {{ currentDetail.profit }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="策略描述" :span="2">
            {{ currentDetail.description }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Search, View, Edit } from '@element-plus/icons-vue'

const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const currentEditStrategy = ref<any>(null)
const currentDetail = ref<any>(null)

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

const editForm = ref({
  name: '',
  type: '',
  status: '',
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
  currentEditStrategy.value = strategy
  editForm.value = {
    name: strategy.name,
    type: strategy.type,
    status: strategy.status,
    description: strategy.description
  }
  showEditDialog.value = true
}

const viewDetail = (strategy: any) => {
  currentDetail.value = strategy
  showDetailDialog.value = true
}

const updateStrategy = () => {
  if (!editForm.value.name || !editForm.value.type) {
    ElMessage.warning('请填写完整信息')
    return
  }

  const index = strategies.value.findIndex(s => s.id === currentEditStrategy.value.id)
  if (index !== -1) {
    strategies.value[index] = {
      ...strategies.value[index],
      name: editForm.value.name,
      type: editForm.value.type,
      status: editForm.value.status,
      description: editForm.value.description
    }
  }

  ElMessage.success('策略更新成功')
  showEditDialog.value = false
}

const deleteStrategy = (strategy: any) => {
  // 如果是从编辑对话框调用的，strategy 已经是 currentEditStrategy
  if (!strategy) {
    strategy = currentEditStrategy.value
  }

  ElMessageBox.confirm(
    `确定要删除策略"${strategy.name}"吗？删除后无法恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    const index = strategies.value.findIndex(s => s.id === strategy.id)
    if (index !== -1) {
      strategies.value.splice(index, 1)
    }
    ElMessage.success('策略删除成功')
    showEditDialog.value = false
  }).catch(() => {
    // 用户取消删除
  })
}

const importStrategy = () => {
  ElMessage.info('导入策略功能开发中...')
}

const createStrategy = () => {
  if (!strategyForm.value.name || !strategyForm.value.type) {
    ElMessage.warning('请填写完整信息')
    return
  }

  const newStrategy = {
    id: Date.now(),
    name: strategyForm.value.name,
    type: strategyForm.value.type === 'trend' ? '趋势跟踪' :
          strategyForm.value.type === 'mean_reversion' ? '均值回归' :
          strategyForm.value.type === 'arbitrage' ? '套利策略' : '高频交易',
    status: '已停止',
    createTime: new Date().toISOString().split('T')[0],
    profit: 0,
    description: strategyForm.value.description
  }

  strategies.value.unshift(newStrategy)
  ElMessage.success('策略创建成功')
  showCreateDialog.value = false

  // 重置表单
  strategyForm.value = {
    name: '',
    type: '',
    description: ''
  }
}
</script>

<style lang="scss" scoped>
.strategy-page {
  /* CSS 变量定义 */
  --color-primary: #5B8FF9;
  --color-secondary: #9254DE;
  --color-success: #73D13D;
  --color-danger: #FF7A7E;
  --color-bg: #FFFFFF;
  --color-bg-light: #F5F7FA;
  --color-text: #262626;
  --color-text-secondary: #595959;
  --color-border: #E8E8E8;
  --radius-md: 8px;
  --radius-lg: 12px;
  --spacing-sm: 12px;
  --spacing-md: 16px;

  .strategy-card {
    margin-bottom: 20px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 20px rgba(91, 143, 249, 0.15);
      transform: translateY(-2px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .strategy-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--color-text);
      }
    }

    .strategy-info {
      p {
        margin: 8px 0;
        font-size: 14px;
        color: var(--color-text-secondary);

        &.description {
          color: #8C8C8C;
          margin-top: 12px;
        }

        strong {
          color: var(--color-text);
          font-weight: 500;
        }
      }

      .profit-up {
        color: var(--color-danger);
        font-weight: 600;
      }

      .profit-down {
        color: var(--color-success);
        font-weight: 600;
      }
    }

    .card-footer {
      display: flex;
      gap: var(--spacing-sm);
      padding: var(--spacing-sm) 0;

      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 16px;
        border: none;
        border-radius: var(--radius-md);
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.25s ease;

        .el-icon {
          font-size: 16px;
        }

        &.detail-btn {
          background: linear-gradient(135deg, rgba(91, 143, 249, 0.1) 0%, rgba(91, 143, 249, 0.05) 100%);
          color: var(--color-primary);

          &:hover {
            background: linear-gradient(135deg, rgba(91, 143, 249, 0.2) 0%, rgba(91, 143, 249, 0.1) 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(91, 143, 249, 0.2);
          }

          &:active {
            transform: translateY(0);
          }
        }

        &.edit-btn {
          background: linear-gradient(135deg, rgba(146, 84, 222, 0.1) 0%, rgba(146, 84, 222, 0.05) 100%);
          color: var(--color-secondary);

          &:hover {
            background: linear-gradient(135deg, rgba(146, 84, 222, 0.2) 0%, rgba(146, 84, 222, 0.1) 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(146, 84, 222, 0.2);
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  .detail-content {
    .profit-up {
      color: var(--color-danger);
      font-weight: 600;
    }

    .profit-down {
      color: var(--color-success);
      font-weight: 600;
    }
  }
}

/* Element Plus 对话框样式优化 */
:deep(.el-dialog) {
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);

  .el-dialog__header {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
  }

  .el-dialog__body {
    padding: var(--spacing-md);
  }

  .el-dialog__footer {
    padding: var(--spacing-md);
    border-top: 1px solid var(--color-border);
  }
}

/* 卡片样式优化 */
:deep(.el-card) {
  border-radius: var(--radius-lg);

  .el-card__header {
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--color-bg-light);
    border-bottom: 1px solid var(--color-border);
  }

  .el-card__body {
    padding: var(--spacing-md);
  }

  .el-card__footer {
    padding: 0 var(--spacing-md) var(--spacing-md);
    border-top: 1px solid var(--color-border);
  }
}
</style>
