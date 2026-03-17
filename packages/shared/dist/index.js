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
};
//# sourceMappingURL=index.js.map