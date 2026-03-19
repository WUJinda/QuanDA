/**
 * WebSocket 连接管理 Composable
 * 支持自动重连、心跳检测
 */
import { ref, onMounted, onUnmounted } from 'vue'

export interface WebSocketOptions {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
  reconnect?: boolean
  maxReconnectAttempts?: number
  reconnectInterval?: number
  heartbeatInterval?: number
}

export function useWebSocket(url: string, options: WebSocketOptions = {}) {
  const {
    onMessage,
    onError,
    onOpen,
    onClose,
    reconnect = true,
    maxReconnectAttempts = 5,
    reconnectInterval = 3000,
    heartbeatInterval = 30000
  } = options

  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const shouldReconnect = ref(true)
  
  let heartbeatTimer: number | null = null
  let reconnectTimer: number | null = null

  const connect = () => {
    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        console.log('WebSocket 连接成功')
        isConnected.value = true
        reconnectAttempts.value = 0
        
        // 启动心跳
        startHeartbeat()
        
        if (onOpen) onOpen()
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessage) onMessage(data)
        } catch (e) {
          console.error('WebSocket 消息解析错误:', e)
        }
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket 错误:', error)
        if (onError) onError(error)
      }

      ws.value.onclose = () => {
        console.log('WebSocket 连接关闭')
        isConnected.value = false
        stopHeartbeat()
        
        if (onClose) onClose()

        // 尝试重连
        if (shouldReconnect.value && reconnect && reconnectAttempts.value < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(2, reconnectAttempts.value)
          console.log(`${delay}ms 后尝试重连...`)
          
          reconnectTimer = window.setTimeout(() => {
            reconnectAttempts.value++
            connect()
          }, delay)
        } else if (reconnectAttempts.value >= maxReconnectAttempts) {
          console.error('WebSocket 重连次数已达上限')
        }
      }
    } catch (error) {
      console.error('WebSocket 连接失败:', error)
    }
  }

  const startHeartbeat = () => {
    if (heartbeatTimer) return

    heartbeatTimer = window.setInterval(() => {
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        // 发送心跳包
        ws.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, heartbeatInterval)
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  const send = (data: any) => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(typeof data === 'string' ? data : JSON.stringify(data))
      return true
    }
    console.warn('WebSocket 未连接，无法发送消息')
    return false
  }

  const close = () => {
    shouldReconnect.value = false
    stopHeartbeat()
    
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    close()
  })

  return {
    ws,
    isConnected,
    send,
    close,
    reconnect: connect
  }
}
