<template>
  <el-select
    v-model="selectedFuture"
    placeholder="选择期货合约"
    filterable
    @change="handleChange"
    class="future-selector"
  >
    <el-option
      v-for="future in marketStore.futureList"
      :key="future"
      :label="future"
      :value="future"
    />
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useMarketStore } from '@/stores/market'

interface Emits {
  (e: 'change', value: string): void
}

const emit = defineEmits<Emits>()

const marketStore = useMarketStore()
const selectedFuture = ref('IF2512')  // 默认值，立即设置

const handleChange = (value: string) => {
  emit('change', value)
}

// 组件挂载时立即触发一次
onMounted(() => {
  emit('change', selectedFuture.value)
  // 异步加载期货列表
  marketStore.fetchFutureList()
})

watch(() => marketStore.futureList, (newList) => {
  // 当列表加载完成后，如果默认值不在列表中，则使用第一个
  if (newList.length > 0 && !newList.includes(selectedFuture.value)) {
    selectedFuture.value = newList[0]
    emit('change', selectedFuture.value)
  }
})
</script>

<style lang="scss" scoped>
.future-selector {
  width: 200px;
}
</style>
