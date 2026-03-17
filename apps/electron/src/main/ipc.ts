/**
 * QuanDA IPC 通信处理器
 */

import { ipcMain, shell } from 'electron'
import { IPC_CHANNELS } from '@quanda/shared'
import type { ProcessManager } from './lib/process-manager'

/**
 * 注册所有 IPC 处理器
 */
export function registerIpcHandlers(ipcMain: Electron.IpcMain, processManager: ProcessManager | null): void {
  // ============================================
  // 通用
  // ============================================

  ipcMain.handle(IPC_CHANNELS.OPEN_EXTERNAL, async (_event, url: string) => {
    await shell.openExternal(url)
    return true
  })

  ipcMain.handle(IPC_CHANNELS.GET_VERSION, async () => {
    return '1.0.0'
  })

  // ============================================
  // 进程管理
  // ============================================

  ipcMain.handle(IPC_CHANNELS.PROCESS_STATUS, async () => {
    return processManager?.getAllStatus() || {}
  })

  // ============================================
  // 后端管理
  // ============================================

  ipcMain.handle(IPC_CHANNELS.BACKEND_START, async () => {
    return await processManager?.startBackend()
  })

  ipcMain.handle(IPC_CHANNELS.BACKEND_STOP, async () => {
    return await processManager?.stopBackend()
  })

  ipcMain.handle(IPC_CHANNELS.BACKEND_STATUS, async () => {
    return processManager?.getBackendStatus()
  })

  // ============================================
  // 数据库管理
  // ============================================

  ipcMain.handle(IPC_CHANNELS.DB_START, async (_event, type: 'mongo' | 'clickhouse' | 'redis') => {
    return await processManager?.startDatabase(type)
  })

  ipcMain.handle(IPC_CHANNELS.DB_STOP, async (_event, type: 'mongo' | 'clickhouse' | 'redis') => {
    return await processManager?.stopDatabase(type)
  })

  ipcMain.handle(IPC_CHANNELS.DB_STATUS, async () => {
    return processManager?.getAllDatabaseStatus()
  })

  console.log('[IPC] 所有处理器已注册')
}
