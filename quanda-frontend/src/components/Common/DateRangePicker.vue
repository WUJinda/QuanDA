<template>
  <el-date-picker
    v-model="dateRange"
    type="daterange"
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
    format="YYYY-MM-DD"
    value-format="YYYY-MM-DD"
    @change="handleChange"
    class="date-range-picker"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import dayjs from 'dayjs'

interface Emits {
  (e: 'change', start: string, end: string): void
}

const emit = defineEmits<Emits>()

const dateRange = ref<[string, string]>([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

const handleChange = (value: [string, string] | null) => {
  if (value) {
    emit('change', value[0], value[1])
  }
}

// 初始化时触发一次
handleChange(dateRange.value)
</script>

<style lang="scss" scoped>
.date-range-picker {
  width: 280px;
}
</style>
