#!/usr/bin/env python3
"""
Focused 2FA Testing for ServerCraft Panel
Tests the complete 2FA flow step by step
"""

import requests
import json
import pyotp
import time

# Get backend URL from frontend env
BACKEND_URL = "https://servercraft-admin.preview.emergentagent.com/api"

class TwoFactorTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.totp_secret = None
        self.backup_codes = []
        self.device_token = None
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
    
    def test_initial_login(self):
        """Test initial login to get admin token"""
        print("\n=== Testing Initial Login ===")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "testadmin@servercraft.com",
                    "password": "testpassword123"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.admin_token = data["access_token"]
                    self.log_result("Initial Login", True, "Login successful, got access token")
                    return True
                elif data.get("requires_2fa"):
                    self.log_result("Initial Login", False, "2FA already enabled - need to reset first")
                    return False
                else:
                    self.log_result("Initial Login", False, "No access token in response", {"response": data})
                    return False
            else:
                self.log_result("Initial Login", False, f"Login failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("Initial Login", False, f"Error during login: {str(e)}")
            return False
    
    def test_2fa_setup(self):
        """Test 2FA setup - generate secret and QR code"""
        print("\n=== Testing 2FA Setup ===")
        
        if not self.admin_token:
            self.log_result("2FA Setup", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/auth/2fa/setup", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if all(field in data for field in ['secret', 'qr_code', 'backup_codes']):
                    self.totp_secret = data['secret']
                    self.backup_codes = data['backup_codes']
                    self.log_result("2FA Setup", True, f"2FA setup successful - got secret and {len(self.backup_codes)} backup codes")
                    return True
                else:
                    self.log_result("2FA Setup", False, "Missing required fields in response", {"response": data})
                    return False
            else:
                self.log_result("2FA Setup", False, f"2FA setup failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("2FA Setup", False, f"Error during 2FA setup: {str(e)}")
            return False
    
    def test_2fa_enable(self):
        """Test 2FA enable with TOTP verification"""
        print("\n=== Testing 2FA Enable ===")
        
        if not self.admin_token or not self.totp_secret:
            self.log_result("2FA Enable", False, "Missing admin token or TOTP secret")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Generate valid TOTP token
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            enable_data = {
                "token": valid_token,
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/2fa/enable", headers=headers, json=enable_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("2FA Enable", True, "2FA enabled successfully")
                    return True
                else:
                    self.log_result("2FA Enable", False, "Enable response indicates failure", {"response": data})
                    return False
            else:
                self.log_result("2FA Enable", False, f"2FA enable failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("2FA Enable", False, f"Error during 2FA enable: {str(e)}")
            return False
    
    def test_2fa_status(self):
        """Test 2FA status endpoint"""
        print("\n=== Testing 2FA Status ===")
        
        if not self.admin_token:
            self.log_result("2FA Status", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/auth/2fa/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("enabled") == True:
                    self.log_result("2FA Status", True, f"2FA status correct - enabled: {data['enabled']}, trusted devices: {data.get('trusted_device_count', 0)}")
                    return True
                else:
                    self.log_result("2FA Status", False, "2FA not showing as enabled", {"response": data})
                    return False
            else:
                self.log_result("2FA Status", False, f"2FA status failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("2FA Status", False, f"Error checking 2FA status: {str(e)}")
            return False
    
    def test_login_with_2fa(self):
        """Test login flow with 2FA enabled"""
        print("\n=== Testing Login with 2FA ===")
        
        if not self.totp_secret:
            self.log_result("Login with 2FA", False, "No TOTP secret available")
            return False
        
        try:
            # Test 1: Login with email + password only (should require 2FA)
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "testadmin@servercraft.com",
                    "password": "testpassword123"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requires_2fa") and data.get("temp_token"):
                    self.log_result("Login - 2FA Required", True, "Login correctly requires 2FA verification")
                    
                    # Test 2: Login with valid TOTP token
                    totp = pyotp.TOTP(self.totp_secret)
                    valid_token = totp.now()
                    
                    full_login_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={
                            "email": "testadmin@servercraft.com",
                            "password": "testpassword123",
                            "totp_token": valid_token
                        }
                    )
                    
                    if full_login_response.status_code == 200:
                        full_data = full_login_response.json()
                        if full_data.get("access_token") and not full_data.get("requires_2fa"):
                            self.log_result("Login - 2FA Success", True, "Login successful with valid 2FA token")
                            return True
                        else:
                            self.log_result("Login - 2FA Success", False, "Login with 2FA token failed", {"response": full_data})
                            return False
                    else:
                        self.log_result("Login - 2FA Success", False, f"Login with 2FA failed (HTTP {full_login_response.status_code})")
                        return False
                else:
                    self.log_result("Login - 2FA Required", False, "Login should require 2FA but doesn't", {"response": data})
                    return False
            else:
                self.log_result("Login - 2FA Required", False, f"Login failed (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Login with 2FA", False, f"Error testing 2FA login: {str(e)}")
            return False
    
    def test_backup_codes(self):
        """Test backup codes functionality"""
        print("\n=== Testing Backup Codes ===")
        
        if not self.admin_token or not self.backup_codes:
            self.log_result("Backup Codes", False, "Missing admin token or backup codes")
            return False
        
        try:
            # Test login with backup code
            test_code = self.backup_codes[0]  # Use first backup code
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "testadmin@servercraft.com",
                    "password": "testpassword123",
                    "totp_token": test_code
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.log_result("Backup Codes - Login", True, "Login successful with backup code")
                    return True
                else:
                    self.log_result("Backup Codes - Login", False, "Login with backup code failed - no access token", {"response": data})
                    return False
            else:
                self.log_result("Backup Codes - Login", False, f"Login with backup code failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("Backup Codes", False, f"Error testing backup codes: {str(e)}")
            return False
    
    def test_trusted_devices(self):
        """Test trusted devices functionality"""
        print("\n=== Testing Trusted Devices ===")
        
        if not self.totp_secret:
            self.log_result("Trusted Devices", False, "No TOTP secret available")
            return False
        
        try:
            # Login with remember_device=true
            totp = pyotp.TOTP(self.totp_secret)
            valid_token = totp.now()
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "testadmin@servercraft.com",
                    "password": "testpassword123",
                    "totp_token": valid_token,
                    "remember_device": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("device_token"):
                    self.device_token = data["device_token"]
                    self.log_result("Trusted Devices - Remember", True, "Device token generated for trusted device")
                    
                    # Test subsequent login with device token (should bypass 2FA)
                    time.sleep(1)  # Small delay
                    
                    device_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={
                            "email": "testadmin@servercraft.com",
                            "password": "testpassword123",
                            "device_token": self.device_token
                        }
                    )
                    
                    if device_response.status_code == 200:
                        device_data = device_response.json()
                        if device_data.get("access_token") and not device_data.get("requires_2fa"):
                            self.log_result("Trusted Devices - Bypass", True, "Trusted device successfully bypassed 2FA")
                            return True
                        else:
                            self.log_result("Trusted Devices - Bypass", False, "Trusted device did not bypass 2FA", {"response": device_data})
                            return False
                    else:
                        self.log_result("Trusted Devices - Bypass", False, f"Trusted device login failed (HTTP {device_response.status_code})")
                        return False
                else:
                    self.log_result("Trusted Devices - Remember", False, "No device token returned", {"response": data})
                    return False
            else:
                self.log_result("Trusted Devices - Remember", False, f"Remember device login failed (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Trusted Devices", False, f"Error testing trusted devices: {str(e)}")
            return False
    
    def run_comprehensive_2fa_tests(self):
        """Run all 2FA tests in sequence"""
        print(f"🚀 Starting Comprehensive 2FA Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in sequence - each depends on the previous
        success = True
        
        success &= self.test_initial_login()
        if success:
            success &= self.test_2fa_setup()
        if success:
            success &= self.test_2fa_enable()
        if success:
            success &= self.test_2fa_status()
        if success:
            success &= self.test_login_with_2fa()
        if success:
            success &= self.test_backup_codes()
        if success:
            success &= self.test_trusted_devices()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 2FA TEST SUMMARY")
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
        else:
            print("\n🎉 ALL 2FA TESTS PASSED!")
        
        return self.test_results

if __name__ == "__main__":
    tester = TwoFactorTester()
    results = tester.run_comprehensive_2fa_tests()