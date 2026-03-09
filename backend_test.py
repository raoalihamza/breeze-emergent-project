#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class BreezeMatrixAPITester:
    def __init__(self, base_url="https://team-portal-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.agent_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.admin_email = "kyle@breezewealthmanagement.com"
        self.admin_password = "Breeze2026!"
        self.new_admin_password = "NewBreeze2026!"
        
        # Test recruit data
        self.test_recruit_email = f"test.recruit.{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_recruit_name = "Test Recruit"
        self.test_comp_percentage = 75.0

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None, expected_status: int = 200) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}"
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "text": response.text}
            
            return success, response_data
            
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_admin_login(self):
        """Test admin login with default credentials"""
        print("\n🔐 Testing Admin Authentication...")
        
        success, response = self.make_request(
            'POST', 'auth/login',
            data={"email": self.admin_email, "password": self.admin_password}
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            user_data = response.get('user', {})
            needs_reset = user_data.get('needs_password_reset', False)
            
            self.log_test("Admin Login", True, f"Role: {user_data.get('role')}, Needs Reset: {needs_reset}")
            return True, needs_reset
        else:
            self.log_test("Admin Login", False, f"Response: {response}")
            return False, False

    def test_password_reset(self):
        """Test password reset functionality"""
        if not self.admin_token:
            self.log_test("Password Reset", False, "No admin token available")
            return False
        
        success, response = self.make_request(
            'POST', 'auth/reset-password',
            data={"new_password": self.new_admin_password},
            token=self.admin_token
        )
        
        self.log_test("Password Reset", success, f"Response: {response}")
        
        if success:
            # Test login with new password
            success, response = self.make_request(
                'POST', 'auth/login',
                data={"email": self.admin_email, "password": self.new_admin_password}
            )
            
            if success and 'token' in response:
                self.admin_token = response['token']
                self.log_test("Login with New Password", True)
                return True
            else:
                self.log_test("Login with New Password", False, f"Response: {response}")
        
        return success

    def test_auth_me(self):
        """Test get current user endpoint"""
        if not self.admin_token:
            self.log_test("Get Current User", False, "No admin token available")
            return False
        
        success, response = self.make_request('GET', 'auth/me', token=self.admin_token)
        self.log_test("Get Current User", success, f"User: {response.get('name', 'Unknown')}")
        return success

    def test_create_invite(self):
        """Test creating an invite"""
        if not self.admin_token:
            self.log_test("Create Invite", False, "No admin token available")
            return False, None
        
        success, response = self.make_request(
            'POST', 'invites',
            data={
                "recruit_email": self.test_recruit_email,
                "recruit_first_name": "Test",
                "recruit_last_name": "Recruit", 
                "recruit_npn": f"NPN{datetime.now().strftime('%H%M%S')}",
                "comp_percentage": self.test_comp_percentage,
                "message": "Welcome to Breeze Matrix!"
            },
            token=self.admin_token,
            expected_status=200
        )
        
        invite_token = response.get('token') if success else None
        self.log_test("Create Invite", success, f"Token: {invite_token[:8]}..." if invite_token else f"Response: {response}")
        return success, invite_token

    def test_validate_invite(self, invite_token: str):
        """Test validating an invite token"""
        if not invite_token:
            self.log_test("Validate Invite", False, "No invite token available")
            return False
        
        success, response = self.make_request('GET', f'invites/validate/{invite_token}')
        self.log_test("Validate Invite", success, f"Valid: {response.get('valid', False)}")
        return success

    def test_signup_with_invite(self, invite_token: str):
        """Test signup using invite token"""
        if not invite_token:
            self.log_test("Signup with Invite", False, "No invite token available")
            return False
        
        success, response = self.make_request(
            'POST', 'auth/signup',
            data={
                "email": self.test_recruit_email,
                "password": "TestPassword123!",
                "name": self.test_recruit_name,
                "invite_token": invite_token
            }
        )
        
        if success and 'token' in response:
            self.agent_token = response['token']
            self.log_test("Signup with Invite", True, f"New agent: {response.get('user', {}).get('name')}")
            return True
        else:
            self.log_test("Signup with Invite", False, f"Response: {response}")
            return False

    def test_hierarchy_endpoints(self):
        """Test hierarchy-related endpoints"""
        print("\n🌳 Testing Hierarchy Endpoints...")
        
        if not self.admin_token:
            self.log_test("Hierarchy Tests", False, "No admin token available")
            return
        
        # Test hierarchy tree
        success, response = self.make_request('GET', 'hierarchy/tree', token=self.admin_token)
        self.log_test("Get Hierarchy Tree", success, f"Trees: {len(response.get('trees', []))}")
        
        # Test downline
        success, response = self.make_request('GET', 'hierarchy/downline', token=self.admin_token)
        self.log_test("Get Downline", success, f"Members: {len(response) if isinstance(response, list) else 0}")
        
        # Test get users (admin only)
        success, response = self.make_request('GET', 'users', token=self.admin_token)
        self.log_test("Get All Users", success, f"Users: {len(response) if isinstance(response, list) else 0}")

    def test_resources_endpoints(self):
        """Test resource management endpoints"""
        print("\n📚 Testing Resources Endpoints...")
        
        if not self.admin_token:
            self.log_test("Resources Tests", False, "No admin token available")
            return
        
        # Create a test resource
        success, response = self.make_request(
            'POST', 'resources',
            data={
                "title": "Test Training Script",
                "category": "Training",
                "type": "Document",
                "url": "https://example.com/training.pdf",
                "description": "Test resource for API testing"
            },
            token=self.admin_token
        )
        
        resource_id = response.get('id') if success else None
        self.log_test("Create Resource", success, f"ID: {resource_id}")
        
        # Get resources
        success, response = self.make_request('GET', 'resources', token=self.admin_token)
        self.log_test("Get Resources", success, f"Count: {len(response) if isinstance(response, list) else 0}")
        
        # Delete test resource
        if resource_id:
            success, response = self.make_request('DELETE', f'resources/{resource_id}', token=self.admin_token)
            self.log_test("Delete Resource", success)

    def test_carriers_endpoints(self):
        """Test carrier management endpoints"""
        print("\n🏢 Testing Carriers Endpoints...")
        
        if not self.admin_token:
            self.log_test("Carriers Tests", False, "No admin token available")
            return
        
        # Create a test carrier
        success, response = self.make_request(
            'POST', 'carriers',
            data={
                "name": "Test Insurance Co",
                "description": "Test carrier for API testing",
                "guideline_url": "https://example.com/guidelines.pdf",
                "notes": "Test carrier notes"
            },
            token=self.admin_token
        )
        
        carrier_id = response.get('id') if success else None
        self.log_test("Create Carrier", success, f"ID: {carrier_id}")
        
        # Get carriers
        success, response = self.make_request('GET', 'carriers', token=self.admin_token)
        self.log_test("Get Carriers", success, f"Count: {len(response) if isinstance(response, list) else 0}")
        
        # Delete test carrier
        if carrier_id:
            success, response = self.make_request('DELETE', f'carriers/{carrier_id}', token=self.admin_token)
            self.log_test("Delete Carrier", success)

    def test_production_endpoints(self):
        """Test production tracking endpoints"""
        print("\n📊 Testing Production Endpoints...")
        
        if not self.admin_token:
            self.log_test("Production Tests", False, "No admin token available")
            return
        
        # Get current user to use as agent_id for webhook test
        success, user_response = self.make_request('GET', 'auth/me', token=self.admin_token)
        if not success:
            self.log_test("Production Tests", False, "Could not get current user")
            return
        
        agent_id = user_response.get('id')
        
        # Test production webhook (simulating Zapier)
        success, response = self.make_request(
            'POST', 'production/webhook',
            data={
                "agent_id": agent_id,
                "carrier": "Test Insurance Co",
                "policy_number": "TEST-12345",
                "submitted_ap": 50000.0,
                "issued_paid_ap": 45000.0,
                "status": "issued",
                "submission_date": "2024-01-15"
            }
        )
        self.log_test("Production Webhook", success, f"Response: {response}")
        
        # Get production data
        success, response = self.make_request('GET', 'production', token=self.admin_token)
        self.log_test("Get Production Data", success, f"Records: {len(response) if isinstance(response, list) else 0}")
        
        # Get production stats
        success, response = self.make_request('GET', 'production/stats', token=self.admin_token)
        if success:
            stats = response
            self.log_test("Get Production Stats", True, 
                         f"Submitted: ${stats.get('total_submitted_ap', 0):,.0f}, "
                         f"Issued: ${stats.get('total_issued_ap', 0):,.0f}, "
                         f"Policies: {stats.get('total_policies', 0)}")
        else:
            self.log_test("Get Production Stats", False, f"Response: {response}")

    def test_test_agent_login(self):
        """Test login with test agent credentials from review request"""
        print("\n🔐 Testing Test Agent Authentication...")
        
        test_agent_email = "testagent@breeze.com"
        test_agent_password = "TestAgent123!"
        
        success, response = self.make_request(
            'POST', 'auth/login',
            data={"email": test_agent_email, "password": test_agent_password}
        )
        
        if success and 'token' in response:
            self.test_agent_token = response['token']
            user_data = response.get('user', {})
            self.test_agent_id = user_data.get('id')
            
            self.log_test("Test Agent Login", True, f"Role: {user_data.get('role')}, ID: {self.test_agent_id}")
            return True
        else:
            self.log_test("Test Agent Login", False, f"Response: {response}")
            return False

    def test_admin_access_test_agent_kpis(self):
        """Test admin accessing test agent's KPIs"""
        if not self.admin_token:
            self.log_test("Admin Access Test Agent KPIs", False, "No admin token available")
            return
            
        if not hasattr(self, 'test_agent_id') or not self.test_agent_id:
            self.log_test("Admin Access Test Agent KPIs", False, "No test agent ID available")
            return
        
        # Create a KPI entry for the test agent first
        if hasattr(self, 'test_agent_token') and self.test_agent_token:
            from datetime import date
            today = date.today().isoformat()
            
            kpi_data = {
                "date": today,
                "dials_made": 25,
                "contacts_made": 8,
                "appointments_set": 4,
                "presentations_given": 2,
                "sales_made": 1
            }
            
            success, response = self.make_request(
                'POST', 'kpi',
                data=kpi_data,
                token=self.test_agent_token
            )
            self.log_test("Create KPI Entry for Test Agent", success, f"Test agent KPI created")
        
        # Now test admin accessing test agent's KPIs
        success, response = self.make_request(
            'GET', f'kpi?user_id={self.test_agent_id}', 
            token=self.admin_token
        )
        kpi_count = len(response) if isinstance(response, list) else 0
        self.log_test("Admin Access Test Agent KPIs", success, f"Test agent KPIs found: {kpi_count}")

    def test_kpi_endpoints(self):
        """Test KPI tracking endpoints"""
        print("\n📈 Testing KPI Tracking Endpoints...")
        
        if not self.admin_token:
            self.log_test("KPI Tests", False, "No admin token available")
            return
        
        # Test creating KPI entry for today
        from datetime import date
        today = date.today().isoformat()
        
        kpi_data = {
            "date": today,
            "dials_made": 50,
            "contacts_made": 15,
            "appointments_set": 8,
            "presentations_given": 5,
            "sales_made": 2
        }
        
        success, response = self.make_request(
            'POST', 'kpi',
            data=kpi_data,
            token=self.admin_token
        )
        
        kpi_id = response.get('id') if success else None
        self.log_test("Create KPI Entry", success, f"ID: {kpi_id}, Date: {today}")
        
        # Test updating the same KPI entry (same date)
        updated_kpi_data = {
            "date": today,
            "dials_made": 60,  # Updated value
            "contacts_made": 18,  # Updated value
            "appointments_set": 10,  # Updated value
            "presentations_given": 6,  # Updated value
            "sales_made": 3  # Updated value
        }
        
        success, response = self.make_request(
            'POST', 'kpi',
            data=updated_kpi_data,
            token=self.admin_token
        )
        
        self.log_test("Update KPI Entry (same date)", success, f"Updated dials: {response.get('dials_made', 'N/A')}")
        
        # Test fetching all KPI entries
        success, response = self.make_request('GET', 'kpi', token=self.admin_token)
        kpi_count = len(response) if isinstance(response, list) else 0
        self.log_test("Get All KPI Entries", success, f"Count: {kpi_count}")
        
        # Test fetching KPI entries with date range
        from datetime import timedelta
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        success, response = self.make_request(
            'GET', f'kpi?start_date={week_ago}&end_date={today}', 
            token=self.admin_token
        )
        range_count = len(response) if isinstance(response, list) else 0
        self.log_test("Get KPI Entries with Date Range", success, f"Count in range: {range_count}")
        
        # Test weekly CEO report generation
        success, response = self.make_request('GET', 'kpi/weekly-report', token=self.admin_token)
        if success:
            report_keys = list(response.keys()) if isinstance(response, dict) else []
            expected_keys = ['week_start', 'week_end', 'kpi_summary', 'improvements', 'declines', 'focus_areas', 'self_reflection_questions']
            has_all_keys = all(key in report_keys for key in expected_keys)
            
            focus_areas = response.get('focus_areas', [])
            reflection_questions = response.get('self_reflection_questions', [])
            
            self.log_test("Generate Weekly CEO Report", success, 
                         f"Has all keys: {has_all_keys}, Focus areas: {len(focus_areas)}, Reflection questions: {len(reflection_questions)}")
            
            # Verify AI-generated content is meaningful (not empty)
            if focus_areas and reflection_questions:
                self.log_test("AI-Generated Content Present", True, 
                             f"Focus areas sample: '{focus_areas[0][:50]}...', Questions sample: '{reflection_questions[0][:50]}...'")
            else:
                self.log_test("AI-Generated Content Present", False, "Missing focus areas or reflection questions")
        else:
            self.log_test("Generate Weekly CEO Report", False, f"Response: {response}")

    def test_book_of_business_endpoints(self):
        """Test Book of Business (Clients) endpoints comprehensively"""
        print("\n📋 Testing Book of Business Endpoints...")
        
        if not self.admin_token:
            self.log_test("Book of Business Tests", False, "No admin token available")
            return
        
        # Test data for client creation
        client_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1985-03-15",
            "state": "CA",
            "carrier": "Pacific Life",
            "product": "IUL Premium",
            "policy_number": "PL-2024-001",
            "monthly_premium": 250.0,
            "client_why": "Wants to secure his family's financial future and build wealth for retirement",
            "beneficiaries": [
                {"name": "Jane Doe", "phone_number": "555-123-4567"},
                {"name": "Michael Doe", "phone_number": "555-987-6543"}
            ],
            "additional_notes": "Client is very interested in tax-free growth potential"
        }
        
        # 1. Test POST /api/clients - Create new client
        success, response = self.make_request(
            'POST', 'clients',
            data=client_data,
            token=self.admin_token
        )
        
        client_id = response.get('id') if success else None
        annual_premium = response.get('annual_premium') if success else None
        expected_annual = client_data['monthly_premium'] * 12
        
        if success and annual_premium == expected_annual:
            self.log_test("Create Client", True, f"ID: {client_id}, Annual Premium: ${annual_premium}")
        else:
            self.log_test("Create Client", False, f"Response: {response}")
            return
        
        # Verify beneficiaries are stored correctly
        beneficiaries = response.get('beneficiaries', [])
        if len(beneficiaries) == 2:
            self.log_test("Client Beneficiaries Stored", True, f"Count: {len(beneficiaries)}")
        else:
            self.log_test("Client Beneficiaries Stored", False, f"Expected 2, got {len(beneficiaries)}")
        
        # 2. Test GET /api/clients - Fetch all clients
        success, response = self.make_request('GET', 'clients', token=self.admin_token)
        client_count = len(response) if isinstance(response, list) else 0
        
        # Find our created client
        created_client = None
        if success and isinstance(response, list):
            created_client = next((c for c in response if c.get('id') == client_id), None)
        
        if success and created_client:
            self.log_test("Get All Clients", True, f"Total clients: {client_count}, Found created client")
        else:
            self.log_test("Get All Clients", False, f"Response: {response}")
        
        # 3. Test GET /api/clients/{client_id} - Get single client
        if client_id:
            success, response = self.make_request('GET', f'clients/{client_id}', token=self.admin_token)
            
            if success and response.get('id') == client_id:
                self.log_test("Get Single Client", True, f"Name: {response.get('first_name')} {response.get('last_name')}")
            else:
                self.log_test("Get Single Client", False, f"Response: {response}")
        
        # 4. Test PUT /api/clients/{client_id} - Update client
        if client_id:
            update_data = {
                "monthly_premium": 300.0,
                "additional_notes": "Updated notes - client increased premium"
            }
            
            success, response = self.make_request(
                'PUT', f'clients/{client_id}',
                data=update_data,
                token=self.admin_token
            )
            
            updated_annual = response.get('annual_premium') if success else None
            expected_updated_annual = update_data['monthly_premium'] * 12
            
            if success and updated_annual == expected_updated_annual:
                self.log_test("Update Client", True, f"New annual premium: ${updated_annual}")
            else:
                self.log_test("Update Client", False, f"Response: {response}")
        
        # 5. Test authorization - create agent token and test access
        if hasattr(self, 'agent_token') and self.agent_token and client_id:
            # Agent should NOT be able to access admin's client
            success, response = self.make_request(
                'GET', f'clients/{client_id}', 
                token=self.agent_token, 
                expected_status=403
            )
            self.log_test("Agent Access to Admin Client (should fail)", success, "Correctly blocked")
        
        # 6. Test Export Endpoints
        export_formats = ['csv', 'xlsx', 'pdf']
        for format_type in export_formats:
            success, response = self.make_request(
                'GET', f'clients/export/{format_type}', 
                token=self.admin_token
            )
            
            # For export endpoints, we expect different response handling
            if success or (hasattr(response, 'get') and response.get('status_code') == 200):
                self.log_test(f"Export Clients ({format_type.upper()})", True, "Export successful")
            else:
                self.log_test(f"Export Clients ({format_type.upper()})", False, f"Response: {response}")
        
        # 7. Test DELETE /api/clients/{client_id} - Delete client (do this last)
        if client_id:
            success, response = self.make_request('DELETE', f'clients/{client_id}', token=self.admin_token)
            
            if success:
                self.log_test("Delete Client", True, "Client deleted successfully")
                
                # Verify client is actually deleted
                success, response = self.make_request(
                    'GET', f'clients/{client_id}', 
                    token=self.admin_token, 
                    expected_status=404
                )
                self.log_test("Verify Client Deleted", success, "Client not found (expected)")
            else:
                self.log_test("Delete Client", False, f"Response: {response}")

    def test_role_based_access(self):
        """Test role-based access control"""
        print("\n🔒 Testing Role-Based Access Control...")
        
        if not self.agent_token:
            self.log_test("Role-Based Access", False, "No agent token available")
            return
        
        # Agent should NOT be able to access admin endpoints
        success, response = self.make_request('GET', 'users', token=self.agent_token, expected_status=403)
        self.log_test("Agent Access to Admin Endpoint (should fail)", success, "Correctly blocked")
        
        # Agent should be able to access their own data
        success, response = self.make_request('GET', 'auth/me', token=self.agent_token)
        self.log_test("Agent Access Own Data", success, f"Agent: {response.get('name', 'Unknown')}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Breeze Matrix API Tests...")
        print(f"Testing against: {self.base_url}")
        
        # Authentication flow
        login_success, needs_reset = self.test_admin_login()
        
        if login_success and needs_reset:
            self.test_password_reset()
        
        if self.admin_token:
            self.test_auth_me()
            
            # Try to login with test agent credentials
            self.test_test_agent_login()
            
            # Invite and signup flow
            invite_success, invite_token = self.test_create_invite()
            if invite_success and invite_token:
                self.test_validate_invite(invite_token)
                self.test_signup_with_invite(invite_token)
            
            # Test all endpoints
            self.test_hierarchy_endpoints()
            self.test_resources_endpoints()
            self.test_carriers_endpoints()
            self.test_production_endpoints()
            self.test_kpi_endpoints()
            self.test_book_of_business_endpoints()
            
            # Test admin access to test agent KPIs
            self.test_admin_access_test_agent_kpis()
            
            # Test role-based access
            if self.agent_token:
                self.test_role_based_access()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Return results for further processing
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BreezeMatrixAPITester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        print("\n✅ Backend tests mostly successful!")
        return 0
    else:
        print("\n❌ Backend tests have significant failures!")
        return 1

if __name__ == "__main__":
    sys.exit(main())