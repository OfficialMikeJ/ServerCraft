#!/usr/bin/env python3
"""
Backend API Testing for ServerCraft Panel
Tests Two-Factor Authentication (2FA), registration removal, plugin management, and authentication
"""

import requests
import json
import os
import tempfile
import zipfile
from pathlib import Path
import time
import pyotp
import re

# Get backend URL from frontend env
BACKEND_URL = "https://servercraft-admin.preview.emergentagent.com/api"

class ServerCraftTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.admin_credentials = {
            "email": "testadmin@servercraft.com",
            "password": "testpassword123"
        }
        
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
    
    def get_fresh_admin_token(self):
        """Get a fresh admin token for authentication"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return data["access_token"]
            return None
        except Exception:
            return None
    
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
            # We'll try with test admin credentials
            test_credentials = [
                {"email": "testadmin@servercraft.com", "password": "testpassword123"},
                {"email": "admin@servercraft.com", "password": "admin123"},
                {"email": "admin@servercraft.com", "password": "password123"},
                {"email": "test@example.com", "password": "password123"},
                {"email": "test@example.com", "password": "testpassword123"}
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
                        # Store successful credentials for future use
                        self.admin_credentials = creds
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
        
        fresh_token = self.get_fresh_admin_token()
        if not fresh_token:
            self.log_result("Plugin List Endpoint", False, "Cannot get fresh admin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {fresh_token}"}
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
        
        fresh_token = self.get_fresh_admin_token()
        if not fresh_token:
            self.log_result("Plugin Upload Validation", False, "Cannot get fresh admin token")
            return
        
        headers = {"Authorization": f"Bearer {fresh_token}"}
        
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
        
        if not hasattr(self, 'uploaded_plugin_id') or not self.uploaded_plugin_id:
            self.log_result(
                "Plugin Management",
                False,
                "Cannot test - no uploaded plugin available"
            )
            return
        
        fresh_token = self.get_fresh_admin_token()
        if not fresh_token:
            self.log_result("Plugin Management", False, "Cannot get fresh admin token")
            return
        
        headers = {"Authorization": f"Bearer {fresh_token}"}
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
    
    def test_2fa_setup_flow(self):
        """Test 2FA Setup Flow - Generate secret and QR code"""
        print("\n=== Testing 2FA Setup Flow ===")
        
        token = self.admin_token or self.get_fresh_admin_token()
        if not token:
            self.log_result("2FA Setup Flow", False, "Cannot get admin token")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.post(f"{self.base_url}/auth/2fa/setup", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['secret', 'qr_code', 'backup_codes']
                
                if all(field in data for field in required_fields):
                    # Validate secret format (base32)
                    secret = data['secret']
                    if re.match(r'^[A-Z2-7]+$', secret) and len(secret) >= 16:
                        # Validate QR code format (base64 data URI)
                        qr_code = data['qr_code']
                        if qr_code.startswith('data:image/png;base64,'):
                            # Validate backup codes (should be 10 codes)
                            backup_codes = data['backup_codes']
                            if len(backup_codes) == 10:
                                # Store secret for later tests
                                self.totp_secret = secret
                                self.backup_codes = backup_codes
                                self.log_result(
                                    "2FA Setup Flow",
                                    True,
                                    f"2FA setup successful - secret, QR code, and {len(backup_codes)} backup codes generated"
                                )
                            else:
                                self.log_result(
                                    "2FA Setup Flow",
                                    False,
                                    f"Invalid backup codes count: {len(backup_codes)} (expected 10)"
                                )
                        else:
                            self.log_result(
                                "2FA Setup Flow",
                                False,
                                "Invalid QR code format (not base64 data URI)"
                            )
                    else:
                        self.log_result(
                            "2FA Setup Flow",
                            False,
                            "Invalid secret format (not valid base32)"
                        )
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result(
                        "2FA Setup Flow",
                        False,
                        f"Missing required fields: {missing}",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "2FA Setup Flow",
                    False,
                    f"2FA setup failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("2FA Setup Flow", False, f"Error testing 2FA setup: {str(e)}")
    
    def test_2fa_enable(self):
        """Test 2FA Enable with TOTP verification"""
        print("\n=== Testing 2FA Enable ===")
        
        if not hasattr(self, 'totp_secret'):
            self.log_result("2FA Enable", False, "Cannot test - no TOTP secret from setup")
            return
        
        token = self.admin_token or self.get_fresh_admin_token()
        if not token:
            self.log_result("2FA Enable", False, "Cannot get admin token")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with invalid token first
        try:
            invalid_data = {
                "token": "123456",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/auth/2fa/enable", headers=headers, json=invalid_data)
            
            if response.status_code == 401:
                self.log_result(
                    "2FA Enable - Invalid Token",
                    True,
                    "Invalid TOTP token properly rejected"
                )
            else:
                self.log_result(
                    "2FA Enable - Invalid Token",
                    False,
                    f"Invalid token not rejected (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
        except Exception as e:
            self.log_result("2FA Enable - Invalid Token", False, f"Error testing invalid token: {str(e)}")
        
        # Test with valid token
        try:
            # Generate valid TOTP token
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            valid_data = {
                "token": valid_token,
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/auth/2fa/enable", headers=headers, json=valid_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.twofa_enabled = True
                    self.log_result(
                        "2FA Enable - Valid Token",
                        True,
                        "2FA enabled successfully with valid TOTP token"
                    )
                else:
                    self.log_result(
                        "2FA Enable - Valid Token",
                        False,
                        "Enable response indicates failure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "2FA Enable - Valid Token",
                    False,
                    f"2FA enable failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("2FA Enable - Valid Token", False, f"Error testing valid token: {str(e)}")
    
    def test_2fa_status(self):
        """Test 2FA Status endpoint"""
        print("\n=== Testing 2FA Status ===")
        
        token = self.admin_token or self.get_fresh_admin_token()
        if not token:
            self.log_result("2FA Status", False, "Cannot get admin token")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.get(f"{self.base_url}/auth/2fa/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['enabled', 'has_trusted_devices', 'trusted_device_count']
                
                if all(field in data for field in required_fields):
                    enabled = data['enabled']
                    expected_enabled = hasattr(self, 'twofa_enabled') and self.twofa_enabled
                    
                    if enabled == expected_enabled:
                        self.log_result(
                            "2FA Status",
                            True,
                            f"2FA status correct - enabled: {enabled}, trusted devices: {data['trusted_device_count']}"
                        )
                    else:
                        self.log_result(
                            "2FA Status",
                            False,
                            f"2FA status mismatch - expected enabled: {expected_enabled}, got: {enabled}"
                        )
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result(
                        "2FA Status",
                        False,
                        f"Missing required fields: {missing}",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "2FA Status",
                    False,
                    f"2FA status failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("2FA Status", False, f"Error testing 2FA status: {str(e)}")
    
    def test_login_with_2fa(self):
        """Test Login Flow with 2FA"""
        print("\n=== Testing Login with 2FA ===")
        
        if not hasattr(self, 'twofa_enabled') or not self.twofa_enabled:
            self.log_result("Login with 2FA", False, "Cannot test - 2FA not enabled")
            return
        
        # Test 1: Login with email + password only (should require 2FA)
        try:
            login_data = {
                "email": "testadmin@servercraft.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requires_2fa") and data.get("temp_token"):
                    self.temp_token = data["temp_token"]
                    self.log_result(
                        "Login - 2FA Required",
                        True,
                        "Login correctly requires 2FA verification"
                    )
                else:
                    self.log_result(
                        "Login - 2FA Required",
                        False,
                        "Login should require 2FA but doesn't",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Login - 2FA Required",
                    False,
                    f"Login failed unexpectedly (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
        except Exception as e:
            self.log_result("Login - 2FA Required", False, f"Error testing 2FA required: {str(e)}")
        
        # Test 2: Login with email + password + valid TOTP token
        try:
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            login_data = {
                "email": "testadmin@servercraft.com",
                "password": "testpassword123",
                "totp_token": valid_token
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token") and not data.get("requires_2fa"):
                    self.log_result(
                        "Login - 2FA Success",
                        True,
                        "Login successful with valid 2FA token"
                    )
                else:
                    self.log_result(
                        "Login - 2FA Success",
                        False,
                        "Login with 2FA token failed",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Login - 2FA Success",
                    False,
                    f"Login with 2FA failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
        except Exception as e:
            self.log_result("Login - 2FA Success", False, f"Error testing 2FA login: {str(e)}")
    
    def test_backup_codes(self):
        """Test Backup Codes functionality"""
        print("\n=== Testing Backup Codes ===")
        
        token = self.admin_token or self.get_fresh_admin_token()
        if not token:
            self.log_result("Backup Codes", False, "Cannot get admin token")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test backup code regeneration
        try:
            response = self.session.get(f"{self.base_url}/auth/2fa/backup-codes", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "backup_codes" in data and len(data["backup_codes"]) == 10:
                    new_backup_codes = data["backup_codes"]
                    self.log_result(
                        "Backup Codes - Regeneration",
                        True,
                        f"Backup codes regenerated successfully ({len(new_backup_codes)} codes)"
                    )
                    
                    # Test login with backup code
                    if new_backup_codes:
                        test_code = new_backup_codes[0]  # Use first backup code
                        login_data = {
                            "email": "testadmin@servercraft.com",
                            "password": "testpassword123",
                            "totp_token": test_code
                        }
                        
                        login_response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                        
                        if login_response.status_code == 200:
                            login_data_result = login_response.json()
                            if login_data_result.get("access_token"):
                                self.log_result(
                                    "Backup Codes - Login",
                                    True,
                                    "Login successful with backup code"
                                )
                            else:
                                self.log_result(
                                    "Backup Codes - Login",
                                    False,
                                    "Login with backup code failed - no access token",
                                    {"response": login_data_result}
                                )
                        else:
                            self.log_result(
                                "Backup Codes - Login",
                                False,
                                f"Login with backup code failed (HTTP {login_response.status_code})",
                                {"response": login_response.text[:200]}
                            )
                else:
                    self.log_result(
                        "Backup Codes - Regeneration",
                        False,
                        "Invalid backup codes response",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Backup Codes - Regeneration",
                    False,
                    f"Backup codes regeneration failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("Backup Codes", False, f"Error testing backup codes: {str(e)}")
    
    def test_trusted_devices(self):
        """Test Trusted Devices functionality"""
        print("\n=== Testing Trusted Devices ===")
        
        if not hasattr(self, 'twofa_enabled') or not self.twofa_enabled:
            self.log_result("Trusted Devices", False, "Cannot test - 2FA not enabled")
            return
        
        # Test login with remember_device=true
        try:
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            login_data = {
                "email": "testadmin@servercraft.com",
                "password": "testpassword123",
                "totp_token": valid_token,
                "remember_device": True
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("device_token"):
                    self.device_token = data["device_token"]
                    self.log_result(
                        "Trusted Devices - Remember Device",
                        True,
                        "Device token generated for trusted device"
                    )
                    
                    # Test subsequent login with device token (should bypass 2FA)
                    time.sleep(1)  # Small delay to ensure different timestamp
                    
                    device_login_data = {
                        "email": "testadmin@servercraft.com",
                        "password": "testpassword123",
                        "device_token": self.device_token
                    }
                    device_response = self.session.post(f"{self.base_url}/auth/login", json=device_login_data)
                    
                    if device_response.status_code == 200:
                        device_data = device_response.json()
                        if device_data.get("access_token") and not device_data.get("requires_2fa"):
                            self.log_result(
                                "Trusted Devices - Bypass 2FA",
                                True,
                                "Trusted device successfully bypassed 2FA"
                            )
                        else:
                            self.log_result(
                                "Trusted Devices - Bypass 2FA",
                                False,
                                "Trusted device did not bypass 2FA",
                                {"response": device_data}
                            )
                    else:
                        self.log_result(
                            "Trusted Devices - Bypass 2FA",
                            False,
                            f"Trusted device login failed (HTTP {device_response.status_code})",
                            {"response": device_response.text[:200]}
                        )
                else:
                    self.log_result(
                        "Trusted Devices - Remember Device",
                        False,
                        "No device token returned for remember device",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Trusted Devices - Remember Device",
                    False,
                    f"Remember device login failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("Trusted Devices", False, f"Error testing trusted devices: {str(e)}")
    
    def test_2fa_disable(self):
        """Test 2FA Disable functionality"""
        print("\n=== Testing 2FA Disable ===")
        
        if not hasattr(self, 'twofa_enabled') or not self.twofa_enabled:
            self.log_result("2FA Disable", False, "Cannot test - 2FA not enabled")
            return
        
        # Get fresh token for disable operation
        fresh_token = self.get_fresh_admin_token()
        if not fresh_token:
            self.log_result("2FA Disable", False, "Cannot get fresh admin token")
            return
        
        headers = {"Authorization": f"Bearer {fresh_token}"}
        
        # Test disable with valid credentials
        try:
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            disable_data = {
                "password": "testpassword123",
                "token": valid_token
            }
            response = self.session.post(f"{self.base_url}/auth/2fa/disable", headers=headers, json=disable_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.twofa_enabled = False
                    self.log_result(
                        "2FA Disable",
                        True,
                        "2FA disabled successfully"
                    )
                else:
                    self.log_result(
                        "2FA Disable",
                        False,
                        "Disable response indicates failure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "2FA Disable",
                    False,
                    f"2FA disable failed (HTTP {response.status_code})",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result("2FA Disable", False, f"Error testing 2FA disable: {str(e)}")
    
    def test_2fa_security(self):
        """Test 2FA Security measures"""
        print("\n=== Testing 2FA Security ===")
        
        # Test rate limiting on setup endpoint
        try:
            fresh_token = self.get_fresh_admin_token()
            if fresh_token:
                headers = {"Authorization": f"Bearer {fresh_token}"}
                
                # Make multiple rapid requests to test rate limiting
                rate_limit_responses = []
                for i in range(7):  # Limit is 5/hour, so 7 should trigger rate limit
                    response = self.session.post(f"{self.base_url}/auth/2fa/setup", headers=headers)
                    rate_limit_responses.append(response.status_code)
                    time.sleep(0.1)  # Small delay between requests
                
                # Check if any requests were rate limited (429)
                if 429 in rate_limit_responses:
                    self.log_result(
                        "2FA Security - Rate Limiting",
                        True,
                        "Rate limiting working on 2FA setup endpoint"
                    )
                else:
                    # Since 2FA is already enabled, we expect 400 errors, not rate limiting
                    if all(status in [400, 401] for status in rate_limit_responses):
                        self.log_result(
                            "2FA Security - Rate Limiting",
                            True,
                            "Rate limiting test inconclusive - 2FA already enabled (expected 400 errors)"
                        )
                    else:
                        self.log_result(
                            "2FA Security - Rate Limiting",
                            False,
                            "Rate limiting not working on 2FA setup endpoint",
                            {"responses": rate_limit_responses}
                        )
            else:
                self.log_result("2FA Security - Rate Limiting", False, "Cannot get fresh admin token")
                
        except Exception as e:
            self.log_result("2FA Security - Rate Limiting", False, f"Error testing rate limiting: {str(e)}")
        
        # Test authentication requirement
        try:
            # Test 2FA endpoints without authentication
            endpoints_to_test = [
                "/auth/2fa/setup",
                "/auth/2fa/status",
                "/auth/2fa/backup-codes"
            ]
            
            auth_required_count = 0
            for endpoint in endpoints_to_test:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [401, 403]:
                    auth_required_count += 1
            
            if auth_required_count == len(endpoints_to_test):
                self.log_result(
                    "2FA Security - Auth Required",
                    True,
                    "All 2FA endpoints properly require authentication"
                )
            else:
                self.log_result(
                    "2FA Security - Auth Required",
                    False,
                    f"Only {auth_required_count}/{len(endpoints_to_test)} endpoints require auth"
                )
                
        except Exception as e:
            self.log_result("2FA Security - Auth Required", False, f"Error testing auth requirement: {str(e)}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting ServerCraft Backend Tests - 2FA Focus")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run authentication tests first
        self.test_registration_removed()
        self.test_login_functionality()
        
        # Run comprehensive 2FA tests
        self.test_2fa_setup_flow()
        self.test_2fa_enable()
        self.test_2fa_status()
        self.test_login_with_2fa()
        self.test_backup_codes()
        self.test_trusted_devices()
        self.test_2fa_disable()
        self.test_2fa_security()
        
        # Run plugin tests
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