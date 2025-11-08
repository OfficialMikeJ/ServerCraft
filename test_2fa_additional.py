#!/usr/bin/env python3
"""
Additional 2FA Security Testing for ServerCraft Panel
Tests 2FA disable, backup code regeneration, and security measures
"""

import requests
import json
import pyotp
import time

# Get backend URL from frontend env
BACKEND_URL = "https://servercraft-admin.preview.emergentagent.com/api"

class AdditionalTwoFactorTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
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
    
    def get_admin_token_with_2fa(self):
        """Get admin token when 2FA is enabled"""
        try:
            # First, get the user's 2FA secret from database (for testing purposes)
            # In real scenario, user would use their authenticator app
            
            # Login to get temp token first
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": "testadmin@servercraft.com",
                    "password": "testpassword123"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requires_2fa"):
                    # We need to get the secret from database for testing
                    # In production, user would use their authenticator app
                    import os
                    from motor.motor_asyncio import AsyncIOMotorClient
                    import asyncio
                    
                    async def get_secret():
                        mongo_url = 'mongodb://localhost:27017'
                        client = AsyncIOMotorClient(mongo_url)
                        db = client['test_database']
                        
                        user = await db.users.find_one(
                            {'email': 'testadmin@servercraft.com'},
                            {'_id': 0, 'two_factor_secret': 1}
                        )
                        
                        client.close()
                        return user.get('two_factor_secret') if user else None
                    
                    secret = asyncio.run(get_secret())
                    
                    if secret:
                        # Generate TOTP token
                        totp = pyotp.TOTP(secret)
                        valid_token = totp.now()
                        
                        # Login with 2FA token
                        full_response = self.session.post(
                            f"{self.base_url}/auth/login",
                            json={
                                "email": "testadmin@servercraft.com",
                                "password": "testpassword123",
                                "totp_token": valid_token
                            }
                        )
                        
                        if full_response.status_code == 200:
                            full_data = full_response.json()
                            return full_data.get("access_token"), secret
                        
            return None, None
        except Exception as e:
            print(f"Error getting admin token: {e}")
            return None, None
    
    def test_backup_code_regeneration(self):
        """Test backup code regeneration endpoint"""
        print("\n=== Testing Backup Code Regeneration ===")
        
        token, secret = self.get_admin_token_with_2fa()
        if not token:
            self.log_result("Backup Code Regeneration", False, "Cannot get admin token with 2FA")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/auth/2fa/backup-codes", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "backup_codes" in data and len(data["backup_codes"]) == 10:
                    self.log_result("Backup Code Regeneration", True, f"Backup codes regenerated successfully ({len(data['backup_codes'])} codes)")
                    return True
                else:
                    self.log_result("Backup Code Regeneration", False, "Invalid backup codes response", {"response": data})
                    return False
            else:
                self.log_result("Backup Code Regeneration", False, f"Backup code regeneration failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("Backup Code Regeneration", False, f"Error testing backup code regeneration: {str(e)}")
            return False
    
    def test_2fa_verify_endpoint(self):
        """Test 2FA token verification endpoint"""
        print("\n=== Testing 2FA Token Verification ===")
        
        token, secret = self.get_admin_token_with_2fa()
        if not token or not secret:
            self.log_result("2FA Token Verification", False, "Cannot get admin token or secret")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test with valid token
            totp = pyotp.TOTP(secret)
            valid_token = totp.now()
            
            response = self.session.post(
                f"{self.base_url}/auth/2fa/verify",
                headers=headers,
                json={"token": valid_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") == True:
                    self.log_result("2FA Token Verification - Valid", True, "Valid token correctly verified")
                    
                    # Test with invalid token
                    invalid_response = self.session.post(
                        f"{self.base_url}/auth/2fa/verify",
                        headers=headers,
                        json={"token": "123456"}
                    )
                    
                    if invalid_response.status_code == 200:
                        invalid_data = invalid_response.json()
                        if invalid_data.get("valid") == False:
                            self.log_result("2FA Token Verification - Invalid", True, "Invalid token correctly rejected")
                            return True
                        else:
                            self.log_result("2FA Token Verification - Invalid", False, "Invalid token not rejected", {"response": invalid_data})
                            return False
                    else:
                        self.log_result("2FA Token Verification - Invalid", False, f"Invalid token test failed (HTTP {invalid_response.status_code})")
                        return False
                else:
                    self.log_result("2FA Token Verification - Valid", False, "Valid token not verified", {"response": data})
                    return False
            else:
                self.log_result("2FA Token Verification - Valid", False, f"Token verification failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("2FA Token Verification", False, f"Error testing token verification: {str(e)}")
            return False
    
    def test_trusted_device_management(self):
        """Test trusted device management"""
        print("\n=== Testing Trusted Device Management ===")
        
        token, secret = self.get_admin_token_with_2fa()
        if not token:
            self.log_result("Trusted Device Management", False, "Cannot get admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Clear all trusted devices
            response = self.session.delete(f"{self.base_url}/auth/2fa/trusted-devices", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("Trusted Device Management", True, "Trusted devices cleared successfully")
                    return True
                else:
                    self.log_result("Trusted Device Management", False, "Clear trusted devices response indicates failure", {"response": data})
                    return False
            else:
                self.log_result("Trusted Device Management", False, f"Clear trusted devices failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("Trusted Device Management", False, f"Error testing trusted device management: {str(e)}")
            return False
    
    def test_2fa_disable(self):
        """Test 2FA disable functionality"""
        print("\n=== Testing 2FA Disable ===")
        
        token, secret = self.get_admin_token_with_2fa()
        if not token or not secret:
            self.log_result("2FA Disable", False, "Cannot get admin token or secret")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Generate valid TOTP token for disable
            totp = pyotp.TOTP(secret)
            valid_token = totp.now()
            
            disable_data = {
                "password": "testpassword123",
                "token": valid_token
            }
            
            response = self.session.post(f"{self.base_url}/auth/2fa/disable", headers=headers, json=disable_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("2FA Disable", True, "2FA disabled successfully")
                    
                    # Verify 2FA is actually disabled by checking status
                    # Need to get new token since 2FA is now disabled
                    login_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={
                            "email": "testadmin@servercraft.com",
                            "password": "testpassword123"
                        }
                    )
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        if login_data.get("access_token") and not login_data.get("requires_2fa"):
                            self.log_result("2FA Disable - Verification", True, "2FA disable verified - login no longer requires 2FA")
                            return True
                        else:
                            self.log_result("2FA Disable - Verification", False, "2FA still required after disable", {"response": login_data})
                            return False
                    else:
                        self.log_result("2FA Disable - Verification", False, f"Login after disable failed (HTTP {login_response.status_code})")
                        return False
                else:
                    self.log_result("2FA Disable", False, "Disable response indicates failure", {"response": data})
                    return False
            else:
                self.log_result("2FA Disable", False, f"2FA disable failed (HTTP {response.status_code})", {"response": response.text[:200]})
                return False
                
        except Exception as e:
            self.log_result("2FA Disable", False, f"Error testing 2FA disable: {str(e)}")
            return False
    
    def test_security_measures(self):
        """Test security measures (authentication requirements)"""
        print("\n=== Testing Security Measures ===")
        
        try:
            # Test endpoints without authentication
            endpoints_to_test = [
                ("/auth/2fa/setup", "POST"),
                ("/auth/2fa/status", "GET"),
                ("/auth/2fa/backup-codes", "GET"),
                ("/auth/2fa/verify", "POST"),
                ("/auth/2fa/trusted-devices", "DELETE")
            ]
            
            auth_required_count = 0
            for endpoint, method in endpoints_to_test:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", json={})
                elif method == "DELETE":
                    response = self.session.delete(f"{self.base_url}{endpoint}")
                
                if response.status_code in [401, 403]:
                    auth_required_count += 1
            
            if auth_required_count == len(endpoints_to_test):
                self.log_result("Security - Auth Required", True, "All 2FA endpoints properly require authentication")
                return True
            else:
                self.log_result("Security - Auth Required", False, f"Only {auth_required_count}/{len(endpoints_to_test)} endpoints require auth")
                return False
                
        except Exception as e:
            self.log_result("Security - Auth Required", False, f"Error testing security measures: {str(e)}")
            return False
    
    def run_additional_tests(self):
        """Run all additional 2FA tests"""
        print(f"🚀 Starting Additional 2FA Security Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests
        self.test_backup_code_regeneration()
        self.test_2fa_verify_endpoint()
        self.test_trusted_device_management()
        self.test_security_measures()
        self.test_2fa_disable()  # Run this last as it disables 2FA
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 ADDITIONAL 2FA TEST SUMMARY")
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
            print("\n🎉 ALL ADDITIONAL 2FA TESTS PASSED!")
        
        return self.test_results

if __name__ == "__main__":
    tester = AdditionalTwoFactorTester()
    results = tester.run_additional_tests()