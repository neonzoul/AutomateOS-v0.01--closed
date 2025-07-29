#!/usr/bin/env python3
"""
Frontend component tests for critical user flows.
Tests React components using a Python-based approach to verify component structure and functionality.
"""

import os
import re
import json
from typing import Dict, List, Any

class FrontendComponentTester:
    """Test frontend React components for critical functionality."""
    
    def __init__(self):
        self.frontend_path = "frontend/src"
        self.test_results = []
    
    def read_file(self, filepath: str) -> str:
        """Read a file and return its contents."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def test_component_exists(self, component_path: str) -> bool:
        """Test if a component file exists."""
        return os.path.isfile(component_path)
    
    def test_component_imports(self, content: str, required_imports: List[str]) -> Dict[str, Any]:
        """Test if component has required imports."""
        results = {}
        for imp in required_imports:
            results[imp] = imp in content
        return results
    
    def test_component_exports(self, content: str, component_name: str) -> bool:
        """Test if component has proper export."""
        export_patterns = [
            f"export default {component_name}",
            f"export {{ {component_name} }}",
            f"export const {component_name}",
            f"export function {component_name}"
        ]
        return any(pattern in content for pattern in export_patterns)
    
    def test_hooks_usage(self, content: str, expected_hooks: List[str]) -> Dict[str, bool]:
        """Test if component uses expected React hooks."""
        results = {}
        for hook in expected_hooks:
            # Look for hook usage patterns
            patterns = [
                f"const \\[.*\\] = {hook}\\(",
                f"{hook}\\(",
                f"= {hook}\\("
            ]
            results[hook] = any(re.search(pattern, content) for pattern in patterns)
        return results
    
    def test_api_integration(self, content: str) -> Dict[str, bool]:
        """Test if component integrates with API service."""
        api_patterns = {
            "api_import": "from.*api",
            "api_service": "workflowService",
            "axios_usage": "axios\\.",
            "api_calls": "\\.(get|post|put|delete)\\("
        }
        
        results = {}
        for name, pattern in api_patterns.items():
            results[name] = bool(re.search(pattern, content))
        return results
    
    def test_error_handling(self, content: str) -> Dict[str, bool]:
        """Test if component has error handling."""
        error_patterns = {
            "try_catch": "try\\s*\\{.*catch",
            "error_state": "error.*useState|useState.*error",
            "toast_error": "toast\\(.*error|status.*error",
            "error_display": "error.*&&|\\{error"
        }
        
        results = {}
        for name, pattern in error_patterns.items():
            results[name] = bool(re.search(pattern, content, re.DOTALL))
        return results
    
    def test_loading_states(self, content: str) -> Dict[str, bool]:
        """Test if component has loading state management."""
        loading_patterns = {
            "loading_state": "loading.*useState|useState.*loading",
            "loading_display": "loading.*&&|\\{loading|<Spinner|isLoading",
            "loading_text": "Loading|loading"
        }
        
        results = {}
        for name, pattern in loading_patterns.items():
            results[name] = bool(re.search(pattern, content, re.IGNORECASE))
        return results
    
    def test_form_validation(self, content: str) -> Dict[str, bool]:
        """Test if component has form validation."""
        validation_patterns = {
            "form_validation": "validation|validate|isValid",
            "required_fields": "required|isRequired",
            "error_messages": "errorMessage|error.*message",
            "form_state": "formData|form.*State"
        }
        
        results = {}
        for name, pattern in validation_patterns.items():
            results[name] = bool(re.search(pattern, content, re.IGNORECASE))
        return results

class TestWorkflowListComponent:
    """Test the WorkflowList component."""
    
    def __init__(self):
        self.tester = FrontendComponentTester()
        self.component_path = "frontend/src/components/dashboard/WorkflowList.tsx"
    
    def test_component_structure(self):
        """Test WorkflowList component structure."""
        if not self.tester.test_component_exists(self.component_path):
            return {"error": "Component file not found"}
        
        content = self.tester.read_file(self.component_path)
        
        results = {
            "exists": True,
            "imports": self.tester.test_component_imports(content, [
                "@chakra-ui/react",
                "useState",
                "useEffect",
                "workflowService"
            ]),
            "exports": self.tester.test_component_exports(content, "WorkflowList"),
            "hooks": self.tester.test_hooks_usage(content, ["useState", "useEffect"]),
            "api_integration": self.tester.test_api_integration(content),
            "error_handling": self.tester.test_error_handling(content),
            "loading_states": self.tester.test_loading_states(content)
        }
        
        return results
    
    def test_workflow_crud_operations(self):
        """Test if WorkflowList supports CRUD operations."""
        if not self.tester.test_component_exists(self.component_path):
            return {"error": "Component file not found"}
        
        content = self.tester.read_file(self.component_path)
        
        crud_patterns = {
            "fetch_workflows": "getWorkflows|fetchWorkflows",
            "create_workflow": "createWorkflow|addWorkflow",
            "delete_workflow": "deleteWorkflow|removeWorkflow",
            "edit_workflow": "editWorkflow|updateWorkflow"
        }
        
        results = {}
        for operation, pattern in crud_patterns.items():
            results[operation] = bool(re.search(pattern, content, re.IGNORECASE))
        
        return results

class TestWorkflowCardComponent:
    """Test the WorkflowCard component."""
    
    def __init__(self):
        self.tester = FrontendComponentTester()
        self.component_path = "frontend/src/components/dashboard/WorkflowCard.tsx"
    
    def test_component_structure(self):
        """Test WorkflowCard component structure."""
        if not self.tester.test_component_exists(self.component_path):
            return {"error": "Component file not found"}
        
        content = self.tester.read_file(self.component_path)
        
        results = {
            "exists": True,
            "imports": self.tester.test_component_imports(content, [
                "@chakra-ui/react",
                "react"
            ]),
            "exports": self.tester.test_component_exports(content, "WorkflowCard"),
            "props_interface": "interface.*Props|type.*Props" in content,
            "workflow_display": bool(re.search("workflow\\.(name|description|status)", content)),
            "action_buttons": bool(re.search("Button.*edit|Button.*delete|IconButton", content, re.IGNORECASE))
        }
        
        return results

class TestCreateWorkflowModal:
    """Test the CreateWorkflowModal component."""
    
    def __init__(self):
        self.tester = FrontendComponentTester()
        self.component_path = "frontend/src/components/dashboard/CreateWorkflowModal.tsx"
    
    def test_component_structure(self):
        """Test CreateWorkflowModal component structure."""
        if not self.tester.test_component_exists(self.component_path):
            return {"error": "Component file not found"}
        
        content = self.tester.read_file(self.component_path)
        
        results = {
            "exists": True,
            "imports": self.tester.test_component_imports(content, [
                "@chakra-ui/react",
                "useState"
            ]),
            "exports": self.tester.test_component_exports(content, "CreateWorkflowModal"),
            "modal_components": bool(re.search("Modal|ModalOverlay|ModalContent", content)),
            "form_elements": bool(re.search("Input|Textarea|FormControl", content)),
            "form_validation": self.tester.test_form_validation(content),
            "api_integration": self.tester.test_api_integration(content),
            "error_handling": self.tester.test_error_handling(content)
        }
        
        return results

class TestAuthComponents:
    """Test authentication components."""
    
    def __init__(self):
        self.tester = FrontendComponentTester()
        self.login_path = "frontend/src/components/auth/LoginForm.tsx"
        self.register_path = "frontend/src/components/auth/RegisterForm.tsx"
    
    def test_login_form(self):
        """Test LoginForm component."""
        if not self.tester.test_component_exists(self.login_path):
            return {"error": "LoginForm component not found"}
        
        content = self.tester.read_file(self.login_path)
        
        results = {
            "exists": True,
            "form_elements": bool(re.search("Input.*email|Input.*password", content, re.IGNORECASE)),
            "form_validation": self.tester.test_form_validation(content),
            "submit_handler": bool(re.search("onSubmit|handleSubmit", content)),
            "api_integration": self.tester.test_api_integration(content),
            "error_handling": self.tester.test_error_handling(content),
            "loading_states": self.tester.test_loading_states(content)
        }
        
        return results
    
    def test_register_form(self):
        """Test RegisterForm component."""
        if not self.tester.test_component_exists(self.register_path):
            return {"error": "RegisterForm component not found"}
        
        content = self.tester.read_file(self.register_path)
        
        results = {
            "exists": True,
            "form_elements": bool(re.search("Input.*email|Input.*password", content, re.IGNORECASE)),
            "password_confirmation": bool(re.search("confirm.*password|password.*confirm", content, re.IGNORECASE)),
            "form_validation": self.tester.test_form_validation(content),
            "submit_handler": bool(re.search("onSubmit|handleSubmit", content)),
            "api_integration": self.tester.test_api_integration(content),
            "error_handling": self.tester.test_error_handling(content)
        }
        
        return results

class TestAPIService:
    """Test the API service layer."""
    
    def __init__(self):
        self.tester = FrontendComponentTester()
        self.api_path = "frontend/src/services/api.ts"
    
    def test_api_service_structure(self):
        """Test API service structure and endpoints."""
        if not self.tester.test_component_exists(self.api_path):
            return {"error": "API service file not found"}
        
        content = self.tester.read_file(self.api_path)
        
        # Test for required API endpoints
        endpoints = {
            "auth_endpoints": bool(re.search("login|register|token", content, re.IGNORECASE)),
            "workflow_endpoints": bool(re.search("workflows|getWorkflows|createWorkflow", content)),
            "crud_operations": bool(re.search("get|post|put|delete", content, re.IGNORECASE)),
            "base_url": bool(re.search("baseURL|BASE_URL", content)),
            "axios_config": bool(re.search("axios\\.create|axios\\.defaults", content))
        }
        
        # Test for JWT token handling
        jwt_handling = {
            "token_storage": bool(re.search("localStorage|sessionStorage|token", content)),
            "auth_headers": bool(re.search("Authorization|Bearer", content)),
            "interceptors": bool(re.search("interceptors|request\\.use|response\\.use", content))
        }
        
        results = {
            "exists": True,
            "endpoints": endpoints,
            "jwt_handling": jwt_handling,
            "error_handling": self.tester.test_error_handling(content)
        }
        
        return results

def run_frontend_tests():
    """Run all frontend component tests."""
    print("🧪 Running Frontend Component Tests")
    print("=" * 50)
    
    # Test WorkflowList component
    print("\n1. Testing WorkflowList Component...")
    workflow_list_test = TestWorkflowListComponent()
    workflow_list_results = workflow_list_test.test_component_structure()
    crud_results = workflow_list_test.test_workflow_crud_operations()
    
    if "error" in workflow_list_results:
        print(f"❌ {workflow_list_results['error']}")
    else:
        print("✅ WorkflowList component exists")
        print(f"   Imports: {sum(workflow_list_results['imports'].values())}/{len(workflow_list_results['imports'])} ✓")
        print(f"   Hooks: {sum(workflow_list_results['hooks'].values())}/{len(workflow_list_results['hooks'])} ✓")
        print(f"   API Integration: {sum(workflow_list_results['api_integration'].values())}/{len(workflow_list_results['api_integration'])} ✓")
        print(f"   CRUD Operations: {sum(crud_results.values())}/{len(crud_results)} ✓")
    
    # Test WorkflowCard component
    print("\n2. Testing WorkflowCard Component...")
    workflow_card_test = TestWorkflowCardComponent()
    workflow_card_results = workflow_card_test.test_component_structure()
    
    if "error" in workflow_card_results:
        print(f"❌ {workflow_card_results['error']}")
    else:
        print("✅ WorkflowCard component exists")
        print(f"   Props Interface: {'✅' if workflow_card_results['props_interface'] else '❌'}")
        print(f"   Workflow Display: {'✅' if workflow_card_results['workflow_display'] else '❌'}")
        print(f"   Action Buttons: {'✅' if workflow_card_results['action_buttons'] else '❌'}")
    
    # Test CreateWorkflowModal component
    print("\n3. Testing CreateWorkflowModal Component...")
    modal_test = TestCreateWorkflowModal()
    modal_results = modal_test.test_component_structure()
    
    if "error" in modal_results:
        print(f"❌ {modal_results['error']}")
    else:
        print("✅ CreateWorkflowModal component exists")
        print(f"   Modal Components: {'✅' if modal_results['modal_components'] else '❌'}")
        print(f"   Form Elements: {'✅' if modal_results['form_elements'] else '❌'}")
        print(f"   Form Validation: {sum(modal_results['form_validation'].values())}/{len(modal_results['form_validation'])} ✓")
    
    # Test Auth components
    print("\n4. Testing Authentication Components...")
    auth_test = TestAuthComponents()
    login_results = auth_test.test_login_form()
    register_results = auth_test.test_register_form()
    
    if "error" in login_results:
        print(f"❌ LoginForm: {login_results['error']}")
    else:
        print("✅ LoginForm component exists")
        print(f"   Form Elements: {'✅' if login_results['form_elements'] else '❌'}")
        print(f"   Form Validation: {sum(login_results['form_validation'].values())}/{len(login_results['form_validation'])} ✓")
    
    if "error" in register_results:
        print(f"❌ RegisterForm: {register_results['error']}")
    else:
        print("✅ RegisterForm component exists")
        print(f"   Form Elements: {'✅' if register_results['form_elements'] else '❌'}")
        print(f"   Password Confirmation: {'✅' if register_results['password_confirmation'] else '❌'}")
    
    # Test API service
    print("\n5. Testing API Service...")
    api_test = TestAPIService()
    api_results = api_test.test_api_service_structure()
    
    if "error" in api_results:
        print(f"❌ {api_results['error']}")
    else:
        print("✅ API service exists")
        print(f"   Endpoints: {sum(api_results['endpoints'].values())}/{len(api_results['endpoints'])} ✓")
        print(f"   JWT Handling: {sum(api_results['jwt_handling'].values())}/{len(api_results['jwt_handling'])} ✓")
    
    print("\n" + "=" * 50)
    print("🎉 Frontend component tests completed!")
    
    # Calculate overall score
    all_results = [
        workflow_list_results, crud_results, workflow_card_results,
        modal_results, login_results, register_results, api_results
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for result in all_results:
        if isinstance(result, dict) and "error" not in result:
            for key, value in result.items():
                if isinstance(value, dict):
                    total_tests += len(value)
                    passed_tests += sum(1 for v in value.values() if v)
                elif isinstance(value, bool):
                    total_tests += 1
                    passed_tests += 1 if value else 0
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    return success_rate > 70  # Consider 70% as passing

if __name__ == "__main__":
    success = run_frontend_tests()
    if not success:
        exit(1)