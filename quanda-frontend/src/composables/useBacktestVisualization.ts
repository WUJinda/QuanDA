// 回测可视化逻辑
import { ref, reactive, onUnmounted } from 'vue'
import type { BacktestKLine, BacktestSignal, VisualizationState, WSMessage } from '@/types/backtest-visualization'

export function useBacktestVisualization() {
  // 状态
  const state = reactive<VisualizationState>({
    status: 'idle',
    progress: 0,
    message: '等待启动',
    klines: [],
    account: null,
    signals: [],
    result: null
  })

  // WebSocket 连接
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5

  // 连接 WebSocket
  const connect = (backtestId: string) => {
    if (ws) {
      ws.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = '8010'
    const wsUrl = `${protocol}//${host}:${port}/api/backtest/ws/${backtestId}`

    try {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('[BacktestWS] 连接已建立')
        reconnectAttempts = 0
        state.message = 'WebSocket 连接成功'
      }

      ws.onmessage = (event) => {
        try {
          const data: WSMessage = JSON.parse(event.data)
          handleMessage(data)
        } catch (e) {
          console.error('[BacktestWS] 消息解析错误:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('[BacktestWS] 连接错误:', error)
        state.message = '连接错误'
        state.status = 'error'
      }

      ws.onclose = () => {
        console.log('[BacktestWS] 连接已关闭')
        // 尝试重连
        if (reconnectAttempts < maxReconnectAttempts && state.status === 'running') {
          reconnectTimer = setTimeout(() => {
            reconnectAttempts++
            console.log(`[BacktestWS] 尝试重连 (${reconnectAttempts}/${maxReconnectAttempts})`)
            connect(backtestId)
          }, 3000)
        }
      }
    } catch (e) {
      console.error('[BacktestWS] 创建连接失败:', e)
      state.status = 'error'
      state.message = '创建连接失败'
    }
  }

  // 处理消息
  const handleMessage = (data: WSMessage) => {
    switch (data.type) {
      case 'status':
        state.message = `状态: ${data.message || '运行中'}`
        break

      case 'started':
        state.status = 'running'
        state.message = '回测已启动'
        break

      case 'progress':
        state.progress = data.progress || 0
        state.message = data.message || `处理中 ${data.progress}%`
        break

      case 'kline':
        if (data.data) {
          const kline = data.data as BacktestKLine
          // 增量更新：如果最后一根K线时间相同，更新它；否则添加新K线
          const lastKline = state.klines[state.klines.length - 1]
          if (lastKline && lastKline.time === kline.time) {
            state.klines[state.klines.length - 1] = kline
          } else {
            state.klines.push(kline)
          }
        }
        break

      case 'account':
        if (data.data) {
          state.account = data.data as any
        }
        break

      case 'signal':
        if (data.data) {
          state.signals.push(data.data as BacktestSignal)
        }
        break

      case 'completed':
        state.status = 'completed'
        state.progress = 100
        state.message = '回测完成'
        if (data.result) {
          state.result = data.result
        }
        break

      case 'error':
        state.status = 'error'
        state.message = data.message || '发生错误'
        break
    }
  }

  // 启动回测
  const startBacktest = (backtestId: string) => {
    connect(backtestId)

    // 等待连接建立后发送启动命令
    const checkAndStart = () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'start' }))
      } else {
        setTimeout(checkAndStart, 100)
      }
    }
    checkAndStart()
  }

  // 获取状态
  const getStatus = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'get_status' }))
    }
  }

  // 断开连接
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
  }

  // 重置状态
  const reset = () => {
    state.status = 'idle'
    state.progress = 0
    state.message = '等待启动'
    state.klines = []
    state.account = null
    state.signals = []
    state.result = null
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    state,
    connect,
    startBacktest,
    getStatus,
    disconnect,
    reset
  }
}
