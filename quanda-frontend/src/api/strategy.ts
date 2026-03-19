import request from './request'
import type { Strategy, StrategyConfig, StrategyAnalysis } from '@/types/strategy'

export const strategyApi = {
  // 获取策略列表
  getList: async (skip: number = 0, limit: number = 20, keyword?: string, status?: string) => {
    const params: any = { skip, limit }
    if (keyword) params.keyword = keyword
    if (status) params.status = status

    const response = await request.get<any, { total: number; list: Strategy[] }>('/strategy/list', { params })
    return response
  },

  // 获取策略详情
  getDetail: async (id: string) => {
    const response = await request.get<any, Strategy>(`/strategy/${id}`)
    return response
  },

  // 获取策略代码
  getCode: async (id: string) => {
    const response = await request.get<any, { code: string; name: string }>(`/strategy/${id}/code`)
    return response
  },

  // 更新策略代码
  updateCode: async (id: string, code: string) => {
    const response = await request.put<any, null>(`/strategy/${id}/code`, { code })
    return response
  },

  // 创建策略
  create: async (data: StrategyConfig) => {
    const response = await request.post<any, Strategy>('/strategy/create', data)
    return response
  },

  // 更新策略
  update: async (id: string, data: Partial<Strategy>) => {
    const response = await request.put<any, Strategy>(`/strategy/${id}`, data)
    return response
  },

  // 删除策略
  delete: async (id: string) => {
    const response = await request.delete<any, null>(`/strategy/${id}`)
    return response
  },

  // 启动策略
  start: async (id: string) => {
    const response = await request.post<any, { strategy_id: string; status: string }>(`/strategy/${id}/start`)
    return response
  },

  // 停止策略
  stop: async (id: string) => {
    const response = await request.post<any, { strategy_id: string; status: string }>(`/strategy/${id}/stop`)
    return response
  },

  // 分析策略代码
  analyze: async (code: string) => {
    const response = await request.post<any, StrategyAnalysis>('/strategy/analyze', { code })
    return response
  }
}
