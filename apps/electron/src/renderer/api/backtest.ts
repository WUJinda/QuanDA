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
  getList: async () => {
    const response = await request.get('/backtest/list')
    return response?.data || []
  },

  // 获取回测任务详情
  getDetail: async (id: number) => {
    const response = await request.get(`/backtest/${id}`)
    return response?.data || null
  },

  // 创建回测任务
  create: async (data: any) => {
    const response = await request.post('/backtest/create', data)
    return response?.data || null
  },

  // 删除回测任务
  delete: async (id: number) => {
    const response = await request.delete(`/backtest/${id}`)
    return response?.data || null
  },

  // 获取回测结果
  getResult: async (id: number) => {
    const response = await request.get(`/backtest/${id}/result`)
    return response?.data || null
  }
}
