/**
 * QuanDA 共享类型定义
 */
export declare const IPC_CHANNELS: {
    readonly OPEN_EXTERNAL: "open:external";
    readonly GET_VERSION: "get:version";
    readonly PROCESS_START: "process:start";
    readonly PROCESS_STOP: "process:stop";
    readonly PROCESS_STATUS: "process:status";
    readonly BACKEND_START: "backend:start";
    readonly BACKEND_STOP: "backend:stop";
    readonly BACKEND_STATUS: "backend:status";
    readonly BACKEND_LOGS: "backend:logs";
    readonly DB_START: "db:start";
    readonly DB_STOP: "db:stop";
    readonly DB_STATUS: "db:status";
    readonly DB_MONGO_START: "db:mongo:start";
    readonly DB_CLICKHOUSE_START: "db:clickhouse:start";
    readonly DB_REDIS_START: "db:redis:start";
};
export type ProcessType = 'mongodb' | 'clickhouse' | 'redis' | 'backend';
export type ProcessStatus = 'stopped' | 'starting' | 'running' | 'stopping' | 'error';
export interface ProcessInfo {
    type: ProcessType;
    status: ProcessStatus;
    pid?: number;
    port?: number;
    path?: string;
    error?: string;
}
export interface BackendConfig {
    pythonPath: string;
    scriptPath: string;
    port: number;
    host: string;
}
export interface DatabaseConfig {
    mongo: {
        enabled: boolean;
        port: number;
        dataPath: string;
        executablePath?: string;
    };
    clickhouse: {
        enabled: boolean;
        port: number;
        dataPath: string;
        executablePath?: string;
    };
    redis: {
        enabled: boolean;
        port: number;
        dataPath: string;
        executablePath?: string;
    };
}
export interface UserDataPaths {
    root: string;
    data: string;
    logs: string;
    config: string;
    databases: string;
}
export interface LogEntry {
    timestamp: number;
    level: 'info' | 'warn' | 'error' | 'debug';
    source: string;
    message: string;
}
export interface AppState {
    backend: ProcessInfo;
    databases: {
        mongo: ProcessInfo;
        clickhouse: ProcessInfo;
        redis: ProcessInfo;
    };
    ports: {
        backend: number;
        mongo: number;
        clickhouse: number;
        redis: number;
    };
}
//# sourceMappingURL=index.d.ts.map