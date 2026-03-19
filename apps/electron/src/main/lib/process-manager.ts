/**
 * 进程管理器
 * 负责管理数据库和 Python 后端进程
 */

import { spawn, ChildProcess, exec } from 'child_process'
import { join } from 'path'
import { existsSync } from 'fs'
import type { ProcessInfo, ProcessType, ProcessStatus } from '@quanda/shared'
import { getDatabasePath, ensureDirectories } from './paths'

/**
 * 进程管理器类
 */
export class ProcessManager {
  private processes: Map<ProcessType, ProcessInfo> = new Map()
  private childProcesses: Map<ProcessType, ChildProcess> = new Map()

  constructor() {
    ensureDirectories()
    this.initializeStatus()
  }

  /**
   * 初始化进程状态
   */
  private initializeStatus(): void {
    const types: ProcessType[] = ['mongodb', 'clickhouse', 'redis', 'backend']
    for (const type of types) {
      this.processes.set(type, {
        type,
        status: 'stopped',
      })
    }
  }

  /**
   * 获取所有进程状态
   */
  public getAllStatus(): Record<string, ProcessInfo> {
    const result: Record<string, ProcessInfo> = {}
    for (const [key, value] of this.processes) {
      result[key] = { ...value }
    }
    return result
  }

  /**
   * 获取单个进程状态
   */
  public getStatus(type: ProcessType): ProcessInfo {
    return this.processes.get(type) || { type, status: 'stopped' }
  }

  /**
   * 更新进程状态
   */
  private updateStatus(type: ProcessType, updates: Partial<ProcessInfo>): void {
    const current = this.processes.get(type)
    if (current) {
      this.processes.set(type, { ...current, ...updates })
    }
  }

  /**
   * 启动数据库
   */
  public async startDatabase(type: 'mongo' | 'clickhouse' | 'redis'): Promise<boolean> {
    const typeMap = {
      mongo: 'mongodb',
      clickhouse: 'clickhouse',
      redis: 'redis'
    } as const

    const processType: ProcessType = typeMap[type]
    const current = this.getStatus(processType)

    if (current.status === 'running' || current.status === 'starting') {
      console.log(`[进程管理] ${type} 已经在运行或正在启动`)
      return true
    }

    this.updateStatus(processType, { status: 'starting' })

    try {
      let success = false

      if (type === 'mongo') {
        success = await this.startMongoDB()
      } else if (type === 'clickhouse') {
        success = await this.startClickHouse()
      } else if (type === 'redis') {
        success = await this.startRedis()
      }

      if (success) {
        this.updateStatus(processType, { status: 'running' })
        console.log(`[进程管理] ${type} 启动成功`)
        return true
      } else {
        this.updateStatus(processType, { status: 'error', error: '启动失败' })
        return false
      }
    } catch (error) {
      this.updateStatus(processType, {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      console.error(`[进程管理] ${type} 启动失败:`, error)
      return false
    }
  }

  /**
   * 停止数据库
   */
  public async stopDatabase(type: 'mongo' | 'clickhouse' | 'redis'): Promise<boolean> {
    const typeMap = {
      mongo: 'mongodb',
      clickhouse: 'clickhouse',
      redis: 'redis'
    } as const

    const processType: ProcessType = typeMap[type]
    const child = this.childProcesses.get(processType)

    if (child) {
      child.kill('SIGTERM')
      this.childProcesses.delete(processType)
      this.updateStatus(processType, { status: 'stopped', pid: undefined })
      console.log(`[进程管理] ${type} 已停止`)
      return true
    }

    return false
  }

  /**
   * 获取所有数据库状态
   */
  public getAllDatabaseStatus(): Record<string, ProcessInfo> {
    return {
      mongo: this.getStatus('mongodb'),
      clickhouse: this.getStatus('clickhouse'),
      redis: this.getStatus('redis'),
    }
  }

  /**
   * 启动 MongoDB
   * 注意：Demo 版本假设 MongoDB 由用户自己管理（系统服务或手动启动）
   */
  private async startMongoDB(): Promise<boolean> {
    const dataPath = getDatabasePath('mongo')
    const port = 27017

    console.log(`[进程管理] MongoDB 检查 (端口: ${port}, 数据目录: ${dataPath})`)

    // 检查 MongoDB 连接是否可用
    const isAvailable = await this.checkMongoDBConnection()

    if (isAvailable) {
      this.updateStatus('mongodb', { status: 'running', port, path: dataPath })
      console.log('[进程管理] MongoDB 连接成功')
      return true
    } else {
      this.updateStatus('mongodb', { status: 'stopped', port, path: dataPath })
      console.warn('[进程管理] MongoDB 不可用，请在设置中配置或启动 MongoDB')
      return false
    }
  }

  /**
   * 检查 MongoDB 连接是否可用
   */
  private async checkMongoDBConnection(): Promise<boolean> {
    return new Promise((resolve) => {
      // 使用 mongosh 或 mongo 命令检查连接
      const mongoCmd = process.platform === 'win32' ? 'mongosh' : 'mongosh'

      exec(`${mongoCmd} --eval "db.version()" --quiet`, (error) => {
        if (error) {
          // 尝试旧版的 mongo 命令
          exec(`mongo --eval "db.version()" --quiet`, (error2) => {
            resolve(!error2)
          })
        } else {
          resolve(true)
        }
      })
    })
  }

  /**
   * 启动 ClickHouse
   */
  private async startClickHouse(): Promise<boolean> {
    const dataPath = getDatabasePath('clickhouse')
    const port = 8123

    console.log(`[进程管理] ClickHouse 启动 (端口: ${port}, 数据目录: ${dataPath})`)
    this.updateStatus('clickhouse', { port, path: dataPath })

    // 模拟启动成功
    return true
  }

  /**
   * 启动 Redis
   */
  private async startRedis(): Promise<boolean> {
    const dataPath = getDatabasePath('redis')
    const port = 6379

    console.log(`[进程管理] Redis 启动 (端口: ${port}, 数据目录: ${dataPath})`)
    this.updateStatus('redis', { port, path: dataPath })

    // 模拟启动成功
    return true
  }

  /**
   * 启动 Python 后端
   */
  public async startBackend(): Promise<boolean> {
    const current = this.getStatus('backend')

    if (current.status === 'running' || current.status === 'starting') {
      console.log('[进程管理] 后端已经在运行或正在启动')
      return true
    }

    this.updateStatus('backend', { status: 'starting' })

    try {
      // TODO: 实际应该使用打包的 Python 后端可执行文件
      // 这里先使用开发模式下的 Python 脚本

      // 查找 Python 后端脚本
      const possiblePaths = [
        join(process.cwd(), 'quanda', 'QDWebServer', 'server.py'),
        join(process.cwd(), 'packages', 'backend', 'quanda', 'QDWebServer', 'server.py'),
      ]

      let scriptPath = ''
      for (const path of possiblePaths) {
        if (existsSync(path)) {
          scriptPath = path
          break
        }
      }

      if (!scriptPath) {
        throw new Error('找不到 Python 后端脚本')
      }

      const pythonPath = process.env.PYTHON_PATH || 'D:\\Programs\\Python\\Python313\\python.exe'
      const port = 8010

      console.log(`[进程管理] 启动 Python 后端: ${pythonPath} ${scriptPath}`)

      const child = spawn(pythonPath, [scriptPath], {
        cwd: process.cwd(),
        env: { ...process.env },
      })

      this.childProcesses.set('backend', child)

      child.stdout?.on('data', (data) => {
        console.log(`[后端] ${data.toString().trim()}`)
      })

      child.stderr?.on('data', (data) => {
        console.error(`[后端错误] ${data.toString().trim()}`)
      })

      child.on('error', (error) => {
        console.error('[进程管理] 后端进程错误:', error)
        this.updateStatus('backend', {
          status: 'error',
          error: error.message
        })
      })

      child.on('exit', (code, signal) => {
        console.log(`[进程管理] 后端进程退出 (code: ${code}, signal: ${signal})`)
        this.updateStatus('backend', { status: 'stopped', pid: undefined })
        this.childProcesses.delete('backend')
      })

      // 等待后端启动
      await new Promise(resolve => setTimeout(resolve, 3000))

      if (child.pid) {
        this.updateStatus('backend', {
          status: 'running',
          pid: child.pid,
          port,
          path: scriptPath
        })
        console.log(`[进程管理] 后端启动成功 (PID: ${child.pid}, 端口: ${port})`)
        return true
      }

      return false
    } catch (error) {
      this.updateStatus('backend', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      console.error('[进程管理] 后端启动失败:', error)
      return false
    }
  }

  /**
   * 停止 Python 后端
   */
  public async stopBackend(): Promise<boolean> {
    const child = this.childProcesses.get('backend')

    if (child) {
      child.kill('SIGTERM')
      this.childProcesses.delete('backend')
      this.updateStatus('backend', { status: 'stopped', pid: undefined })
      console.log('[进程管理] 后端已停止')
      return true
    }

    return false
  }

  /**
   * 获取后端状态
   */
  public getBackendStatus(): ProcessInfo {
    return this.getStatus('backend')
  }

  /**
   * 停止所有进程
   */
  public async stopAll(): Promise<void> {
    console.log('[进程管理] 停止所有进程...')

    // 停止后端
    await this.stopBackend()

    // 停止数据库
    await this.stopDatabase('mongo')
    await this.stopDatabase('clickhouse')
    await this.stopDatabase('redis')

    console.log('[进程管理] 所有进程已停止')
  }
}
