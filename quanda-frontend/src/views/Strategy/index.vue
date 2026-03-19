<template>
  <div class="strategy-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建策略
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索策略"
          style="width: 200px;"
          clearable
          @keyup.enter="loadStrategyList"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="strategy in strategies" :key="strategy.id">
        <el-card class="strategy-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="strategy-name">{{ strategy.name }}</span>
              <el-tag :type="strategy.status === 'running' ? 'success' : 'info'" size="small">
                {{ strategy.status === 'running' ? '运行中' : '已停止' }}
              </el-tag>
            </div>
          </template>
          <div class="strategy-info">
            <p><strong>类型:</strong> {{ getStrategyTypeLabel(strategy.type) }}</p>
            <p><strong>创建时间:</strong> {{ strategy.create_time?.split('T')[0] }}</p>
            <p><strong>累计收益:</strong>
              <span :class="strategy.profit >= 0 ? 'up' : 'down'">
                {{ strategy.profit }}%
              </span>
            </p>
            <p class="description">{{ strategy.description || '暂无描述' }}</p>
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

    <div v-if="strategies.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无策略，点击上方按钮创建" />
    </div>

    <!-- 创建策略对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建策略" width="600px">
      <el-form :model="strategyForm" label-width="100px">
        <el-form-item label="策略名称" required>
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="strategyForm.type" placeholder="选择策略类型" style="width: 100%">
            <el-option v-for="item in STRATEGY_TYPES" :key="item.value" :label="item.label" :value="item.value" />
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
        <el-form-item label="策略代码">
          <el-input
            v-model="strategyForm.code"
            type="textarea"
            :rows="10"
            placeholder="请输入策略代码（Python）"
            font-family="monospace"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createStrategy" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑策略" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="策略名称" required>
          <el-input v-model="editForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="editForm.type" placeholder="选择策略类型" style="width: 100%">
            <el-option v-for="item in STRATEGY_TYPES" :key="item.value" :label="item.label" :value="item.value" />
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
        <el-button type="primary" @click="updateStrategy" :loading="updating">保存</el-button>
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
            {{ getStrategyTypeLabel(currentDetail.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="策略状态">
            <el-tag :type="currentDetail.status === 'running' ? 'success' : 'info'">
              {{ currentDetail.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentDetail.create_time }}
          </el-descriptions-item>
          <el-descriptions-item label="累计收益">
            <span :class="currentDetail.profit >= 0 ? 'profit-up' : 'profit-down'">
              {{ currentDetail.profit }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="夏普比率">
            {{ currentDetail.sharpe_ratio || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤">
            <span class="profit-down">{{ currentDetail.max_drawdown || '-' }}%</span>
          </el-descriptions-item>
          <el-descriptions-item label="策略描述" :span="2">
            {{ currentDetail.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button
            v-if="currentDetail.status !== 'running'"
            type="success"
            @click="startStrategy(currentDetail)"
          >
            启动策略
          </el-button>
          <el-button
            v-else
            type="danger"
            @click="stopStrategy(currentDetail)"
          >
            停止策略
          </el-button>
          <el-button @click="goToBacktest(currentDetail)">
            运行回测
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Edit } from '@element-plus/icons-vue'
import { strategyApi } from '@/api/strategy'
import { STRATEGY_TYPES } from '@/types/strategy'
import type { Strategy, StrategyConfig } from '@/types/strategy'

const router = useRouter()

const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const currentEditStrategy = ref<Strategy | null>(null)
const currentDetail = ref<Strategy | null>(null)

const strategies = ref<Strategy[]>([])

const strategyForm = ref<StrategyConfig>({
  name: '',
  type: 'custom',
  description: '',
  code: ''
})

const editForm = ref({
  name: '',
  type: '',
  description: ''
})

const loadStrategyList = async () => {
  loading.value = true
  try {
    const response = await strategyApi.getList(0, 100, searchKeyword.value)
    strategies.value = response.list || []
  } catch (error) {
    console.error('加载策略列表失败:', error)
    ElMessage.error('加载策略列表失败')
  } finally {
    loading.value = false
  }
}

const createStrategy = async () => {
  if (!strategyForm.value.name) {
    ElMessage.warning('请输入策略名称')
    return
  }

  creating.value = true
  try {
    await strategyApi.create(strategyForm.value)
    ElMessage.success('策略创建成功')
    showCreateDialog.value = false

    // 重置表单
    strategyForm.value = {
      name: '',
      type: 'custom',
      description: '',
      code: ''
    }

    loadStrategyList()
  } catch (error) {
    ElMessage.error('创建策略失败')
  } finally {
    creating.value = false
  }
}

const editStrategy = (strategy: Strategy) => {
  currentEditStrategy.value = strategy
  editForm.value = {
    name: strategy.name,
    type: strategy.type,
    description: strategy.description || ''
  }
  showEditDialog.value = true
}

const viewDetail = async (strategy: Strategy) => {
  try {
    const detail = await strategyApi.getDetail(strategy.id)
    currentDetail.value = detail
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('获取策略详情失败')
  }
}

const updateStrategy = async () => {
  if (!currentEditStrategy.value || !editForm.value.name) {
    ElMessage.warning('请填写完整信息')
    return
  }

  updating.value = true
  try {
    await strategyApi.update(currentEditStrategy.value.id, editForm.value)
    ElMessage.success('策略更新成功')
    showEditDialog.value = false
    loadStrategyList()
  } catch (error) {
    ElMessage.error('更新策略失败')
  } finally {
    updating.value = false
  }
}

const deleteStrategy = async (strategy: Strategy | null) => {
  if (!strategy) {
    strategy = currentEditStrategy.value
  }
  if (!strategy) return

  try {
    await ElMessageBox.confirm(
      `确定要删除策略"${strategy.name}"吗？删除后无法恢复。`,
      '确认删除',
      { type: 'warning' }
    )

    await strategyApi.delete(strategy.id)
    ElMessage.success('策略删除成功')
    showEditDialog.value = false
    loadStrategyList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除策略失败')
    }
  }
}

const startStrategy = async (strategy: Strategy) => {
  try {
    await strategyApi.start(strategy.id)
    ElMessage.success('策略已启动')
    currentDetail.value = { ...strategy, status: 'running' }
    loadStrategyList()
  } catch (error) {
    ElMessage.error('启动策略失败')
  }
}

const stopStrategy = async (strategy: Strategy) => {
  try {
    await strategyApi.stop(strategy.id)
    ElMessage.success('策略已停止')
    currentDetail.value = { ...strategy, status: 'stopped' }
    loadStrategyList()
  } catch (error) {
    ElMessage.error('停止策略失败')
  }
}

const goToBacktest = (strategy: Strategy) => {
  router.push('/backtest')
}

const getStrategyTypeLabel = (type: string) => {
  const item = STRATEGY_TYPES.find(t => t.value === type)
  return item?.label || type
}

onMounted(() => {
  loadStrategyList()
})
</script>

<style lang="scss" scoped>
@use '@/styles/design-system.scss' as *;

.strategy-page {
  --color-tech-blue: #5B8FF9;
  --color-vibrant-orange: #FF8C42;
  --color-success: #52C41A;
  --color-danger: #FF4D4F;

  padding: 20px;
  background: linear-gradient(135deg, #F7F9FC 0%, #EFF3F8 100%);
  min-height: 100vh;

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    margin-bottom: 24px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(91, 143, 249, 0.1);
    box-shadow: 0 2px 8px rgba(91, 143, 249, 0.08);

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    :deep(.el-button--primary) {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, #7AA5FF 100%);
      border: none;
      border-radius: 10px;
    }
  }

  .strategy-card {
    margin-bottom: 20px;
    border-radius: 16px;
    border: 2px solid rgba(91, 143, 249, 0.1);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(91, 143, 249, 0.15);
    }

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
        color: #5A5A5A;

        strong {
          color: #1A1A1A;
        }

        &.description {
          color: #8C8C8C;
          margin-top: 12px;
          padding: 8px;
          background: #F7F9FC;
          border-radius: 6px;
          border-left: 3px solid var(--color-tech-blue);
        }
      }

      .up {
        color: var(--color-danger);
        font-weight: 600;
      }

      .down {
        color: var(--color-success);
        font-weight: 600;
      }
    }

    .card-footer {
      display: flex;
      gap: 8px;

      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 12px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;

        &.detail-btn {
          background: rgba(91, 143, 249, 0.1);
          color: var(--color-tech-blue);

          &:hover {
            background: var(--color-tech-blue);
            color: white;
          }
        }

        &.edit-btn {
          background: rgba(255, 140, 66, 0.1);
          color: var(--color-vibrant-orange);

          &:hover {
            background: var(--color-vibrant-orange);
            color: white;
          }
        }
      }
    }
  }

  .empty-state {
    padding: 60px 0;
    background: white;
    border-radius: 16px;
    text-align: center;
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

    .detail-actions {
      margin-top: 20px;
      display: flex;
      gap: 12px;
    }
  }
}
</style>
