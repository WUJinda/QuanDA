import request from './request'
import type { StrategyReference, StrategyReferenceFilter } from '@/types/strategy-reference'

export const strategyReferenceApi = {
  // 获取策略参考列表
  getList: async (filter?: StrategyReferenceFilter) => {
    const response = await request.get<StrategyReference[]>('/strategy-reference/list', {
      params: filter
    })
    return response?.data || []
  },

  // 获取策略参考详情
  getDetail: async (id: string) => {
    const response = await request.get<StrategyReference>(`/strategy-reference/${id}`)
    return response?.data || null
  },

  // 创建策略参考
  create: async (data: Partial<StrategyReference>) => {
    const response = await request.post('/strategy-reference/create', data)
    return response?.data || null
  },

  // 更新策略参考
  update: async (id: string, data: Partial<StrategyReference>) => {
    const response = await request.put(`/strategy-reference/update/${id}`, data)
    return response?.data || null
  },

  // 删除策略参考
  delete: async (id: string) => {
    const response = await request.delete(`/strategy-reference/delete/${id}`)
    return response?.data || null
  },

  // 上传截图（使用原生方式，不经过拦截器）
  uploadImage: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await request.post<{ url: string }>('/strategy-reference/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response?.data || { url: '' }
  },

  // 分析K线区间
  analyzeSegment: async (code: string, start: string, end: string, frequence: string) => {
    const response = await request.post<any>('/strategy-reference/analyze', {
      code,
      start,
      end,
      frequence
    })
    return response?.data || null
  }
}
