/**
 * QuanDA Preload 脚本
 * 通过 contextBridge 安全地将 API 暴露给渲染进程
 */

import { contextBridge, ipcRenderer } from 'electron'
import { IPC_CHANNELS } from '@quanda/shared'
import type { ProcessInfo, AppState } from '@quanda/shared'

/**
 * 暴露给渲染进程的 API 接口定义
 */
export interface ElectronAPI {
  // ===== 通用 =====
  openExternal: (url: string) => Promise<void>
  getVersion: () => Promise<string>

  // ===== 进程管理 =====
  getProcessStatus: () => Promise<Record<string, ProcessInfo>>

  // ===== 后端管理 =====
  startBackend: () => Promise<boolean>
  stopBackend: () => Promise<boolean>
  getBackendStatus: () => Promise<ProcessInfo>

  // ===== 数据库管理 =====
  startDatabase: (type: 'mongo' | 'clickhouse' | 'redis') => Promise<boolean>
  stopDatabase: (type: 'mongo' | 'clickhouse' | 'redis') => Promise<boolean>
  getDatabaseStatus: () => Promise<{
    mongo: ProcessInfo
    clickhouse: ProcessInfo
    redis: ProcessInfo
  }>

  // ===== 应用状态 =====
  getAppState: () => Promise<AppState>
}

/**
 * 实现 ElectronAPI 接口
 */
const electronAPI: ElectronAPI = {
  // 通用
  openExternal: (url: string) => {
    return ipcRenderer.invoke(IPC_CHANNELS.OPEN_EXTERNAL, url)
  },

  getVersion: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.GET_VERSION)
  },

  // 进程管理
  getProcessStatus: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.PROCESS_STATUS)
  },

  // 后端管理
  startBackend: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.BACKEND_START)
  },

  stopBackend: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.BACKEND_STOP)
  },

  getBackendStatus: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.BACKEND_STATUS)
  },

  // 数据库管理
  startDatabase: (type: 'mongo' | 'clickhouse' | 'redis') => {
    return ipcRenderer.invoke(IPC_CHANNELS.DB_START, type)
  },

  stopDatabase: (type: 'mongo' | 'clickhouse' | 'redis') => {
    return ipcRenderer.invoke(IPC_CHANNELS.DB_STOP, type)
  },

  getDatabaseStatus: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.DB_STATUS)
  },

  // 应用状态
  getAppState: () => {
    return ipcRenderer.invoke(IPC_CHANNELS.PROCESS_STATUS)
  },
}

// 将 API 暴露到渲染进程的 window 对象上
contextBridge.exposeInMainWorld('electronAPI', electronAPI)

// 扩展 Window 接口的类型定义
declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
