# AutomateOS Task Queue Infrastructure

This document describes the task queue infrastructure implemented for AutomateOS workflow execution.

## Overview

The task queue infrastructure enables asynchronous processing of workflow executions using Redis and RQ (Redis Queue). This ensures that webhook triggers return immediately while workflows are processed in the background.

## Components

### 1. Redis Connection (`app/queue.py`)

- **Redis URL**: Configurable via `REDIS_URL` environment variable (default: `redis://localhost:6379/0`)
- **Connection**: Shared Redis connection for queue operations
- **Queue**: Named queue `workflow_execution` for all workflow jobs

### 2. Job Functions

#### `enqueue_workflow_execution(workflow_id, payload)`
- Enqueues a workflow for background execution
- Returns job ID for tracking
- Configures 10-minute timeout and 24-hour result retention

#### `execute_workflow_job(workflow_id, payload)`
- Main job function executed by workers
- Creates execution logs in database
- Handles errors and updates execution status
- Currently placeholder - full implementation in task 5.2

#### `get_job_status(job_id)`
- Retrieves job status and metadata
- Returns status, timestamps, results, and error information

### 3. Background Worker (`worker.py`)

- Standalone script for processing queued jobs
- Handles graceful shutdown on SIGINT/SIGTERM
- Connects to Redis and processes jobs from `workflow_execution` queue

### 4. Webhook Endpoint (`/webhook/{webhook_id}`)

- Receives HTTP POST requests from external services
- Validates webhook ID against database
- Enqueues workflow execution immediately
- Returns HTTP 202 Accepted with job information

### 5. Monitoring Endpoints

#### `GET /jobs/{job_id}/status`
- Returns detailed job status information
- Includes execution timestamps and results

#### `GET /queue/info`
- Returns queue statistics
- Shows job counts by status (queued, running, failed, finished)

## Database Integration

### Execution Logging

The queue system integrates with the database to create execution logs:

```python
class ExecutionLog(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    status: str  # "running", "success", "failed"
    payload: dict  # Input data
    result: Optional[dict]  # Execution results
    error_message: Optional[str]  # Error details
    started_at: datetime
    completed_at: Optional[datetime]
```

### Workflow Lookup

Webhooks are resolved to workflows using the `webhook_url` field:

```python
def get_workflow_by_webhook_id(session: Session, webhook_id: str) -> Workflow:
    webhook_url = f"/webhook/{webhook_id}"
    return session.exec(
        select(Workflow).where(Workflow.webhook_url == webhook_url)
    ).first()
```

## Usage

### Starting the Infrastructure

1. **Start Redis** (required):
   ```bash
   # Install and start Redis server
   redis-server
   ```

2. **Start the FastAPI server**:
   ```bash
   python start_server.py
   # or
   uvicorn app.main:app --reload
   ```

3. **Start background workers**:
   ```bash
   python start_worker.py
   # or
   python worker.py
   ```

### Testing

Run the test scripts to verify functionality:

```bash
# Test queue infrastructure
python test_queue.py

# Test webhook endpoints (requires server running)
python test_webhook.py
```

### Triggering Workflows

Send HTTP POST requests to webhook URLs:

```bash
curl -X POST http://localhost:8000/webhook/{webhook_id} \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

Response:
```json
{
  "message": "Workflow execution enqueued",
  "job_id": "abc123-def456-...",
  "workflow_id": 1,
  "status": "accepted"
}
```

### Monitoring Jobs

Check job status:

```bash
curl http://localhost:8000/jobs/{job_id}/status
```

Check queue statistics:

```bash
curl http://localhost:8000/queue/info
```

## Configuration

### Environment Variables

- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `WORKER_COUNT`: Number of worker processes (future enhancement)

### Job Configuration

- **Timeout**: 10 minutes per workflow execution
- **Result TTL**: 24 hours
- **Failure TTL**: 24 hours

## Error Handling

### Job Failures

- Failed jobs are marked with status "failed"
- Error messages are stored in execution logs
- Failed jobs are moved to RQ's failed job registry

### Connection Failures

- Redis connection errors are handled gracefully
- Server continues to operate without queue functionality
- Workers automatically reconnect on Redis restart

### Workflow Errors

- Invalid webhook IDs return HTTP 404
- Inactive workflows return HTTP 400
- Database errors are logged and propagated

## Security Considerations

- Webhook URLs use UUIDs for security through obscurity
- No authentication required for webhook endpoints (by design)
- Payload data is stored in execution logs for audit trail

## Performance

### Scalability

- Multiple workers can process jobs concurrently
- Redis handles job distribution automatically
- Database connections are managed per job execution

### Monitoring

- Queue length and job counts available via API
- Execution logs provide detailed timing information
- Failed jobs are retained for debugging

## Future Enhancements

1. **Job Priorities**: Different priority levels for workflows
2. **Retry Logic**: Automatic retry for failed jobs
3. **Dead Letter Queue**: Special handling for repeatedly failed jobs
4. **Metrics**: Detailed performance and usage metrics
5. **Clustering**: Multi-instance worker deployment

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **4.2**: Asynchronous workflow execution via background jobs
- **4.3**: Immediate HTTP 202 response for webhook triggers
- **4.4**: Background processing without blocking web server
- **7.1**: Concurrent workflow execution handling
- **7.2**: Responsive web server under load
- **7.3**: Non-blocking long-running workflow execution