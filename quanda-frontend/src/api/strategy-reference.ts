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
    try {
      const response = await request.post<any>('/strategy-reference/analyze', {
        code,
        start,
        end,
        frequence
      })
      
      if (!response) {
        throw new Error('分析接口返回数据为空，请检查后端服务')
      }
      
      if (!(response as any).pattern) {
        throw new Error('分析结果缺少 pattern 数据，可能是数据格式错误')
      }
      
      return response
    } catch (error: any) {
      // 重新抛出错误，保留原始错误信息
      const errorMsg = error.message || '分析失败'
      throw new Error(errorMsg)
    }
  }
}
