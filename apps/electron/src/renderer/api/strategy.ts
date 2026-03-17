import request from './request'
import type { Strategy, StrategyConfig } from '@/types/strategy'

export const strategyApi = {
  // 获取策略列表
  getList: async () => {
    const response = await request.get<any, Strategy[]>('/strategy/list')
    return response?.data || []
  },

  // 获取策略详情
  getDetail: async (id: number) => {
    const response = await request.get<any, Strategy>(`/strategy/${id}`)
    return response?.data || null
  },

  // 创建策略
  create: async (data: StrategyConfig) => {
    const response = await request.post('/strategy/create', data)
    return response?.data || null
  },

  // 更新策略
  update: async (id: number, data: Partial<Strategy>) => {
    const response = await request.put(`/strategy/${id}`, data)
    return response?.data || null
  },

  // 删除策略
  delete: async (id: number) => {
    const response = await request.delete(`/strategy/${id}`)
    return response?.data || null
  },

  // 获取策略的回测历史
  getBacktestHistory: async (id: number) => {
    const response = await request.get(`/strategy/${id}/backtest-history`)
    return response?.data || []
  },

  // 启动策略
  start: async (id: number) => {
    const response = await request.post(`/strategy/${id}/start`)
    return response?.data || null
  },

  // 停止策略
  stop: async (id: number) => {
    const response = await request.post(`/strategy/${id}/stop`)
    return response?.data || null
  }
}
