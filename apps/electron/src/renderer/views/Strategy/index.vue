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
@use '@/styles/design-system.scss' as *;

.strategy-page {
  /* 双主色设计系统 - 科技蓝 + 活力橙 */
  --color-tech-blue: #5B8FF9;
  --color-tech-blue-light: #7AA5FF;
  --color-tech-blue-lighter: #A3C0FF;
  --color-vibrant-orange: #FF8C42;
  --color-vibrant-orange-light: #FFA666;
  --color-vibrant-orange-lighter: #FFBF8A;
  
  --color-success: #52C41A;
  --color-danger: #FF4D4F;
  --color-warning: #FAAD14;
  --color-purple: #9254DE;
  
  --color-bg: #FFFFFF;
  --color-bg-light: #F7F9FC;
  --color-bg-lighter: #EFF3F8;
  --color-text: #1A1A1A;
  --color-text-secondary: #5A5A5A;
  --color-text-tertiary: #8C8C8C;
  --color-border: #E5E8EF;
  --color-border-light: #F0F2F7;
  
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  
  --shadow-sm: 0 2px 8px rgba(91, 143, 249, 0.08);
  --shadow-md: 0 4px 16px rgba(91, 143, 249, 0.12);
  --shadow-lg: 0 8px 24px rgba(91, 143, 249, 0.16);
  --shadow-hover: 0 12px 32px rgba(91, 143, 249, 0.20);
  
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #F7F9FC 0%, #EFF3F8 100%);
  min-height: 100vh;

  /* 工具栏 - 毛玻璃效果 */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: var(--radius-xl);
    border: 1px solid rgba(91, 143, 249, 0.1);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      box-shadow: var(--shadow-md);
      border-color: rgba(91, 143, 249, 0.2);
    }

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }

    /* 主按钮样式 - 科技蓝渐变 */
    :deep(.el-button--primary) {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
      border: none;
      border-radius: var(--radius-md);
      padding: 10px 20px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(91, 143, 249, 0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(91, 143, 249, 0.4);
      }

      &:active {
        transform: translateY(0);
      }
    }

    /* 次要按钮 - 活力橙边框 */
    :deep(.el-button:not(.el-button--primary)) {
      background: white;
      border: 2px solid var(--color-vibrant-orange);
      color: var(--color-vibrant-orange);
      border-radius: var(--radius-md);
      padding: 8px 18px;
      font-weight: 600;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: linear-gradient(135deg, rgba(255, 140, 66, 0.1) 0%, rgba(255, 166, 102, 0.05) 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.25);
      }
    }

    /* 搜索框 */
    :deep(.el-input) {
      .el-input__wrapper {
        border-radius: var(--radius-md);
        border: 2px solid var(--color-border);
        background: white;
        box-shadow: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          border-color: var(--color-tech-blue-light);
        }

        &.is-focus {
          border-color: var(--color-tech-blue);
          box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
        }
      }

      .el-input__prefix {
        color: var(--color-tech-blue);
      }
    }
  }

  /* 卡片网格布局 */
  :deep(.el-row) {
    margin-left: -10px !important;
    margin-right: -10px !important;

    .el-col {
      padding-left: 10px !important;
      padding-right: 10px !important;
    }
  }

  /* 策略卡片 - 现代科技感设计 */
  .strategy-card {
    margin-bottom: 20px;
    border-radius: var(--radius-xl);
    border: 2px solid var(--color-border-light);
    background: white;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;

    /* 顶部装饰条 - 渐变 */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    &:hover {
      transform: translateY(-8px) scale(1.02);
      box-shadow: var(--shadow-hover);
      border-color: var(--color-tech-blue-lighter);

      &::before {
        opacity: 1;
      }

      .card-header .strategy-name {
        background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    /* 卡片头部 */
    :deep(.el-card__header) {
      padding: var(--spacing-lg);
      background: linear-gradient(135deg, rgba(91, 143, 249, 0.03) 0%, rgba(255, 140, 66, 0.02) 100%);
      border-bottom: 2px solid var(--color-border-light);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .strategy-name {
          font-size: 18px;
          font-weight: 700;
          color: var(--color-text);
          letter-spacing: -0.3px;
          transition: all 0.3s ease;
        }

        /* 状态标签 */
        .el-tag {
          border-radius: var(--radius-sm);
          padding: 4px 12px;
          font-weight: 600;
          font-size: 12px;
          border: none;

          &.el-tag--success {
            background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(82, 196, 26, 0.3);
          }

          &.el-tag--info {
            background: linear-gradient(135deg, #8C8C8C 0%, #BFBFBF 100%);
            color: white;
          }
        }
      }
    }

    /* 卡片内容 */
    :deep(.el-card__body) {
      padding: var(--spacing-lg);

      .strategy-info {
        p {
          margin: 10px 0;
          font-size: 14px;
          color: var(--color-text-secondary);
          line-height: 1.6;
          display: flex;
          align-items: center;

          &.description {
            color: var(--color-text-tertiary);
            margin-top: var(--spacing-md);
            padding: var(--spacing-sm);
            background: var(--color-bg-light);
            border-radius: var(--radius-sm);
            border-left: 3px solid var(--color-tech-blue);
            display: block;
          }

          strong {
            color: var(--color-text);
            font-weight: 600;
            margin-right: 8px;
            min-width: 80px;
          }

          /* 图标装饰 */
          &::before {
            content: '●';
            color: var(--color-tech-blue);
            margin-right: 8px;
            font-size: 8px;
          }

          &.description::before {
            display: none;
          }
        }

        .up {
          color: var(--color-danger);
          font-weight: 700;
          font-size: 16px;
          padding: 2px 8px;
          background: linear-gradient(135deg, rgba(255, 77, 79, 0.1) 0%, rgba(255, 77, 79, 0.05) 100%);
          border-radius: var(--radius-sm);
        }

        .down {
          color: var(--color-success);
          font-weight: 700;
          font-size: 16px;
          padding: 2px 8px;
          background: linear-gradient(135deg, rgba(82, 196, 26, 0.1) 0%, rgba(82, 196, 26, 0.05) 100%);
          border-radius: var(--radius-sm);
        }
      }
    }

    /* 卡片底部操作区 */
    :deep(.el-card__footer) {
      padding: var(--spacing-md) var(--spacing-lg);
      background: linear-gradient(180deg, white 0%, var(--color-bg-light) 100%);
      border-top: 2px solid var(--color-border-light);

      .card-footer {
        display: flex;
        gap: var(--spacing-sm);

        .action-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 10px 16px;
          border: none;
          border-radius: var(--radius-md);
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;

          .el-icon {
            font-size: 16px;
            transition: transform 0.3s ease;
          }

          /* 按钮光泽效果 */
          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s ease;
          }

          &:hover::before {
            left: 100%;
          }

          &.detail-btn {
            background: linear-gradient(135deg, rgba(91, 143, 249, 0.12) 0%, rgba(91, 143, 249, 0.06) 100%);
            color: var(--color-tech-blue);
            border: 2px solid rgba(91, 143, 249, 0.2);

            &:hover {
              background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
              color: white;
              transform: translateY(-2px);
              box-shadow: 0 6px 16px rgba(91, 143, 249, 0.35);

              .el-icon {
                transform: scale(1.1);
              }
            }

            &:active {
              transform: translateY(0);
            }
          }

          &.edit-btn {
            background: linear-gradient(135deg, rgba(255, 140, 66, 0.12) 0%, rgba(255, 140, 66, 0.06) 100%);
            color: var(--color-vibrant-orange);
            border: 2px solid rgba(255, 140, 66, 0.2);

            &:hover {
              background: linear-gradient(135deg, var(--color-vibrant-orange) 0%, var(--color-vibrant-orange-light) 100%);
              color: white;
              transform: translateY(-2px);
              box-shadow: 0 6px 16px rgba(255, 140, 66, 0.35);

              .el-icon {
                transform: scale(1.1);
              }
            }

            &:active {
              transform: translateY(0);
            }
          }
        }
      }
    }
  }

  /* 详情内容样式 */
  .detail-content {
    .profit-up {
      color: var(--color-danger);
      font-weight: 700;
      font-size: 18px;
    }

    .profit-down {
      color: var(--color-success);
      font-weight: 700;
      font-size: 18px;
    }

    :deep(.el-descriptions) {
      .el-descriptions__label {
        font-weight: 600;
        color: var(--color-text);
        background: var(--color-bg-light);
      }

      .el-descriptions__content {
        color: var(--color-text-secondary);
      }
    }
  }
}

/* 对话框全局样式优化 */
:deep(.el-dialog) {
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(91, 143, 249, 0.1);
  overflow: hidden;

  .el-dialog__header {
    padding: var(--spacing-lg) var(--spacing-xl);
    background: linear-gradient(135deg, rgba(91, 143, 249, 0.05) 0%, rgba(255, 140, 66, 0.03) 100%);
    border-bottom: 2px solid var(--color-border-light);

    .el-dialog__title {
      font-size: 20px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-vibrant-orange) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .el-dialog__headerbtn {
      top: var(--spacing-lg);
      right: var(--spacing-lg);
      width: 36px;
      height: 36px;
      border-radius: var(--radius-md);
      transition: all 0.3s ease;

      &:hover {
        background: rgba(255, 77, 79, 0.1);

        .el-dialog__close {
          color: var(--color-danger);
        }
      }
    }
  }

  .el-dialog__body {
    padding: var(--spacing-xl);
  }

  .el-dialog__footer {
    padding: var(--spacing-lg) var(--spacing-xl);
    background: var(--color-bg-light);
    border-top: 2px solid var(--color-border-light);

    .el-button {
      border-radius: var(--radius-md);
      padding: 10px 24px;
      font-weight: 600;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        transform: translateY(-2px);
      }
    }

    .el-button--primary {
      background: linear-gradient(135deg, var(--color-tech-blue) 0%, var(--color-tech-blue-light) 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(91, 143, 249, 0.3);

      &:hover {
        box-shadow: 0 6px 20px rgba(91, 143, 249, 0.4);
      }
    }

    .el-button--danger {
      background: linear-gradient(135deg, var(--color-danger) 0%, #FF7875 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);

      &:hover {
        box-shadow: 0 6px 20px rgba(255, 77, 79, 0.4);
      }
    }
  }

  /* 表单样式 */
  .el-form {
    .el-form-item__label {
      font-weight: 600;
      color: var(--color-text);
    }

    .el-input__wrapper {
      border-radius: var(--radius-md);
      border: 2px solid var(--color-border);
      box-shadow: none;
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--color-tech-blue-light);
      }

      &.is-focus {
        border-color: var(--color-tech-blue);
        box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
      }
    }

    .el-select .el-input__wrapper {
      &.is-focus {
        border-color: var(--color-tech-blue);
      }
    }

    .el-textarea__inner {
      border-radius: var(--radius-md);
      border: 2px solid var(--color-border);
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--color-tech-blue-light);
      }

      &:focus {
        border-color: var(--color-tech-blue);
        box-shadow: 0 0 0 3px rgba(91, 143, 249, 0.1);
      }
    }
  }
}

/* 动画效果 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.strategy-card {
  animation: slideInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) backwards;

  @for $i from 1 through 12 {
    &:nth-child(#{$i}) {
      animation-delay: #{$i * 0.05}s;
    }
  }
}
</style>
