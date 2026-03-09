import request from './request'
import type { StrategyReference, StrategyReferenceFilter } from '@/types/strategy-reference'

export const strategyReferenceApi = {
  // 获取策略参考列表
  getList: (filter?: StrategyReferenceFilter) => {
    return request.get<any, StrategyReference[]>('/strategy-reference/list', {
      params: filter
    })
  },

  // 获取策略参考详情
  getDetail: (id: string) => {
    return request.get<any, StrategyReference>(`/strategy-reference/${id}`)
  },

  // 创建策略参考
  create: (data: Partial<StrategyReference>) => {
    return request.post('/strategy-reference/create', data)
  },

  // 更新策略参考
  update: (id: string, data: Partial<StrategyReference>) => {
    return request.put(`/strategy-reference/${id}`, data)
  },

  // 删除策略参考
  delete: (id: string) => {
    return request.delete(`/strategy-reference/${id}`)
  },

  // 上传截图
  uploadImage: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, { url: string }>('/strategy-reference/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 分析K线区间
  analyzeSegment: (code: string, start: string, end: string, frequence: string) => {
    return request.post('/strategy-reference/analyze', {
      code,
      start,
      end,
      frequence
    })
  }
}
