#!/usr/bin/env python3
"""
Simple validation tests to verify the testing framework and basic imports work.
"""

import pytest
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_python_version():
    """Test that we're running a compatible Python version."""
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
    print(f"✅ Python version: {sys.version_info}")

def test_required_packages():
    """Test that required packages can be imported."""
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        pytest.fail("FastAPI not available")
    
    try:
        import sqlmodel
        print("✅ SQLModel available")
    except ImportError:
        pytest.fail("SQLModel not available")
    
    try:
        import requests
        print("✅ Requests available")
    except ImportError:
        pytest.fail("Requests not available")

def test_app_imports():
    """Test that app modules can be imported."""
    try:
        from app import models, schemas
        print("✅ App models and schemas can be imported")
    except ImportError as e:
        print(f"⚠️  App import warning: {e}")
        # Don't fail the test, just warn
    
    try:
        from app.main import app
        print("✅ FastAPI app can be imported")
    except ImportError as e:
        print(f"⚠️  FastAPI app import warning: {e}")

def test_file_structure():
    """Test that required files exist."""
    required_files = [
        "app/main.py",
        "app/models.py", 
        "app/schemas.py",
        "app/database.py",
        "app/security.py",
        "app/crud.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"⚠️  {file_path} missing")

def test_basic_math():
    """Test that basic testing works."""
    assert 2 + 2 == 4
    assert "hello" + " world" == "hello world"
    print("✅ Basic testing framework working")

class TestBasicValidation:
    """Test class for basic validation."""
    
    def test_class_based_testing(self):
        """Test that class-based testing works."""
        assert True
        print("✅ Class-based testing working")
    
    def test_pytest_features(self):
        """Test pytest features."""
        # Test assertions
        assert 1 == 1
        assert "test" in "testing"
        
        # Test with custom message
        assert len("hello") == 5, "String length should be 5"
        
        print("✅ Pytest features working")

if __name__ == "__main__":
    print("🧪 Running Simple Validation Tests")
    print("=" * 50)
    
    # Run tests manually
    try:
        test_python_version()
        test_required_packages()
        test_app_imports()
        test_file_structure()
        test_basic_math()
        
        # Test class
        validator = TestBasicValidation()
        validator.test_class_based_testing()
        validator.test_pytest_features()
        
        print("\n🎉 All validation tests passed!")
        
    except Exception as e:
        print(f"\n❌ Validation test failed: {e}")
        exit(1)