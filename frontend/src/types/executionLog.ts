export interface ExecutionLogSummary {
    id: number;
    workflow_id: number;
    status: 'success' | 'failed' | 'running';
    started_at: string;
    completed_at?: string;
    error_message?: string;
}

export interface ExecutionLogDetail {
    id: number;
    workflow_id: number;
    status: 'success' | 'failed' | 'running';
    payload: Record<string, any>;
    result?: Record<string, any>;
    error_message?: string;
    started_at: string;
    completed_at?: string;
}

export interface ExecutionLogFilters {
    status?: 'success' | 'failed' | 'running';
    limit?: number;
    offset?: number;
}