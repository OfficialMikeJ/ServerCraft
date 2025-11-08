#!/usr/bin/env python3
"""
Backend API Testing for ServerCraft Panel
Tests registration removal, plugin management, and authentication
"""

import requests
import json
import os
import tempfile
import zipfile
from pathlib import Path
import time

# Get backend URL from frontend env
BACKEND_URL = "https://servercraft-admin.preview.emergentagent.com/api"

class ServerCraftTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_registration_removed(self):
        """Test 1: Verify registration endpoint is removed"""
        print("\n=== Testing Registration Endpoint Removal ===")
        
        try:
            # Test POST to registration endpoint
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com", 
                    "password": "testpassword123"
                }
            )
            
            # Should return 404 or 405 (method not allowed)
            if response.status_code in [404, 405]:
                self.log_result(
                    "Registration Endpoint Removal",
                    True,
                    f"Registration endpoint properly removed (HTTP {response.status_code})"
                )
            else:
                self.log_result(
                    "Registration Endpoint Removal", 
                    False,
                    f"Registration endpoint still accessible (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Registration Endpoint Removal",
                False, 
                f"Error testing registration endpoint: {str(e)}"
            )
    
    def test_login_functionality(self):
        """Test 2: Verify login endpoint still works"""
        print("\n=== Testing Login Functionality ===")
        
        try:
            # First, let's check if there's an admin user in the system
            # We'll try with common admin credentials
            test_credentials = [
                {"email": "admin@servercraft.com", "password": "admin123"},
                {"email": "admin@servercraft.com", "password": "password123"},
                {"email": "admin@servercraft.com", "password": "servercraft123"},
                {"email": "admin@servercraft.com", "password": "admin"},
                {"email": "test@example.com", "password": "password123"},
                {"email": "test@example.com", "password": "testpassword123"},
                {"email": "test@example.com", "password": "test123"},
                {"email": "admin@example.com", "password": "password123"}
            ]
            
            login_success = False
            for creds in test_credentials:
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json=creds
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.admin_token = data["access_token"]
                        login_success = True
                        self.log_result(
                            "Login Functionality",
                            True,
                            f"Login successful with {creds['email']}"
                        )
                        break
                elif response.status_code == 401:
                    continue  # Try next credentials
                else:
                    self.log_result(
                        "Login Functionality",
                        False,
                        f"Unexpected response from login endpoint (HTTP {response.status_code})",
                        {"response": response.text[:200]}
                    )
                    return
            
            if not login_success:
                self.log_result(
                    "Login Functionality",
                    False,
                    "Could not login with test credentials - no admin user found",
                    {"tried_credentials": [c["email"] for c in test_credentials]}
                )
                
        except Exception as e:
            self.log_result(
                "Login Functionality",
                False,
                f"Error testing login: {str(e)}"
            )
    
    def test_plugin_list_endpoint(self):
        """Test 3: GET /api/plugins - List plugins"""
        print("\n=== Testing Plugin List Endpoint ===")
        
        if not self.admin_token:
            self.log_result(
                "Plugin List Endpoint",
                False,
                "Cannot test - no admin token available"
            )
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/plugins", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Plugin List Endpoint",
                        True,
                        f"Plugin list endpoint working (returned {len(data)} plugins)"
                    )
                else:
                    self.log_result(
                        "Plugin List Endpoint",
                        False,
                        "Plugin list endpoint returned non-array response",
                        {"response_type": type(data).__name__}
                    )
            else:
                self.log_result(
                    "Plugin List Endpoint",
                    False,
                    f"Plugin list endpoint failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin List Endpoint",
                False,
                f"Error testing plugin list: {str(e)}"
            )
    
    def test_plugin_upload_validation(self):
        """Test 4: POST /api/plugins/upload - Upload validation"""
        print("\n=== Testing Plugin Upload Validation ===")
        
        if not self.admin_token:
            self.log_result(
                "Plugin Upload Validation",
                False,
                "Cannot test - no admin token available"
            )
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 4a: Upload non-zip file
        try:
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                f.write(b"This is not a zip file")
                f.flush()
                
                with open(f.name, 'rb') as file:
                    files = {'file': ('test.txt', file, 'text/plain')}
                    response = self.session.post(
                        f"{self.base_url}/plugins/upload",
                        headers=headers,
                        files=files
                    )
                
                if response.status_code == 400:
                    self.log_result(
                        "Plugin Upload - Non-ZIP Rejection",
                        True,
                        "Non-zip file properly rejected"
                    )
                else:
                    self.log_result(
                        "Plugin Upload - Non-ZIP Rejection",
                        False,
                        f"Non-zip file not rejected (HTTP {response.status_code})",
                        {"response": response.text[:200]}
                    )
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result(
                "Plugin Upload - Non-ZIP Rejection",
                False,
                f"Error testing non-zip upload: {str(e)}"
            )
        
        # Test 4b: Upload without admin auth
        try:
            # Create a simple zip file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
                with zipfile.ZipFile(f.name, 'w') as zf:
                    zf.writestr("manifest.json", json.dumps({
                        "id": "test-plugin",
                        "name": "Test Plugin",
                        "version": "1.0.0",
                        "description": "Test plugin"
                    }))
                
                with open(f.name, 'rb') as file:
                    files = {'file': ('test-plugin.zip', file, 'application/zip')}
                    # No authorization header
                    response = self.session.post(
                        f"{self.base_url}/plugins/upload",
                        files=files
                    )
                
                if response.status_code in [401, 403]:
                    self.log_result(
                        "Plugin Upload - Auth Required",
                        True,
                        "Upload properly requires authentication"
                    )
                else:
                    self.log_result(
                        "Plugin Upload - Auth Required",
                        False,
                        f"Upload allowed without auth (HTTP {response.status_code})",
                        {"response": response.text[:200]}
                    )
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result(
                "Plugin Upload - Auth Required",
                False,
                f"Error testing upload without auth: {str(e)}"
            )
        
        # Test 4c: Valid zip file upload
        try:
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
                with zipfile.ZipFile(f.name, 'w') as zf:
                    # Create a valid manifest
                    manifest = {
                        "id": "test-plugin-valid",
                        "name": "Valid Test Plugin", 
                        "version": "1.0.0",
                        "description": "A valid test plugin for testing"
                    }
                    zf.writestr("manifest.json", json.dumps(manifest, indent=2))
                    zf.writestr("main.py", "# Test plugin main file")
                
                with open(f.name, 'rb') as file:
                    files = {'file': ('valid-plugin.zip', file, 'application/zip')}
                    response = self.session.post(
                        f"{self.base_url}/plugins/upload",
                        headers=headers,
                        files=files
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.uploaded_plugin_id = data.get("plugin_id")
                        self.log_result(
                            "Plugin Upload - Valid ZIP",
                            True,
                            f"Valid plugin uploaded successfully (ID: {self.uploaded_plugin_id})"
                        )
                    else:
                        self.log_result(
                            "Plugin Upload - Valid ZIP",
                            False,
                            "Upload response indicates failure",
                            {"response": data}
                        )
                else:
                    self.log_result(
                        "Plugin Upload - Valid ZIP",
                        False,
                        f"Valid plugin upload failed (HTTP {response.status_code})",
                        {"response": response.text[:200]}
                    )
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result(
                "Plugin Upload - Valid ZIP",
                False,
                f"Error testing valid zip upload: {str(e)}"
            )
    
    def test_plugin_management(self):
        """Test 5: Plugin enable/disable/delete operations"""
        print("\n=== Testing Plugin Management Operations ===")
        
        if not self.admin_token:
            self.log_result(
                "Plugin Management",
                False,
                "Cannot test - no admin token available"
            )
            return
        
        if not hasattr(self, 'uploaded_plugin_id') or not self.uploaded_plugin_id:
            self.log_result(
                "Plugin Management",
                False,
                "Cannot test - no uploaded plugin available"
            )
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        plugin_id = self.uploaded_plugin_id
        
        # Test enable plugin
        try:
            response = self.session.put(
                f"{self.base_url}/plugins/{plugin_id}/enable",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result(
                        "Plugin Enable",
                        True,
                        "Plugin enabled successfully"
                    )
                else:
                    self.log_result(
                        "Plugin Enable",
                        False,
                        "Enable response indicates failure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Plugin Enable",
                    False,
                    f"Plugin enable failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin Enable",
                False,
                f"Error testing plugin enable: {str(e)}"
            )
        
        # Test disable plugin
        try:
            response = self.session.put(
                f"{self.base_url}/plugins/{plugin_id}/disable",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result(
                        "Plugin Disable",
                        True,
                        "Plugin disabled successfully"
                    )
                else:
                    self.log_result(
                        "Plugin Disable",
                        False,
                        "Disable response indicates failure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Plugin Disable",
                    False,
                    f"Plugin disable failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin Disable",
                False,
                f"Error testing plugin disable: {str(e)}"
            )
        
        # Test delete plugin
        try:
            response = self.session.delete(
                f"{self.base_url}/plugins/{plugin_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result(
                        "Plugin Delete",
                        True,
                        "Plugin deleted successfully"
                    )
                else:
                    self.log_result(
                        "Plugin Delete",
                        False,
                        "Delete response indicates failure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Plugin Delete",
                    False,
                    f"Plugin delete failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin Delete",
                False,
                f"Error testing plugin delete: {str(e)}"
            )
    
    def test_non_admin_access(self):
        """Test 6: Verify non-admin users cannot access plugin endpoints"""
        print("\n=== Testing Non-Admin Access Restrictions ===")
        
        # This test would require creating a non-admin user
        # Since registration is removed, we'll test with invalid/no token
        
        # Test with no token
        try:
            response = self.session.get(f"{self.base_url}/plugins")
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Plugin Access - No Auth",
                    True,
                    "Plugin endpoints properly require authentication"
                )
            else:
                self.log_result(
                    "Plugin Access - No Auth",
                    False,
                    f"Plugin endpoints accessible without auth (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin Access - No Auth",
                False,
                f"Error testing no-auth access: {str(e)}"
            )
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid-token-12345"}
            response = self.session.get(f"{self.base_url}/plugins", headers=headers)
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Plugin Access - Invalid Token",
                    True,
                    "Plugin endpoints properly reject invalid tokens"
                )
            else:
                self.log_result(
                    "Plugin Access - Invalid Token",
                    False,
                    f"Plugin endpoints accept invalid token (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Plugin Access - Invalid Token",
                False,
                f"Error testing invalid token access: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting ServerCraft Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_registration_removed()
        self.test_login_functionality()
        self.test_plugin_list_endpoint()
        self.test_plugin_upload_validation()
        self.test_plugin_management()
        self.test_non_admin_access()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return self.test_results

if __name__ == "__main__":
    tester = ServerCraftTester()
    results = tester.run_all_tests()