import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketApi } from '@/api/market'
import type { FutureData, RealtimeData, FutureCategory } from '@/types/market'

export const useMarketStore = defineStore('market', () => {
  const futureList = ref<string[]>([])
  const currentFuture = ref<string>('')
  const futureData = ref<FutureData[]>([])
  const realtimeData = ref<RealtimeData | null>(null)
  const futureCategories = ref<FutureCategory[]>([])

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

  const fetchFutureCategories = async () => {
    try {
      const data = await marketApi.getFutureCategory()
      futureCategories.value = data
      return data
    } catch (error) {
      console.error('获取品种分类失败:', error)
      return []
    }
  }

  // 数据缓存
  const dataCache = ref<Map<string, { data: FutureData[], timestamp: number }>>(new Map())
  const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

  const fetchFutureData = async (code: string, start: string, end: string, frequence: string = 'day', limit?: number) => {
    try {
      // 生成缓存key
      const cacheKey = `${code}_${start}_${end}_${frequence}_${limit || ''}`
      
      // 检查缓存
      const cached = dataCache.value.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        futureData.value = cached.data
        return cached.data
      }
      
      let data: FutureData[]
      
      // 根据周期类型调用不同的 API
      if (frequence === 'day' || frequence === 'week' || frequence === 'month') {
        data = await marketApi.getFutureDay(code, start, end, frequence, limit)
      } else {
        // 分钟数据，默认限制2000条
        data = await marketApi.getFutureMin(code, start, end, frequence, limit || 2000)
      }
      
      // 更新缓存
      dataCache.value.set(cacheKey, { data, timestamp: Date.now() })
      
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
    futureCategories,
    fetchFutureList,
    fetchFutureCategories,
    fetchFutureData,
    fetchRealtimeData
  }
})
