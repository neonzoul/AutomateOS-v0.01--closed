"""
Mock queue system for testing without Redis.

This module provides a simple in-memory queue system that can be used
for testing when Redis is not available.
"""

import uuid
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from .workflow_engine import WorkflowEngine, WorkflowExecutionError
from .database import get_session
from . import models

class MockJob:
    """Mock job class that mimics RQ Job behavior."""
    
    def __init__(self, job_id: str, func, *args, **kwargs):
        self.id = job_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = "queued"
        self.result = None
        self.exc_info = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.ended_at = None
    
    def get_status(self):
        return self.status

class MockQueue:
    """Mock queue class that mimics RQ Queue behavior."""
    
    def __init__(self, name: str):
        self.name = name
        self.jobs = {}
        self.job_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.running = True
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def enqueue(self, func, *args, **kwargs):
        """Enqueue a job for execution."""
        job_id = str(uuid.uuid4())
        job = MockJob(job_id, func, *args, **kwargs)
        
        self.jobs[job_id] = job
        self.job_queue.put(job)
        
        return job
    
    def _worker_loop(self):
        """Worker loop that processes jobs."""
        while self.running:
            try:
                job = self.job_queue.get(timeout=1)
                self._execute_job(job)
            except:
                continue
    
    def _execute_job(self, job: MockJob):
        """Execute a single job."""
        try:
            job.status = "started"
            job.started_at = datetime.utcnow()
            
            # Execute the job function
            result = job.func(*job.args, **job.kwargs)
            
            job.status = "finished"
            job.result = result
            job.ended_at = datetime.utcnow()
            
        except Exception as e:
            job.status = "failed"
            job.exc_info = str(e)
            job.ended_at = datetime.utcnow()
    
    def get_job(self, job_id: str) -> Optional[MockJob]:
        """Get a job by ID."""
        return self.jobs.get(job_id)
    
    def __len__(self):
        """Get queue length."""
        return self.job_queue.qsize()

# Global mock queue instance
mock_workflow_queue = MockQueue("workflow_execution")

def get_mock_workflow_queue():
    """Get the mock workflow queue."""
    return mock_workflow_queue

def enqueue_workflow_execution_mock(workflow_id: int, payload: Dict[str, Any]) -> str:
    """Mock version of enqueue_workflow_execution."""
    job = mock_workflow_queue.enqueue(
        execute_workflow_job_mock,
        workflow_id,
        payload
    )
    return job.id

def execute_workflow_job_mock(workflow_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock version of execute_workflow_job."""
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
        
        raise e
        
    finally:
        session.close()

def get_job_status_mock(job_id: str) -> Dict[str, Any]:
    """Mock version of get_job_status."""
    job = mock_workflow_queue.get_job(job_id)
    
    if not job:
        return {
            "id": job_id,
            "status": "not_found",
            "error": "Job not found in queue"
        }
    
    return {
        "id": job.id,
        "status": job.get_status(),
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        "result": job.result,
        "exc_info": job.exc_info
    }

def get_queue_info_mock() -> Dict[str, Any]:
    """Mock version of get_queue_info."""
    return {
        "name": mock_workflow_queue.name,
        "length": len(mock_workflow_queue),
        "failed_job_count": 0,  # Simplified for mock
        "started_job_count": 0,
        "finished_job_count": len([j for j in mock_workflow_queue.jobs.values() if j.status == "finished"])
    }