<template>
  <el-select
    v-model="selectedAccount"
    placeholder="选择账户"
    filterable
    @change="handleChange"
    class="account-selector"
  >
    <el-option
      v-for="account in accountList"
      :key="account"
      :label="account"
      :value="account"
    />
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAccountStore } from '@/stores/account'

interface Emits {
  (e: 'change', value: string): void
}

const emit = defineEmits<Emits>()

const accountStore = useAccountStore()
const selectedAccount = ref('')
const accountList = ref<string[]>([])

const handleChange = (value: string) => {
  emit('change', value)
}

watch(() => accountStore.accountList, (newList) => {
  accountList.value = newList
  if (newList.length > 0 && !selectedAccount.value) {
    selectedAccount.value = newList[0]
    emit('change', selectedAccount.value)
  }
})

onMounted(async () => {
  await accountStore.fetchAccountList()
})
</script>

<style lang="scss" scoped>
.account-selector {
  width: 200px;
}
</style>
