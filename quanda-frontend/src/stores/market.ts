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

  const fetchFutureData = async (code: string, start: string, end: string) => {
    try {
      const data = await marketApi.getFutureDay(code, start, end)
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
