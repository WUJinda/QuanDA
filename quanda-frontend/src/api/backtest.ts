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
  },

  // 获取回测任务列表
  getList: () => {
    return request.get('/backtest/list')
  },

  // 获取回测任务详情
  getDetail: (id: number) => {
    return request.get(`/backtest/${id}`)
  },

  // 创建回测任务
  create: (data: any) => {
    return request.post('/backtest/create', data)
  },

  // 删除回测任务
  delete: (id: number) => {
    return request.delete(`/backtest/${id}`)
  },

  // 获取回测结果
  getResult: (id: number) => {
    return request.get(`/backtest/${id}/result`)
  }
}
