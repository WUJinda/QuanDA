<template>
  <el-popover
    placement="bottom-start"
    :width="480"
    trigger="click"
    v-model:visible="popoverVisible"
    popper-class="future-selector-popover"
  >
    <template #reference>
      <div class="future-selector-trigger" :class="{ 'is-active': popoverVisible }">
        <span class="selected-code">{{ selectedFuture || '选择合约' }}</span>
        <el-icon class="arrow-icon"><ArrowDown /></el-icon>
      </div>
    </template>

    <div class="future-selector-panel">
      <!-- 搜索框 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索合约/品种..."
          prefix-icon="Search"
          clearable
          size="default"
          class="search-input"
        />
      </div>

      <!-- 最近使用 -->
      <div class="recent-section" v-if="recentUsed.length > 0 && !searchKeyword">
        <div class="section-title">
          <el-icon><Clock /></el-icon>
          最近使用
        </div>
        <div class="recent-tags">
          <el-tag
            v-for="code in recentUsed.slice(0, 6)"
            :key="code"
            class="recent-tag"
            @click="selectContract(code)"
          >
            {{ code }}
          </el-tag>
        </div>
      </div>

      <!-- 分类选择 -->
      <div class="category-section" v-if="!searchKeyword">
        <el-tabs v-model="activeExchange" type="card" class="exchange-tabs">
          <el-tab-pane
            v-for="category in categories"
            :key="category.exchange"
            :label="category.name"
            :name="category.exchange"
          >
            <div class="product-grid">
              <div
                v-for="product in category.products"
                :key="product.code"
                class="product-item"
                :class="{ 'is-selected': selectedProduct === product.code }"
                @click="selectProduct(product.code)"
              >
                <span class="product-code">{{ product.code }}</span>
                <span class="product-name">{{ product.name }}</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 搜索结果 / 合约列表 -->
      <div class="contract-section">
        <div class="section-title" v-if="!searchKeyword && selectedProduct">
          <el-icon><Document /></el-icon>
          {{ getProductName(selectedProduct) }} 合约
        </div>
        <div class="section-title" v-else-if="searchKeyword">
          <el-icon><Search /></el-icon>
          搜索结果
        </div>
        <div class="contract-list" v-if="filteredContracts.length > 0">
          <div
            v-for="contract in filteredContracts"
            :key="contract"
            class="contract-item"
            :class="{ 'is-selected': selectedFuture === contract }"
            @click="selectContract(contract)"
          >
            <span class="contract-code">{{ contract }}</span>
            <el-icon v-if="selectedFuture === contract" class="check-icon"><Check /></el-icon>
          </div>
          <!-- 更多结果提示 -->
          <div v-if="hasMoreResults" class="more-results-tip">
            仅显示前 {{ SEARCH_LIMIT }} 条结果，请输入更精确的关键词
          </div>
        </div>
        <div class="empty-result" v-else-if="searchKeyword">
          <el-icon><Warning /></el-icon>
          <span>未找到匹配的合约</span>
        </div>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useMarketStore } from '@/stores/market'
import { ArrowDown, Clock, Document, Search, Check, Warning } from '@element-plus/icons-vue'

interface Emits {
  (e: 'change', value: string): void
}

const emit = defineEmits<Emits>()
const marketStore = useMarketStore()

const popoverVisible = ref(false)
const searchKeyword = ref('')
const activeExchange = ref('SHFE')
const selectedProduct = ref('')
const selectedFuture = ref('IF2512')
const recentUsed = ref<string[]>([])

// localStorage 配置
const STORAGE_KEY = 'future_recent_used'
const STORAGE_VERSION = 1

// 从 localStorage 加载最近使用
const loadRecentUsed = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const data = JSON.parse(saved)
      // 版本检查，防止数据格式变更导致解析错误
      if (data.version === STORAGE_VERSION && Array.isArray(data.items)) {
        recentUsed.value = data.items
      } else {
        // 版本不匹配，重置数据
        recentUsed.value = []
      }
    }
  } catch {
    recentUsed.value = []
  }
}

// 保存最近使用
const saveRecentUsed = (code: string) => {
  const index = recentUsed.value.indexOf(code)
  if (index > -1) {
    recentUsed.value.splice(index, 1)
  }
  recentUsed.value.unshift(code)
  recentUsed.value = recentUsed.value.slice(0, 10)
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    version: STORAGE_VERSION,
    items: recentUsed.value
  }))
}

// 品种分类
const categories = computed(() => marketStore.futureCategories)

// 当前分类的品种
const currentCategoryProducts = computed(() => {
  const category = categories.value.find(c => c.exchange === activeExchange.value)
  return category?.products || []
})

// 获取品种名称
const getProductName = (productCode: string) => {
  for (const category of categories.value) {
    const product = category.products.find(p => p.code === productCode)
    if (product) return product.name
  }
  return productCode
}

// 搜索结果限制
const SEARCH_LIMIT = 50

// 过滤的合约列表
const filteredContracts = computed(() => {
  const allContracts = marketStore.futureList

  if (searchKeyword.value) {
    // 搜索模式：匹配合约代码或品种
    const keyword = searchKeyword.value.toUpperCase()
    return allContracts.filter(contract => {
      // 直接匹配合约代码（忽略大小写）
      if (contract.toUpperCase().includes(keyword)) return true
      // 匹配品种名称
      for (const category of categories.value) {
        for (const product of category.products) {
          if (product.code.toUpperCase().includes(keyword) ||
              product.name.includes(keyword)) {
            // 如果品种匹配，返回该品种的所有合约（忽略大小写）
            if (contract.toUpperCase().startsWith(product.code.toUpperCase())) return true
          }
        }
      }
      return false
    }).slice(0, SEARCH_LIMIT)
  }

  // 非搜索模式：显示选中品种的合约（忽略大小写）
  if (selectedProduct.value) {
    const productCode = selectedProduct.value.toUpperCase()
    return allContracts.filter(c => c.toUpperCase().startsWith(productCode))
  }

  return []
})

// 是否有更多搜索结果
const hasMoreResults = computed(() => {
  if (!searchKeyword.value) return false
  const allContracts = marketStore.futureList
  const keyword = searchKeyword.value.toUpperCase()
  const total = allContracts.filter(contract => {
    if (contract.toUpperCase().includes(keyword)) return true
    for (const category of categories.value) {
      for (const product of category.products) {
        if (product.code.toUpperCase().includes(keyword) ||
            product.name.includes(keyword)) {
          if (contract.toUpperCase().startsWith(product.code.toUpperCase())) return true
        }
      }
    }
    return false
  }).length
  return total > SEARCH_LIMIT
})

// 选择品种
const selectProduct = (code: string) => {
  selectedProduct.value = code
}

// 选择合约
const selectContract = (code: string) => {
  selectedFuture.value = code
  saveRecentUsed(code)
  emit('change', code)
  popoverVisible.value = false
}

// 监听合约列表变化，设置默认值
watch(() => marketStore.futureList, (newList) => {
  if (newList.length > 0 && !newList.includes(selectedFuture.value)) {
    selectedFuture.value = newList[0]
    emit('change', selectedFuture.value)
  }
}, { immediate: true })

onMounted(async () => {
  loadRecentUsed()
  // 加载品种分类
  if (marketStore.futureCategories.length === 0) {
    await marketStore.fetchFutureCategories()
  }
  // 加载合约列表
  if (marketStore.futureList.length === 0) {
    await marketStore.fetchFutureList()
  }
  // 初始触发
  emit('change', selectedFuture.value)
})
</script>

<style lang="scss" scoped>
.future-selector-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  min-width: 140px;
  transition: all 0.2s;

  &:hover {
    border-color: #409eff;
  }

  &.is-active {
    border-color: #409eff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  }

  .selected-code {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
  }

  .arrow-icon {
    margin-left: auto;
    color: #909399;
    transition: transform 0.2s;
  }

  &.is-active .arrow-icon {
    transform: rotate(180deg);
  }
}

.future-selector-panel {
  max-height: 450px;
  overflow-y: auto;

  .search-section {
    margin-bottom: 12px;

    .search-input {
      width: 100%;
    }
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #909399;
    margin-bottom: 8px;
  }

  .recent-section {
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;

    .recent-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .recent-tag {
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #409eff;
          color: #fff;
          border-color: #409eff;
        }
      }
    }
  }

  .category-section {
    margin-bottom: 12px;

    .exchange-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 8px;
      }

      :deep(.el-tabs__item) {
        padding: 0 12px;
        height: 28px;
        line-height: 28px;
        font-size: 12px;
      }
    }

    .product-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 6px;
      max-height: 120px;
      overflow-y: auto;

      .product-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 6px 4px;
        background: #f5f7fa;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #ecf5ff;
        }

        &.is-selected {
          background: #409eff;

          .product-code,
          .product-name {
            color: #fff;
          }
        }

        .product-code {
          font-size: 13px;
          font-weight: 600;
          color: #303133;
        }

        .product-name {
          font-size: 10px;
          color: #909399;
          margin-top: 2px;
        }
      }
    }
  }

  .contract-section {
    .contract-list {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      max-height: 150px;
      overflow-y: auto;

      .contract-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        background: #f5f7fa;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #ecf5ff;
        }

        &.is-selected {
          background: #409eff;

          .contract-code {
            color: #fff;
          }
        }

        .contract-code {
          font-size: 12px;
          font-weight: 500;
          color: #303133;
        }

        .check-icon {
          color: #fff;
          font-size: 12px;
        }
      }
    }

    .more-results-tip {
      grid-column: 1 / -1;
      padding: 8px;
      text-align: center;
      font-size: 11px;
      color: #909399;
      background: #fafafa;
      border-radius: 4px;
    }

    .empty-result {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 20px;
      color: #909399;
      font-size: 13px;
    }
  }
}
</style>

<style lang="scss">
// 全局样式 - popover
.future-selector-popover {
  padding: 12px !important;
}
</style>
