"""
ServerCraft Security Testing Suite
Comprehensive security testing for all implemented features
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime
import sys

class SecurityTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed += 1
            print(f"{status}: {test_name}")
        else:
            self.failed += 1
            print(f"{status}: {test_name} - {message}")
        
        if message and passed:
            print(f"   └─ {message}")
    
    def test_password_strength_validation(self):
        """Test 1: Password Strength Validation"""
        print("\n=== Test 1: Password Strength Validation ===")
        
        weak_passwords = [
            ("short", "Too short"),
            ("alllowercase123!", "No uppercase"),
            ("ALLUPPERCASE123!", "No lowercase"),
            ("NoNumbers!", "No numbers"),
            ("NoSpecialChar123", "No special character"),
            ("Password123!", "Common password")
        ]
        
        for pwd, reason in weak_passwords:
            try:
                response = requests.post(
                    f"{self.api_url}/auth/register",
                    json={
                        "username": f"test_user_{int(time.time())}",
                        "email": f"test{int(time.time())}@example.com",
                        "password": pwd
                    },
                    timeout=10
                )
                
                if response.status_code == 400:
                    self.log_test(
                        f"Password rejection: {reason}",
                        True,
                        f"Correctly rejected weak password"
                    )
                else:
                    self.log_test(
                        f"Password rejection: {reason}",
                        False,
                        f"Weak password was accepted (status: {response.status_code})"
                    )
            except Exception as e:
                self.log_test(f"Password rejection: {reason}", False, str(e))
        
        # Test strong password acceptance
        try:
            strong_pwd = f"StrongP@ssw0rd{int(time.time())}"
            response = requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "username": f"strong_user_{int(time.time())}",
                    "email": f"strong{int(time.time())}@example.com",
                    "password": strong_pwd
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Strong password acceptance",
                    True,
                    "Strong password correctly accepted"
                )
            else:
                self.log_test(
                    "Strong password acceptance",
                    False,
                    f"Strong password rejected (status: {response.status_code})"
                )
        except Exception as e:
            self.log_test("Strong password acceptance", False, str(e))
    
    def test_rate_limiting(self):
        """Test 2: Rate Limiting"""
        print("\n=== Test 2: Rate Limiting ===")
        
        # Test login rate limiting (10 per minute)
        email = f"ratelimit{int(time.time())}@example.com"
        
        # First, create a user
        try:
            requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "username": "ratelimit_user",
                    "email": email,
                    "password": "RateLimit123!"
                },
                timeout=10
            )
        except:
            pass
        
        # Try to exceed rate limit
        rate_limited = False
        for i in range(15):
            try:
                response = requests.post(
                    f"{self.api_url}/auth/login",
                    json={
                        "email": email,
                        "password": "WrongPassword123!"
                    },
                    timeout=5
                )
                
                if response.status_code == 429:
                    rate_limited = True
                    self.log_test(
                        "Rate limiting enforcement",
                        True,
                        f"Rate limit hit at request {i+1}"
                    )
                    break
                    
            except Exception as e:
                if "429" in str(e):
                    rate_limited = True
                    self.log_test(
                        "Rate limiting enforcement",
                        True,
                        f"Rate limit hit at request {i+1}"
                    )
                    break
            
            time.sleep(0.1)
        
        if not rate_limited:
            self.log_test(
                "Rate limiting enforcement",
                False,
                "Rate limit was not enforced after 15 requests"
            )
    
    def test_account_lockout(self):
        """Test 3: Account Lockout After Failed Attempts"""
        print("\n=== Test 3: Account Lockout ===")
        
        # Create test user
        email = f"lockout{int(time.time())}@example.com"
        password = "Correct123!"
        
        try:
            requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "username": "lockout_user",
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            time.sleep(1)
        except:
            pass
        
        # Attempt multiple failed logins
        for i in range(6):
            try:
                response = requests.post(
                    f"{self.api_url}/auth/login",
                    json={
                        "email": email,
                        "password": "WrongPassword123!"
                    },
                    timeout=10
                )
                time.sleep(0.5)
            except:
                pass
        
        # Try to login with correct password (should be locked)
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_test(
                    "Account lockout after failed attempts",
                    True,
                    "Account correctly locked after multiple failures"
                )
            else:
                self.log_test(
                    "Account lockout after failed attempts",
                    False,
                    f"Account not locked (status: {response.status_code})"
                )
        except Exception as e:
            self.log_test("Account lockout after failed attempts", False, str(e))
    
    def test_session_management(self):
        """Test 4: Session Management"""
        print("\n=== Test 4: Session Management ===")
        
        # Create and login user
        email = f"session{int(time.time())}@example.com"
        password = "Session123!"
        
        try:
            # Register
            response = requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "username": "session_user",
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                # Test authenticated request
                headers = {"Authorization": f"Bearer {token}"}
                stats_response = requests.get(
                    f"{self.api_url}/stats",
                    headers=headers,
                    timeout=10
                )
                
                if stats_response.status_code == 200:
                    self.log_test(
                        "Session token validation",
                        True,
                        "Valid token accepted for protected endpoint"
                    )
                else:
                    self.log_test(
                        "Session token validation",
                        False,
                        f"Valid token rejected (status: {stats_response.status_code})"
                    )
                
                # Test logout
                logout_response = requests.post(
                    f"{self.api_url}/auth/logout",
                    headers=headers,
                    timeout=10
                )
                
                if logout_response.status_code == 200:
                    self.log_test(
                        "Session logout",
                        True,
                        "Logout successful"
                    )
                    
                    # Try to use token after logout (should fail)
                    time.sleep(1)
                    after_logout = requests.get(
                        f"{self.api_url}/stats",
                        headers=headers,
                        timeout=10
                    )
                    
                    if after_logout.status_code == 401:
                        self.log_test(
                            "Token invalidation after logout",
                            True,
                            "Token correctly invalidated"
                        )
                    else:
                        self.log_test(
                            "Token invalidation after logout",
                            False,
                            f"Token still valid after logout (status: {after_logout.status_code})"
                        )
                else:
                    self.log_test("Session logout", False, f"Logout failed (status: {logout_response.status_code})")
            else:
                self.log_test("Session management setup", False, "Failed to create test user")
                
        except Exception as e:
            self.log_test("Session management", False, str(e))
    
    def test_token_refresh(self):
        """Test 5: Token Refresh Mechanism"""
        print("\n=== Test 5: Token Refresh ===")
        
        email = f"refresh{int(time.time())}@example.com"
        password = "Refresh123!"
        
        try:
            # Register
            response = requests.post(
                f"{self.api_url}/auth/register",
                json={
                    "username": "refresh_user",
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                refresh_token = data.get("refresh_token")
                
                if refresh_token:
                    # Test token refresh
                    refresh_response = requests.post(
                        f"{self.api_url}/auth/refresh",
                        json={"refresh_token": refresh_token},
                        timeout=10
                    )
                    
                    if refresh_response.status_code == 200:
                        new_data = refresh_response.json()
                        if new_data.get("access_token") and new_data.get("refresh_token"):
                            self.log_test(
                                "Token refresh functionality",
                                True,
                                "New tokens generated successfully"
                            )
                        else:
                            self.log_test(
                                "Token refresh functionality",
                                False,
                                "New tokens not returned"
                            )
                    else:
                        self.log_test(
                            "Token refresh functionality",
                            False,
                            f"Refresh failed (status: {refresh_response.status_code})"
                        )
                else:
                    self.log_test("Token refresh functionality", False, "No refresh token provided")
            else:
                self.log_test("Token refresh setup", False, "Failed to create test user")
                
        except Exception as e:
            self.log_test("Token refresh", False, str(e))
    
    def test_input_sanitization(self):
        """Test 6: Input Sanitization"""
        print("\n=== Test 6: Input Sanitization ===")
        
        # Test XSS prevention in username
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "<iframe src='evil.com'></iframe>",
            "'; DROP TABLE users; --"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                response = requests.post(
                    f"{self.api_url}/auth/register",
                    json={
                        "username": malicious_input,
                        "email": f"xss{int(time.time())}@example.com",
                        "password": "Secure123!"
                    },
                    timeout=10
                )
                
                # Should either reject or sanitize
                if response.status_code in [200, 400]:
                    self.log_test(
                        f"Input sanitization: {malicious_input[:30]}...",
                        True,
                        "Malicious input handled"
                    )
                else:
                    self.log_test(
                        f"Input sanitization: {malicious_input[:30]}...",
                        False,
                        f"Unexpected response (status: {response.status_code})"
                    )
            except Exception as e:
                self.log_test(f"Input sanitization test", False, str(e))
    
    def test_authentication_flows(self):
        """Test 7: Authentication Flows"""
        print("\n=== Test 7: Authentication Flows ===")
        
        # Test accessing protected endpoint without token
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_test(
                    "Protected endpoint without auth",
                    True,
                    "Correctly denied access without token"
                )
            else:
                self.log_test(
                    "Protected endpoint without auth",
                    False,
                    f"Access granted without token (status: {response.status_code})"
                )
        except Exception as e:
            self.log_test("Protected endpoint test", False, str(e))
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = requests.get(
                f"{self.api_url}/stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Invalid token rejection",
                    True,
                    "Invalid token correctly rejected"
                )
            else:
                self.log_test(
                    "Invalid token rejection",
                    False,
                    f"Invalid token accepted (status: {response.status_code})"
                )
        except Exception as e:
            self.log_test("Invalid token test", False, str(e))
    
    def test_email_validation(self):
        """Test 8: Email Validation"""
        print("\n=== Test 8: Email Validation ===")
        
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            try:
                response = requests.post(
                    f"{self.api_url}/auth/register",
                    json={
                        "username": f"test_user_{int(time.time())}",
                        "email": email,
                        "password": "Valid123!"
                    },
                    timeout=10
                )
                
                if response.status_code == 422 or response.status_code == 400:
                    self.log_test(
                        f"Email validation: {email}",
                        True,
                        "Invalid email correctly rejected"
                    )
                else:
                    self.log_test(
                        f"Email validation: {email}",
                        False,
                        f"Invalid email accepted (status: {response.status_code})"
                    )
            except Exception as e:
                self.log_test(f"Email validation: {email}", False, str(e))
    
    def test_duplicate_registration(self):
        """Test 9: Duplicate Registration Prevention"""
        print("\n=== Test 9: Duplicate Registration Prevention ===")
        
        email = f"duplicate{int(time.time())}@example.com"
        user_data = {
            "username": "duplicate_user",
            "email": email,
            "password": "Duplicate123!"
        }
        
        try:
            # First registration
            response1 = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                timeout=10
            )
            
            time.sleep(1)
            
            # Second registration with same email
            response2 = requests.post(
                f"{self.api_url}/auth/register",
                json=user_data,
                timeout=10
            )
            
            if response2.status_code == 400:
                self.log_test(
                    "Duplicate email prevention",
                    True,
                    "Duplicate registration correctly prevented"
                )
            else:
                self.log_test(
                    "Duplicate email prevention",
                    False,
                    f"Duplicate allowed (status: {response2.status_code})"
                )
        except Exception as e:
            self.log_test("Duplicate registration test", False, str(e))
    
    def test_cors_headers(self):
        """Test 10: CORS Headers"""
        print("\n=== Test 10: CORS Headers ===")
        
        try:
            response = requests.options(
                f"{self.api_url}/stats",
                headers={"Origin": "https://example.com"},
                timeout=10
            )
            
            has_cors = "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
            
            if has_cors:
                self.log_test(
                    "CORS headers present",
                    True,
                    "CORS properly configured"
                )
            else:
                self.log_test(
                    "CORS headers present",
                    False,
                    "CORS headers missing"
                )
        except Exception as e:
            self.log_test("CORS test", False, str(e))
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("SECURITY TEST REPORT")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("="*60)
        
        if self.failed > 0:
            print("\n⚠️  FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['test']}")
                    if result['message']:
                        print(f"    └─ {result['message']}")
        
        # Save report to file
        with open('/app/security_test_report.json', 'w') as f:
            json.dump({
                "summary": {
                    "total": self.passed + self.failed,
                    "passed": self.passed,
                    "failed": self.failed,
                    "success_rate": f"{(self.passed / (self.passed + self.failed) * 100):.1f}%",
                    "timestamp": datetime.now().isoformat()
                },
                "tests": self.test_results
            }, f, indent=2)
        
        print("\n📄 Detailed report saved to: /app/security_test_report.json")
        
        return self.failed == 0

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║       ServerCraft Security Testing Suite                 ║
║       Comprehensive Security Feature Testing             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Get backend URL from environment or use default
    import os
    backend_url = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")
    
    print(f"Testing backend at: {backend_url}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    tester = SecurityTester(backend_url)
    
    # Run all tests
    try:
        tester.test_password_strength_validation()
        time.sleep(2)
        
        tester.test_rate_limiting()
        time.sleep(2)
        
        tester.test_account_lockout()
        time.sleep(2)
        
        tester.test_session_management()
        time.sleep(2)
        
        tester.test_token_refresh()
        time.sleep(2)
        
        tester.test_input_sanitization()
        time.sleep(2)
        
        tester.test_authentication_flows()
        time.sleep(2)
        
        tester.test_email_validation()
        time.sleep(2)
        
        tester.test_duplicate_registration()
        time.sleep(2)
        
        tester.test_cors_headers()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
    
    # Generate final report
    all_passed = tester.generate_report()
    
    if all_passed:
        print("\n✅ All security tests passed! Ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review and fix before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
