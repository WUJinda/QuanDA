<template>
  <div class="future-selector-inline">
    <!-- 一级页签：交易所 -->
    <div class="exchange-tabs">
      <div
        v-for="category in categories"
        :key="category.exchange"
        class="exchange-tab"
        :class="{ 'is-active': activeExchange === category.exchange }"
        @click="selectExchange(category.exchange)"
      >
        {{ category.name }}
      </div>
    </div>

    <!-- 二级标签：品种 -->
    <div class="product-tabs" v-if="currentProducts.length > 0">
      <div class="product-tabs-wrapper">
        <div
          v-for="product in currentProducts"
          :key="product.code"
          class="product-tab"
          :class="{ 'is-active': selectedProduct === product.code }"
          @click="selectProduct(product.code)"
          :title="product.name"
        >
          {{ product.code }}
        </div>
      </div>
    </div>

    <!-- 合约列表 -->
    <div class="contract-section" v-if="selectedProduct">
      <div class="contract-grid">
        <div
          v-for="contract in filteredContracts"
          :key="contract"
          class="contract-item"
          :class="{ 'is-selected': selectedFuture === contract }"
          @click="selectContract(contract)"
        >
          {{ contract }}
        </div>
      </div>
      <div class="empty-contracts" v-if="filteredContracts.length === 0">
        暂无合约
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useMarketStore } from '@/stores/market'

interface Emits {
  (e: 'change', value: string): void
}

const emit = defineEmits<Emits>()
const marketStore = useMarketStore()

const activeExchange = ref('SHFE')
const selectedProduct = ref('')
const selectedFuture = ref('')

// localStorage 配置
const EXCHANGE_STORAGE_KEY = 'future_last_exchange'
const PRODUCT_STORAGE_KEY = 'future_last_product'

// 加载上次选择
const loadLastSelection = () => {
  const lastExchange = localStorage.getItem(EXCHANGE_STORAGE_KEY)
  const lastProduct = localStorage.getItem(PRODUCT_STORAGE_KEY)
  if (lastExchange) {
    activeExchange.value = lastExchange
  }
  if (lastProduct) {
    selectedProduct.value = lastProduct
  }
}

// 保存选择
const saveLastSelection = () => {
  localStorage.setItem(EXCHANGE_STORAGE_KEY, activeExchange.value)
  localStorage.setItem(PRODUCT_STORAGE_KEY, selectedProduct.value)
}

// 品种分类
const categories = computed(() => marketStore.futureCategories)

// 当前交易所的品种列表
const currentProducts = computed(() => {
  const category = categories.value.find(c => c.exchange === activeExchange.value)
  return category?.products || []
})

// 过滤的合约列表
const filteredContracts = computed(() => {
  const allContracts = marketStore.futureList
  if (!selectedProduct.value) return []

  const productCode = selectedProduct.value.toUpperCase()
  return allContracts.filter(c => c.toUpperCase().startsWith(productCode))
})

// 选择交易所
const selectExchange = (exchange: string) => {
  activeExchange.value = exchange
  const category = categories.value.find(c => c.exchange === exchange)
  if (category && category.products.length > 0) {
    selectedProduct.value = category.products[0].code
  } else {
    selectedProduct.value = ''
  }
  saveLastSelection()
}

// 选择品种
const selectProduct = (code: string) => {
  selectedProduct.value = code
  saveLastSelection()
}

// 选择合约
const selectContract = (code: string) => {
  selectedFuture.value = code
  emit('change', code)
}

// 监听合约列表变化，设置默认值
watch(() => marketStore.futureList, (newList) => {
  if (newList.length > 0 && !selectedFuture.value) {
    selectedFuture.value = newList[0]
    emit('change', selectedFuture.value)
  }
}, { immediate: true })

// 监听品种列表变化
watch(currentProducts, (products) => {
  if (products.length > 0 && !selectedProduct.value) {
    loadLastSelection()
    const exists = products.some(p => p.code === selectedProduct.value)
    if (!exists) {
      selectedProduct.value = products[0].code
    }
  }
}, { immediate: true })

onMounted(async () => {
  loadLastSelection()
  if (marketStore.futureCategories.length === 0) {
    await marketStore.fetchFutureCategories()
  }
  if (marketStore.futureList.length === 0) {
    await marketStore.fetchFutureList()
  }
})
</script>

<style lang="scss" scoped>
.future-selector-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  // 一级页签：交易所
  .exchange-tabs {
    display: flex;
    gap: 2px;
    background: #f5f7fa;
    padding: 2px;
    border-radius: 4px;

    .exchange-tab {
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 500;
      color: #606266;
      border-radius: 3px;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;

      &:hover {
        color: #409eff;
      }

      &.is-active {
        background: #fff;
        color: #409eff;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      }
    }
  }

  // 二级标签：品种
  .product-tabs {
    .product-tabs-wrapper {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }

    .product-tab {
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 500;
      color: #606266;
      background: #f5f7fa;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: #ecf5ff;
        color: #409eff;
      }

      &.is-active {
        background: #409eff;
        color: #fff;
      }
    }
  }

  // 合约列表
  .contract-section {
    .contract-grid {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }

    .contract-item {
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 500;
      color: #606266;
      background: #f5f7fa;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      font-family: 'Consolas', 'Monaco', monospace;

      &:hover {
        background: #ecf5ff;
        color: #409eff;
      }

      &.is-selected {
        background: #409eff;
        color: #fff;
      }
    }

    .empty-contracts {
      font-size: 12px;
      color: #909399;
      padding: 4px 10px;
    }
  }
}
</style>
