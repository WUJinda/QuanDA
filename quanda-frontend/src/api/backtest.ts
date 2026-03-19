import request from './request'
import type { BacktestTask, BacktestResult, BacktestConfig } from '@/types/backtest'

export const backtestApi = {
  // 获取回测任务列表
  getList: async (skip: number = 0, limit: number = 20) => {
    const response = await request.get<any, { total: number; list: BacktestTask[] }>('/backtest/list', {
      params: { skip, limit }
    })
    return response
  },

  // 获取回测任务详情
  getDetail: async (id: string) => {
    const response = await request.get<any, BacktestTask>(`/backtest/${id}`)
    return response
  },

  // 创建回测任务
  create: async (data: BacktestConfig) => {
    const response = await request.post<any, { backtest_id: string }>('/backtest/create', data)
    return response
  },

  // 运行回测任务
  run: async (id: string) => {
    const response = await request.post<any, { backtest_id: string }>(`/backtest/run/${id}`)
    return response
  },

  // 获取回测结果
  getResult: async (id: string) => {
    const response = await request.get<any, BacktestResult>(`/backtest/result/${id}`)
    return response
  },

  // 删除回测任务
  delete: async (id: string) => {
    const response = await request.delete<any, null>(`/backtest/${id}`)
    return response
  },

  // WebSocket 连接用于实时输出
  getWebSocketUrl: (id: string) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = '8010' // QuanDA 后端端口
    return `${protocol}//${host}:${port}/api/backtest/ws/${id}`
  },

  // 创建 WebSocket 连接
  createWebSocket: (id: string, onMessage: (data: any) => void, onError?: (error: Event) => void) => {
    const ws = new WebSocket(backtestApi.getWebSocketUrl(id))

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (e) {
        console.error('WebSocket 消息解析错误:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      if (onError) onError(error)
    }

    return ws
  }
}

// WebSocket 消息类型
export type WSMessageType = 'status' | 'progress' | 'completed' | 'error' | 'started'

export interface WSMessage {
  type: WSMessageType
  progress?: number
  message?: string
  result?: BacktestResult
  data?: any
  timestamp?: string
}
