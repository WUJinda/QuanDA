/**
 * 进程管理器
 * 负责管理数据库和 Python 后端进程
 */

import { spawn, ChildProcess } from 'child_process'
import { join } from 'path'
import { existsSync } from 'fs'
import { app } from 'electron'
import type { ProcessInfo, ProcessType, ProcessStatus } from '@quanda/shared'
import { getDatabasePath, getDatabaseExecutable, ensureDirectories } from './paths'

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
   */
  private async startMongoDB(): Promise<boolean> {
    const dataPath = getDatabasePath('mongo')
    const port = 27017
    const executable = getDatabaseExecutable('mongo')

    console.log(`[进程管理] MongoDB 启动中 (端口: ${port}, 数据目录: ${dataPath})`)

    try {
      // 检查可执行文件是否存在
      if (!executable || !existsSync(executable)) {
        console.warn(`[进程管理] MongoDB 可执行文件不存在，跳过启动`)
        this.updateStatus('mongodb', {
          status: 'stopped',
          error: 'MongoDB 未安装'
        })
        return false
      }

      // 创建数据库数据目录
      const fs = require('fs')
      if (!fs.existsSync(dataPath)) {
        fs.mkdirSync(dataPath, { recursive: true })
      }

      const command = executable
      const args = [
        '--dbpath', dataPath,
        '--port', String(port),
        '--bind_ip', '127.0.0.1',
        '--logpath', join(dataPath, 'mongodb.log')
      ]
      
      console.log(`[进程管理] 使用绿色版 MongoDB: ${executable}`)

      const child = spawn(command, args, {
        detached: true,
        stdio: 'ignore'
      })

      this.childProcesses.set('mongodb', child)
      child.unref()

      // 等待启动
      await new Promise(resolve => setTimeout(resolve, 2000))

      this.updateStatus('mongodb', {
        status: 'running',
        port,
        path: dataPath,
        pid: child.pid
      })

      console.log(`[进程管理] MongoDB 启动成功 (PID: ${child.pid})`)
      return true
    } catch (error) {
      console.error(`[进程管理] MongoDB 启动失败:`, error)
      this.updateStatus('mongodb', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      return false
    }
  }

  /**
   * 启动 ClickHouse
   */
  private async startClickHouse(): Promise<boolean> {
    const dataPath = getDatabasePath('clickhouse')
    const port = 8123
    const executable = getDatabaseExecutable('clickhouse')

    console.log(`[进程管理] ClickHouse 启动中 (端口: ${port}, 数据目录: ${dataPath})`)

    try {
      // 检查可执行文件是否存在
      if (!executable || !existsSync(executable)) {
        console.warn(`[进程管理] ClickHouse 可执行文件不存在，跳过启动`)
        this.updateStatus('clickhouse', {
          status: 'stopped',
          error: 'ClickHouse 未安装'
        })
        return false
      }

      // 创建数据库数据目录
      const fs = require('fs')
      if (!fs.existsSync(dataPath)) {
        fs.mkdirSync(dataPath, { recursive: true })
      }

      const command = executable
      const args = [
        '--config-file', join(dataPath, 'config.xml'),
        '--http-port', String(port),
        '--path', join(dataPath, 'data'),
        '--logger.log_path', join(dataPath, 'clickhouse.log')
      ]
      
      console.log(`[进程管理] 使用绿色版 ClickHouse: ${executable}`)

      const child = spawn(command, args, {
        detached: true,
        stdio: 'ignore'
      })

      this.childProcesses.set('clickhouse', child)
      child.unref()

      // 等待启动
      await new Promise(resolve => setTimeout(resolve, 3000))

      this.updateStatus('clickhouse', {
        status: 'running',
        port,
        path: dataPath,
        pid: child.pid
      })

      console.log(`[进程管理] ClickHouse 启动成功 (PID: ${child.pid})`)
      return true
    } catch (error) {
      console.error(`[进程管理] ClickHouse 启动失败:`, error)
      this.updateStatus('clickhouse', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      return false
    }
  }

  /**
   * 启动 Redis
   */
  private async startRedis(): Promise<boolean> {
    const dataPath = getDatabasePath('redis')
    const port = 6379
    const executable = getDatabaseExecutable('redis')

    console.log(`[进程管理] Redis 启动中 (端口: ${port}, 数据目录: ${dataPath})`)

    try {
      // 检查可执行文件是否存在
      if (!executable || !existsSync(executable)) {
        console.warn(`[进程管理] Redis 可执行文件不存在，跳过启动`)
        this.updateStatus('redis', {
          status: 'stopped',
          error: 'Redis 未安装'
        })
        return false
      }

      // 创建数据库数据目录
      const fs = require('fs')
      if (!fs.existsSync(dataPath)) {
        fs.mkdirSync(dataPath, { recursive: true })
      }

      const command = executable
      const args = [
        '--port', String(port),
        '--dir', dataPath,
        '--logfile', join(dataPath, 'redis.log')
      ]
      
      console.log(`[进程管理] 使用绿色版 Redis: ${executable}`)

      const child = spawn(command, args, {
        detached: true,
        stdio: 'ignore'
      })

      this.childProcesses.set('redis', child)
      child.unref()

      // 等待启动
      await new Promise(resolve => setTimeout(resolve, 1000))

      this.updateStatus('redis', {
        status: 'running',
        port,
        path: dataPath,
        pid: child.pid
      })

      console.log(`[进程管理] Redis 启动成功 (PID: ${child.pid})`)
      return true
    } catch (error) {
      console.error(`[进程管理] Redis 启动失败:`, error)
      this.updateStatus('redis', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      })
      return false
    }
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
      const isDev = !app.isPackaged
      let executablePath = ''
      const port = 8010

      if (isDev) {
        // 开发模式：使用 Python 脚本
        const possiblePaths = [
          join(process.cwd(), 'quanda', 'QDWebServer', 'server.py'),
          join(process.cwd(), 'packages', 'backend', 'quanda', 'QDWebServer', 'server.py'),
        ]

        for (const path of possiblePaths) {
          if (existsSync(path)) {
            executablePath = path
            break
          }
        }

        if (!executablePath) {
          throw new Error('找不到 Python 后端脚本')
        }

        const pythonPath = process.env.PYTHON_PATH || 'python'
        console.log(`[进程管理] 开发模式 - 启动 Python 后端: ${pythonPath} ${executablePath}`)

        const child = spawn(pythonPath, [executablePath], {
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
            path: executablePath
          })
          console.log(`[进程管理] 后端启动成功 (PID: ${child.pid}, 端口: ${port})`)
          return true
        }

        return false
      } else {
        // 生产模式：使用 PyInstaller 编译后的可执行文件
        const backendExecutable = join(process.resourcesPath, 'backend', 'quanda-backend.exe')

        console.log(`[进程管理] 生产模式 - 查找后端可执行文件: ${backendExecutable}`)
        console.log(`[进程管理] 文件是否存在: ${existsSync(backendExecutable)}`)

        if (!existsSync(backendExecutable)) {
          console.error('[进程管理] 后端可执行文件不存在，应用可能未正确打包')
          this.updateStatus('backend', {
            status: 'error',
            error: '后端可执行文件不存在，请重新安装应用'
          })
          return false
        }

        console.log(`[进程管理] 生产模式 - 启动后端可执行文件: ${backendExecutable}`)

        const child = spawn(backendExecutable, [], {
          detached: true,
          stdio: 'ignore'
        })

        this.childProcesses.set('backend', child)
        child.unref()

        // 等待后端启动
        await new Promise(resolve => setTimeout(resolve, 3000))

        this.updateStatus('backend', {
          status: 'running',
          pid: child.pid,
          port,
          path: backendExecutable
        })

        console.log(`[进程管理] 后端启动成功 (PID: ${child.pid}, 端口: ${port})`)
        return true
      }
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
