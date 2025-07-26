"""
Redis Queue configuration and job management for AutomateOS.

This module handles the asynchronous task queue infrastructure using Redis and RQ.
It provides functions for connecting to Redis, managing job queues, and tracking
workflow execution jobs.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from sqlmodel import Session

from .database import get_session
from . import crud, models

# Redis connection configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis connection
redis_conn = Redis.from_url(REDIS_URL, decode_responses=False)

# Initialize RQ queue for workflow execution
workflow_queue = Queue("workflow_execution", connection=redis_conn)


def get_redis_connection() -> Redis:
    """
    Get Redis connection instance.
    
    Returns:
        Redis: Configured Redis connection
    """
    return redis_conn


def get_workflow_queue() -> Queue:
    """
    Get the workflow execution queue.
    
    Returns:
        Queue: RQ queue for workflow execution jobs
    """
    return workflow_queue


def enqueue_workflow_execution(workflow_id: int, payload: Dict[str, Any]) -> str:
    """
    Enqueue a workflow for execution.
    
    Args:
        workflow_id: ID of the workflow to execute
        payload: Input data for the workflow execution
        
    Returns:
        str: Job ID for tracking the execution
    """
    job = workflow_queue.enqueue(
        execute_workflow_job,
        workflow_id,
        payload,
        job_timeout="10m",  # 10 minute timeout for workflow execution
        result_ttl=86400,   # Keep results for 24 hours
        failure_ttl=86400   # Keep failed job info for 24 hours
    )
    return job.id


def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a queued job.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        Dict containing job status information
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": job.result,
            "exc_info": job.exc_info
        }
    except NoSuchJobError:
        return {
            "id": job_id,
            "status": "not_found",
            "error": "Job not found in queue"
        }


def execute_workflow_job(workflow_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a workflow job with error handling and logging.
    
    This function is called by RQ workers to process workflow executions.
    It creates execution logs, handles errors, and stores results.
    
    Args:
        workflow_id: ID of the workflow to execute
        payload: Input data for the workflow
        
    Returns:
        Dict containing execution results
    """
    from .workflow_engine import WorkflowEngine, WorkflowExecutionError
    
    session = next(get_session())
    execution_log = None
    
    try:
        # Get workflow from database
        workflow = session.get(models.Workflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        if not workflow.is_active:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Create execution log entry
        execution_log = models.ExecutionLog(
            workflow_id=workflow_id,
            status="running",
            payload=payload,
            started_at=datetime.utcnow()
        )
        session.add(execution_log)
        session.commit()
        session.refresh(execution_log)
        
        # Execute workflow using the workflow engine
        engine = WorkflowEngine()
        result = engine.execute_workflow(workflow, payload)
        
        # Update execution log with success
        execution_log.status = "success"
        execution_log.result = result
        execution_log.completed_at = datetime.utcnow()
        session.add(execution_log)
        session.commit()
        
        return result
        
    except WorkflowExecutionError as e:
        error_message = e.message
        error_details = e.details
        
        # Update execution log with failure
        if execution_log:
            execution_log.status = "failed"
            execution_log.error_message = error_message
            execution_log.result = error_details
            execution_log.completed_at = datetime.utcnow()
            session.add(execution_log)
            session.commit()
        
        # Re-raise the exception so RQ marks the job as failed
        raise e
        
    except Exception as e:
        error_message = str(e)
        
        # Update execution log with failure
        if execution_log:
            execution_log.status = "failed"
            execution_log.error_message = error_message
            execution_log.completed_at = datetime.utcnow()
            session.add(execution_log)
            session.commit()
        
        # Re-raise the exception so RQ marks the job as failed
        raise e
        
    finally:
        session.close()


def get_queue_info() -> Dict[str, Any]:
    """
    Get information about the workflow queue.
    
    Returns:
        Dict containing queue statistics
    """
    return {
        "name": workflow_queue.name,
        "length": len(workflow_queue),
        "failed_job_count": workflow_queue.failed_job_registry.count,
        "started_job_count": workflow_queue.started_job_registry.count,
        "finished_job_count": workflow_queue.finished_job_registry.count
    }