import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketApi } from '@/api/market'
import type { FutureData, RealtimeData } from '@/types/market'

export const useMarketStore = defineStore('market', () => {
  const futureList = ref<string[]>([])
  const currentFuture = ref<string>('')
  const futureData = ref<FutureData[]>([])
  const realtimeData = ref<RealtimeData | null>(null)

  const fetchFutureList = async () => {
    try {
      const data = await marketApi.getFutureList()
      futureList.value = data
      if (data.length > 0) {
        currentFuture.value = data[0]
      }
    } catch (error) {
      console.error('获取期货列表失败:', error)
    }
  }

  const fetchFutureData = async (code: string, start: string, end: string, frequence: string = 'day') => {
    try {
      let data: FutureData[]
      
      // 根据周期类型调用不同的 API
      if (frequence === 'day' || frequence === 'week' || frequence === 'month') {
        data = await marketApi.getFutureDay(code, start, end, frequence)
      } else {
        // 分钟数据
        data = await marketApi.getFutureMin(code, start, end, frequence)
      }
      
      futureData.value = data
      return data
    } catch (error) {
      console.error('获取期货数据失败:', error)
      return []
    }
  }

  const fetchRealtimeData = async (code: string) => {
    try {
      const data = await marketApi.getFutureRealtime(code)
      realtimeData.value = data
      return data
    } catch (error) {
      console.error('获取实时数据失败:', error)
      return null
    }
  }

  return {
    futureList,
    currentFuture,
    futureData,
    realtimeData,
    fetchFutureList,
    fetchFutureData,
    fetchRealtimeData
  }
})
