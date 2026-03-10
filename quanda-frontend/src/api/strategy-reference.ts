import request from './request'
import type { StrategyReference, StrategyReferenceFilter } from '@/types/strategy-reference'

export const strategyReferenceApi = {
  // 获取策略参考列表
  getList: async (filter?: StrategyReferenceFilter) => {
    const response = await request.get<StrategyReference[]>('/strategy-reference/list', {
      params: filter
    })
    return response || []
  },

  // 获取策略参考详情
  getDetail: async (id: string) => {
    const response = await request.get<StrategyReference>(`/strategy-reference/${id}`)
    return response || null
  },

  // 创建策略参考
  create: async (data: Partial<StrategyReference>) => {
    const response = await request.post('/strategy-reference/create', data)
    return response || null
  },

  // 更新策略参考
  update: async (id: string, data: Partial<StrategyReference>) => {
    const response = await request.put(`/strategy-reference/update/${id}`, data)
    return response || null
  },

  // 删除策略参考
  delete: async (id: string) => {
    const response = await request.delete(`/strategy-reference/delete/${id}`)
    return response || null
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
    return response || { url: '' }
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

      console.log('[analyzeSegment] 原始响应:', response)

      if (!response) {
        throw new Error('分析接口返回数据为空，请检查后端服务')
      }

      // 检查响应数据结构
      if (typeof response !== 'object') {
        console.error('[analyzeSegment] 响应不是对象:', typeof response)
        throw new Error('分析结果格式错误：响应不是对象类型')
      }

      if (!('pattern' in response)) {
        console.error('[analyzeSegment] 响应中缺少 pattern 字段，响应内容:', response)
        throw new Error('分析结果缺少 pattern 数据，可能是数据格式错误')
      }

      if (!response.pattern) {
        console.error('[analyzeSegment] pattern 字段为空:', response.pattern)
        throw new Error('pattern 数据为空')
      }

      console.log('[analyzeSegment] 分析成功:', response.pattern)
      return response
    } catch (error: any) {
      // 重新抛出错误，保留原始错误信息
      const errorMsg = error.message || '分析失败'
      console.error('[analyzeSegment] 分析失败:', errorMsg)
      throw new Error(errorMsg)
    }
  }
}
