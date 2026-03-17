import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isCollapse = ref(false)
  const loading = ref(false)

  const toggleSidebar = () => {
    isCollapse.value = !isCollapse.value
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const init = async () => {
    // 初始化应用配置
    console.log('QuanDA Frontend Initialized')
  }

  return {
    isCollapse,
    loading,
    toggleSidebar,
    setLoading,
    init
  }
})
