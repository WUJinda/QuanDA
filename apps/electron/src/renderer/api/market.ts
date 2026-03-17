import request from './request'
import type { FutureData, RealtimeData } from '@/types/market'

export const marketApi = {
  // 获取期货列表
  getFutureList: () => {
    return request.get<any, string[]>('/future/list')
  },

  // 获取期货日线数据
  getFutureDay: (code: string, start: string, end: string, frequence = 'day', limit?: number) => {
    return request.get<any, FutureData[]>('/future/day', {
      params: { code, start, end, frequence, limit }
    })
  },

  // 获取期货分钟数据
  getFutureMin: (code: string, start: string, end: string, frequence = '1min', limit?: number) => {
    return request.get<any, FutureData[]>('/future/min', {
      params: { code, start, end, frequence, limit: limit || 2000 }
    })
  },

  // 获取期货实时数据
  getFutureRealtime: (code: string) => {
    return request.get<any, RealtimeData>('/future/realtime', {
      params: { code }
    })
  },

  // 获取期货交易数据
  getFutureTransaction: (code: string, start: string, end: string) => {
    return request.get('/future/transaction', {
      params: { code, start, end }
    })
  }
}
