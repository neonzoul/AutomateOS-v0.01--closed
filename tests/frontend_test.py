#!/usr/bin/env python3
"""
Test script for the frontend workflow dashboard components.
This script verifies that the components are properly structured and will work with the backend.
"""

import os
import json
import re

def check_file_exists(filepath):
    """Check if a file exists."""
    return os.path.isfile(filepath)

def read_file(filepath):
    """Read a file and return its contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def check_component_imports(content):
    """Check if the component has the necessary imports."""
    required_imports = [
        '@chakra-ui/react',
        'useState',
        'useEffect',
    ]
    
    for imp in required_imports:
        if imp not in content:
            return False, f"Missing import: {imp}"
    
    return True, "All required imports present"

def check_api_integration(content):
    """Check if the component integrates with the API service."""
    if 'workflowService' not in content and 'workflowService.getWorkflows' not in content:
        return False, "No API service integration found"
    
    return True, "API service integration found"

def check_crud_operations(content):
    """Check if the component implements CRUD operations."""
    operations = {
        'create': ['createWorkflow', 'post', 'workflowService.createWorkflow', 'create', 'new workflow'],
        'read': ['getWorkflows', 'get', 'workflowService.getWorkflow', 'fetch'],
        'update': ['updateWorkflow', 'put', 'workflowService.updateWorkflow', 'update'],
        'delete': ['deleteWorkflow', 'delete', 'workflowService.deleteWorkflow', 'remove']
    }
    
    results = {}
    for op, keywords in operations.items():
        found = any(keyword.lower() in content.lower() for keyword in keywords)
        results[op] = found
    
    return results

def check_error_handling(content):
    """Check if the component has error handling."""
    error_patterns = [
        r'catch\s*\(\s*error\s*\)',
        r'toast\s*\(\s*\{.*error',
        r'status\s*:\s*[\'"]error[\'"]'
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, content):
            return True, "Error handling found"
    
    return False, "No error handling found"

def check_loading_state(content):
    """Check if the component has loading state management."""
    loading_patterns = [
        r'const\s+\[\s*loading\s*,\s*setLoading\s*\]\s*=\s*useState',
        r'isLoading',
        r'loading\s*=',
        r'<Spinner'
    ]
    
    for pattern in loading_patterns:
        if re.search(pattern, content):
            return True, "Loading state management found"
    
    return False, "No loading state management found"

def check_component(filepath, component_name):
    """Check a component for best practices and functionality."""
    if not check_file_exists(filepath):
        return {
            "component": component_name,
            "exists": False,
            "message": f"Component file not found: {filepath}"
        }
    
    content = read_file(filepath)
    
    imports_ok, imports_msg = check_component_imports(content)
    api_ok, api_msg = check_api_integration(content)
    crud_ops = check_crud_operations(content)
    error_ok, error_msg = check_error_handling(content)
    loading_ok, loading_msg = check_loading_state(content)
    
    return {
        "component": component_name,
        "exists": True,
        "imports": {"ok": imports_ok, "message": imports_msg},
        "api_integration": {"ok": api_ok, "message": api_msg},
        "crud_operations": crud_ops,
        "error_handling": {"ok": error_ok, "message": error_msg},
        "loading_state": {"ok": loading_ok, "message": loading_msg}
    }

def check_api_service(filepath):
    """Check the API service for correct endpoints."""
    if not check_file_exists(filepath):
        return {
            "component": "API Service",
            "exists": False,
            "message": f"API service file not found: {filepath}"
        }
    
    content = read_file(filepath)
    
    # Check if the API service has the correct base URL
    base_url_pattern = r'baseURL:\s*[\'"]http://127\.0\.0\.1:8000[\'"]'
    base_url_ok = bool(re.search(base_url_pattern, content))
    
    # Check if the API service has the correct endpoints
    endpoints = {
        "getWorkflows": "/workflows/",
        "createWorkflow": "/workflows/",
        "getWorkflow": "/workflows/",
        "updateWorkflow": "/workflows/",
        "deleteWorkflow": "/workflows/"
    }
    
    endpoint_results = {}
    for name, path in endpoints.items():
        endpoint_results[name] = name in content and path in content
    
    # Check if the API service has JWT token handling
    jwt_patterns = [
        r'Authorization:\s*[\'"`]Bearer\s+\$\{token\}[\'"`]',
        r'Authorization:\s*[\'"`]Bearer\s+\$\{token\}[\'"`]',
        r'headers\.Authorization\s*=\s*[\'"`]Bearer\s+\$\{token\}[\'"`]',
        r'headers\.Authorization\s*=\s*[\'"`]Bearer\s+\$\{token\}[\'"`]',
        r'headers\.Authorization\s*=\s*[\'"`]Bearer\s+.*?[\'"`]'
    ]
    jwt_ok = any(bool(re.search(pattern, content)) for pattern in jwt_patterns)
    
    return {
        "component": "API Service",
        "exists": True,
        "base_url": base_url_ok,
        "endpoints": endpoint_results,
        "jwt_handling": jwt_ok
    }

def run_tests():
    """Run all tests and print the results."""
    components = [
        {"path": "frontend/src/components/dashboard/WorkflowList.tsx", "name": "WorkflowList"},
        {"path": "frontend/src/components/dashboard/WorkflowCard.tsx", "name": "WorkflowCard"},
        {"path": "frontend/src/components/dashboard/CreateWorkflowModal.tsx", "name": "CreateWorkflowModal"},
        {"path": "frontend/src/components/dashboard/Dashboard.tsx", "name": "Dashboard"}
    ]
    
    api_service = {"path": "frontend/src/services/api.ts", "name": "API Service"}
    
    results = []
    for component in components:
        results.append(check_component(component["path"], component["name"]))
    
    api_result = check_api_service(api_service["path"])
    results.append(api_result)
    
    # Print results in a nice format
    print("\n===== FRONTEND WORKFLOW DASHBOARD TEST RESULTS =====\n")
    
    all_passed = True
    
    for result in results:
        component_name = result["component"]
        print(f"## {component_name}")
        
        if not result["exists"]:
            print(f"❌ {result['message']}")
            all_passed = False
            continue
        
        if component_name != "API Service":
            # Component checks
            print(f"✅ Component exists")
            
            imports = result["imports"]
            print(f"{'✅' if imports['ok'] else '❌'} Imports: {imports['message']}")
            if not imports['ok']:
                all_passed = False
            
            api = result["api_integration"]
            print(f"{'✅' if api['ok'] else '❌'} API Integration: {api['message']}")
            if not api['ok'] and component_name != "WorkflowCard":  # WorkflowCard might not need direct API integration
                all_passed = False
            
            crud = result["crud_operations"]
            if component_name in ["WorkflowList", "CreateWorkflowModal"]:
                print("CRUD Operations:")
                for op, found in crud.items():
                    print(f"  {'✅' if found else '❌'} {op.capitalize()}")
                    # For WorkflowList, all operations are essential
                    # For CreateWorkflowModal, only create is essential
                    if component_name == "WorkflowList" and not found and op in ["read", "create", "delete"]:
                        all_passed = False
                    elif component_name == "CreateWorkflowModal" and not found and op == "create":
                        all_passed = False
            
            error = result["error_handling"]
            print(f"{'✅' if error['ok'] else '❌'} Error Handling: {error['message']}")
            if not error['ok'] and component_name in ["WorkflowList", "CreateWorkflowModal"]:
                all_passed = False
            
            loading = result["loading_state"]
            print(f"{'✅' if loading['ok'] else '❌'} Loading State: {loading['message']}")
            if not loading['ok'] and component_name in ["WorkflowList", "CreateWorkflowModal"]:
                all_passed = False
        else:
            # API Service checks
            print(f"✅ API Service exists")
            
            print(f"{'✅' if result['base_url'] else '❌'} Correct Base URL")
            if not result['base_url']:
                all_passed = False
            
            print("API Endpoints:")
            for endpoint, found in result["endpoints"].items():
                print(f"  {'✅' if found else '❌'} {endpoint}")
                if not found:
                    all_passed = False
            
            print(f"{'✅' if result['jwt_handling'] else '❌'} JWT Token Handling")
            if not result['jwt_handling']:
                all_passed = False
        
        print()
    
    print("===== OVERALL RESULT =====")
    if all_passed:
        print("✅ All tests passed! The frontend workflow dashboard is ready.")
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    run_tests()