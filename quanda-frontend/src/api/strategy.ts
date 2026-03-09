import request from './request'
import type { Strategy, StrategyConfig } from '@/types/strategy'

export const strategyApi = {
  // 获取策略列表
  getList: () => {
    return request.get<any, Strategy[]>('/strategy/list')
  },

  // 获取策略详情
  getDetail: (id: number) => {
    return request.get<any, Strategy>(`/strategy/${id}`)
  },

  // 创建策略
  create: (data: StrategyConfig) => {
    return request.post('/strategy/create', data)
  },

  // 更新策略
  update: (id: number, data: Partial<Strategy>) => {
    return request.put(`/strategy/${id}`, data)
  },

  // 删除策略
  delete: (id: number) => {
    return request.delete(`/strategy/${id}`)
  },

  // 获取策略的回测历史
  getBacktestHistory: (id: number) => {
    return request.get(`/strategy/${id}/backtest-history`)
  },

  // 启动策略
  start: (id: number) => {
    return request.post(`/strategy/${id}/start`)
  },

  // 停止策略
  stop: (id: number) => {
    return request.post(`/strategy/${id}/stop`)
  }
}
