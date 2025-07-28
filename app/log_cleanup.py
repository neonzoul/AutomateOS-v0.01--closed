"""
Log cleanup utilities for AutomateOS.

This module provides utilities for cleaning up old execution logs
to prevent database bloat and maintain system performance.
"""

import argparse
import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select

from .database import get_session
from .models import ExecutionLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_execution_logs(days_to_keep: int = 30, dry_run: bool = False) -> int:
    """
    Clean up execution logs older than the specified number of days.
    
    Args:
        days_to_keep: Number of days to keep logs (default: 30)
        dry_run: If True, only count logs that would be deleted without actually deleting
        
    Returns:
        Number of logs deleted (or would be deleted in dry run mode)
    """
    session = next(get_session())
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        logger.info(f"Cleaning up execution logs older than {cutoff_date}")
        
        # Find logs to delete
        logs_to_delete = session.exec(
            select(ExecutionLog).where(
                ExecutionLog.started_at < cutoff_date
            )
        ).all()
        
        count = len(logs_to_delete)
        
        if dry_run:
            logger.info(f"DRY RUN: Would delete {count} execution logs")
            return count
        
        # Delete the logs
        for log in logs_to_delete:
            session.delete(log)
        
        session.commit()
        logger.info(f"Successfully deleted {count} execution logs")
        
        return count
        
    except Exception as e:
        logger.error(f"Error during log cleanup: {str(e)}")
        session.rollback()
        raise e
        
    finally:
        session.close()


def cleanup_logs_by_status(status: str, days_to_keep: int = 7, dry_run: bool = False) -> int:
    """
    Clean up execution logs with a specific status older than the specified days.
    
    This is useful for cleaning up failed logs more aggressively than successful ones.
    
    Args:
        status: Status of logs to clean ("success", "failed", "running")
        days_to_keep: Number of days to keep logs with this status
        dry_run: If True, only count logs that would be deleted
        
    Returns:
        Number of logs deleted (or would be deleted in dry run mode)
    """
    session = next(get_session())
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        logger.info(f"Cleaning up {status} execution logs older than {cutoff_date}")
        
        # Find logs to delete
        logs_to_delete = session.exec(
            select(ExecutionLog).where(
                ExecutionLog.status == status,
                ExecutionLog.started_at < cutoff_date
            )
        ).all()
        
        count = len(logs_to_delete)
        
        if dry_run:
            logger.info(f"DRY RUN: Would delete {count} {status} execution logs")
            return count
        
        # Delete the logs
        for log in logs_to_delete:
            session.delete(log)
        
        session.commit()
        logger.info(f"Successfully deleted {count} {status} execution logs")
        
        return count
        
    except Exception as e:
        logger.error(f"Error during {status} log cleanup: {str(e)}")
        session.rollback()
        raise e
        
    finally:
        session.close()


def get_log_statistics() -> dict:
    """
    Get statistics about execution logs in the database.
    
    Returns:
        Dict containing log counts by status and age
    """
    session = next(get_session())
    
    try:
        from sqlmodel import func
        
        # Total count
        total_count = session.exec(select(func.count(ExecutionLog.id))).first()
        
        # Count by status
        status_counts = {}
        for status in ["success", "failed", "running"]:
            count = session.exec(
                select(func.count(ExecutionLog.id)).where(ExecutionLog.status == status)
            ).first()
            status_counts[status] = count or 0
        
        # Count by age
        now = datetime.utcnow()
        age_counts = {}
        
        for days, label in [(1, "last_day"), (7, "last_week"), (30, "last_month")]:
            cutoff = now - timedelta(days=days)
            count = session.exec(
                select(func.count(ExecutionLog.id)).where(ExecutionLog.started_at >= cutoff)
            ).first()
            age_counts[label] = count or 0
        
        # Oldest log
        oldest_log = session.exec(
            select(ExecutionLog.started_at).order_by(ExecutionLog.started_at.asc()).limit(1)
        ).first()
        
        return {
            "total_logs": total_count or 0,
            "by_status": status_counts,
            "by_age": age_counts,
            "oldest_log": oldest_log.isoformat() if oldest_log else None
        }
        
    finally:
        session.close()


def main():
    """Command-line interface for log cleanup utilities."""
    parser = argparse.ArgumentParser(description="AutomateOS Log Cleanup Utilities")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old execution logs")
    cleanup_parser.add_argument(
        "--days", 
        type=int, 
        default=30, 
        help="Number of days to keep logs (default: 30)"
    )
    cleanup_parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be deleted without actually deleting"
    )
    
    # Status-specific cleanup command
    status_parser = subparsers.add_parser("cleanup-status", help="Clean up logs by status")
    status_parser.add_argument(
        "status", 
        choices=["success", "failed", "running"], 
        help="Status of logs to clean up"
    )
    status_parser.add_argument(
        "--days", 
        type=int, 
        default=7, 
        help="Number of days to keep logs with this status (default: 7)"
    )
    status_parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be deleted without actually deleting"
    )
    
    # Statistics command
    subparsers.add_parser("stats", help="Show execution log statistics")
    
    args = parser.parse_args()
    
    if args.command == "cleanup":
        count = cleanup_execution_logs(days_to_keep=args.days, dry_run=args.dry_run)
        if args.dry_run:
            print(f"Would delete {count} execution logs")
        else:
            print(f"Deleted {count} execution logs")
            
    elif args.command == "cleanup-status":
        count = cleanup_logs_by_status(
            status=args.status, 
            days_to_keep=args.days, 
            dry_run=args.dry_run
        )
        if args.dry_run:
            print(f"Would delete {count} {args.status} execution logs")
        else:
            print(f"Deleted {count} {args.status} execution logs")
            
    elif args.command == "stats":
        stats = get_log_statistics()
        print("Execution Log Statistics:")
        print(f"  Total logs: {stats['total_logs']}")
        print(f"  By status:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
        print(f"  By age:")
        for age, count in stats['by_age'].items():
            print(f"    {age}: {count}")
        if stats['oldest_log']:
            print(f"  Oldest log: {stats['oldest_log']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()