<template>
  <el-select
    v-model="selectedFuture"
    placeholder="选择期货合约"
    filterable
    @change="handleChange"
    class="future-selector"
  >
    <el-option
      v-for="future in futureList"
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
const selectedFuture = ref('')
const futureList = ref<string[]>([])

const handleChange = (value: string) => {
  emit('change', value)
}

watch(() => marketStore.futureList, (newList) => {
  futureList.value = newList
  if (newList.length > 0 && !selectedFuture.value) {
    selectedFuture.value = newList[0]
    emit('change', selectedFuture.value)
  }
})

onMounted(async () => {
  await marketStore.fetchFutureList()
})
</script>

<style lang="scss" scoped>
.future-selector {
  width: 200px;
}
</style>
