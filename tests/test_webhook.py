#!/usr/bin/env python3
"""
Test script for webhook endpoint functionality.

This script tests the webhook trigger endpoint and job processing.
"""

import requests
import time
import json
from app.database import create_db_and_tables, get_session
from app import crud, schemas, models

def setup_test_data():
    """Create test user and workflow for webhook testing."""
    print("Setting up test data...")
    
    # Create database tables
    create_db_and_tables()
    
    session = next(get_session())
    
    # Create test user
    test_user = schemas.UserCreate(
        email="test@example.com",
        password="testpassword123"
    )
    
    # Check if user already exists
    existing_user = crud.get_user_by_email(session, test_user.email)
    if not existing_user:
        user = crud.create_user(session, test_user)
        print(f"✓ Created test user: {user.email}")
    else:
        user = existing_user
        print(f"✓ Using existing test user: {user.email}")
    
    # Create test workflow
    test_workflow = schemas.WorkflowCreate(
        name="Test Webhook Workflow",
        description="Test workflow for webhook functionality",
        definition={
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "webhook",
                    "config": {"method": "POST"}
                }
            ]
        },
        is_active=True
    )
    
    workflow = crud.create_workflow(session, test_workflow, user.id)
    print(f"✓ Created test workflow: {workflow.name}")
    print(f"✓ Webhook URL: {workflow.webhook_url}")
    
    session.close()
    return workflow.webhook_url

def test_webhook_endpoint(webhook_url):
    """Test the webhook endpoint."""
    print(f"\nTesting webhook endpoint...")
    
    # Extract webhook ID from URL
    webhook_id = webhook_url.split("/")[-1]
    
    # Test payload
    test_payload = {
        "test": True,
        "message": "Test webhook trigger",
        "data": {"key": "value"}
    }
    
    try:
        # Make webhook request
        response = requests.post(
            f"http://localhost:8000/webhook/{webhook_id}",
            json=test_payload,
            timeout=5
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✓ Webhook triggered successfully")
            print(f"✓ Job ID: {result['job_id']}")
            print(f"✓ Response: {json.dumps(result, indent=2)}")
            return result['job_id']
        else:
            print(f"✗ Webhook failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the server is running on localhost:8000")
        return None
    except Exception as e:
        print(f"✗ Webhook test failed: {e}")
        return None

def test_job_status(job_id):
    """Test job status endpoint."""
    if not job_id:
        return
        
    print(f"\nTesting job status...")
    
    try:
        response = requests.get(f"http://localhost:8000/jobs/{job_id}/status")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Job status retrieved")
            print(f"✓ Status: {json.dumps(status, indent=2)}")
        else:
            print(f"✗ Job status failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Job status test failed: {e}")

def main():
    """Run webhook tests."""
    print("AutomateOS Webhook Test")
    print("=" * 25)
    
    # Setup test data
    webhook_url = setup_test_data()
    
    # Test webhook endpoint
    job_id = test_webhook_endpoint(webhook_url)
    
    # Test job status
    test_job_status(job_id)
    
    print("\nTest completed!")
    print("Note: Start the server with 'python start_server.py' and worker with 'python start_worker.py' for full functionality")

if __name__ == "__main__":
    main()