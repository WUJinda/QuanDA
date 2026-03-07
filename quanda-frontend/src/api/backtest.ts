import request from './request'

export const backtestApi = {
  // 运行回测命令
  runCommand: (command: string) => {
    return request.post('/command/run', null, {
      params: { command }
    })
  },

  // WebSocket 连接用于实时输出
  getWebSocketUrl: () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = '8010' // QuanDA 后端端口
    return `${protocol}//${host}:${port}/command/runws`
  }
}
