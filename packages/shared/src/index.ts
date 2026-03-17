/**
 * QuanDA 共享类型定义
 */

// ============================================
// IPC 通道常量
// ============================================

export const IPC_CHANNELS = {
  // 通用
  OPEN_EXTERNAL: 'open:external',
  GET_VERSION: 'get:version',

  // 进程管理
  PROCESS_START: 'process:start',
  PROCESS_STOP: 'process:stop',
  PROCESS_STATUS: 'process:status',

  // 后端管理
  BACKEND_START: 'backend:start',
  BACKEND_STOP: 'backend:stop',
  BACKEND_STATUS: 'backend:status',
  BACKEND_LOGS: 'backend:logs',

  // 数据库管理
  DB_START: 'db:start',
  DB_STOP: 'db:stop',
  DB_STATUS: 'db:status',
  DB_MONGO_START: 'db:mongo:start',
  DB_CLICKHOUSE_START: 'db:clickhouse:start',
  DB_REDIS_START: 'db:redis:start',
} as const

// ============================================
// 进程类型
// ============================================

export type ProcessType = 'mongodb' | 'clickhouse' | 'redis' | 'backend'

export type ProcessStatus = 'stopped' | 'starting' | 'running' | 'stopping' | 'error'

export interface ProcessInfo {
  type: ProcessType
  status: ProcessStatus
  pid?: number
  port?: number
  path?: string
  error?: string
}

// ============================================
// 后端配置
// ============================================

export interface BackendConfig {
  pythonPath: string
  scriptPath: string
  port: number
  host: string
}

// ============================================
// 数据库配置
// ============================================

export interface DatabaseConfig {
  mongo: {
    enabled: boolean
    port: number
    dataPath: string
    executablePath?: string
  }
  clickhouse: {
    enabled: boolean
    port: number
    dataPath: string
    executablePath?: string
  }
  redis: {
    enabled: boolean
    port: number
    dataPath: string
    executablePath?: string
  }
}

// ============================================
// 用户数据目录
// ============================================

export interface UserDataPaths {
  root: string
  data: string
  logs: string
  config: string
  databases: string
}

// ============================================
// 日志条目
// ============================================

export interface LogEntry {
  timestamp: number
  level: 'info' | 'warn' | 'error' | 'debug'
  source: string
  message: string
}

// ============================================
// 应用状态
// ============================================

export interface AppState {
  backend: ProcessInfo
  databases: {
    mongo: ProcessInfo
    clickhouse: ProcessInfo
    redis: ProcessInfo
  }
  ports: {
    backend: number
    mongo: number
    clickhouse: number
    redis: number
  }
}
