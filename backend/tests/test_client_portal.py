"""
Client Portal System Tests
Tests for the new Client Portal feature including:
- Portal client CRUD operations
- Invite generation and validation
- Client authentication
- Portal settings (admin only)
- Book of Business integration
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "kyle@breezewealthmanagement.com"
ADMIN_PASSWORD = "Breeze2026!"
TEST_CLIENT_EMAIL = f"test_portal_client_{uuid.uuid4().hex[:8]}@example.com"


class TestPortalAuth:
    """Test admin/agent authentication for portal management"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        return data["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_admin_login_success(self):
        """Test admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['name']}")


class TestPortalSettings:
    """Test portal settings endpoints (Admin only)"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_get_portal_settings(self, auth_header):
        """Test getting portal settings"""
        response = requests.get(f"{BASE_URL}/api/portal/settings", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        # Check that we got a valid response (settings may have been updated)
        assert isinstance(data, dict)
        print(f"✓ Portal settings retrieved successfully: {list(data.keys())}")
    
    def test_update_portal_settings(self, auth_header):
        """Test updating portal settings"""
        response = requests.put(f"{BASE_URL}/api/portal/settings", 
            headers=auth_header,
            json={
                "show_breeze_branding": True,
                "allow_messaging": False
            }
        )
        assert response.status_code == 200
        print(f"✓ Portal settings updated successfully")


class TestPortalClients:
    """Test portal client CRUD operations"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_create_portal_client(self, auth_header):
        """Test creating a new portal client"""
        test_email = f"test_client_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/portal/clients",
            headers=auth_header,
            json={
                "first_name": "Test",
                "last_name": "PortalClient",
                "email": test_email,
                "phone": "555-123-4567"
            }
        )
        assert response.status_code == 200, f"Create client failed: {response.text}"
        data = response.json()
        assert data["first_name"] == "Test"
        assert data["last_name"] == "PortalClient"
        assert data["email"] == test_email
        assert "id" in data
        print(f"✓ Portal client created: {data['id']}")
        return data["id"]
    
    def test_get_portal_clients_list(self, auth_header):
        """Test getting list of portal clients"""
        response = requests.get(f"{BASE_URL}/api/portal/clients", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Portal clients list retrieved: {len(data)} clients")
    
    def test_get_portal_metrics(self, auth_header):
        """Test getting portal metrics (admin only)"""
        response = requests.get(f"{BASE_URL}/api/portal/metrics", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "total_clients" in data
        assert "active_clients" in data
        assert "invited_clients" in data
        print(f"✓ Portal metrics retrieved: {data['total_clients']} total clients")


class TestPortalInvites:
    """Test portal invite generation and validation"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def test_client(self, auth_header):
        """Create a test client for invite testing"""
        test_email = f"invite_test_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/portal/clients",
            headers=auth_header,
            json={
                "first_name": "Invite",
                "last_name": "TestClient",
                "email": test_email
            }
        )
        assert response.status_code == 200
        return response.json()
    
    def test_generate_invite_link(self, auth_header, test_client):
        """Test generating an invite link for a portal client"""
        client_id = test_client["id"]
        response = requests.post(f"{BASE_URL}/api/portal/clients/{client_id}/invite",
            headers=auth_header
        )
        assert response.status_code == 200, f"Generate invite failed: {response.text}"
        data = response.json()
        assert "invite_token" in data
        assert "expires_at" in data
        print(f"✓ Invite generated with token: {data['invite_token'][:20]}...")
        return data["invite_token"]
    
    def test_validate_invite_token(self, auth_header, test_client):
        """Test validating an invite token"""
        # First generate an invite
        client_id = test_client["id"]
        invite_response = requests.post(f"{BASE_URL}/api/portal/clients/{client_id}/invite",
            headers=auth_header
        )
        assert invite_response.status_code == 200
        invite_token = invite_response.json()["invite_token"]
        
        # Now validate it (no auth required)
        response = requests.get(f"{BASE_URL}/api/portal/invite/validate/{invite_token}")
        assert response.status_code == 200, f"Validate invite failed: {response.text}"
        data = response.json()
        assert data["valid"] == True
        assert "client_first_name" in data
        assert "agent_name" in data
        print(f"✓ Invite validated for client: {data['client_first_name']}")
    
    def test_invalid_invite_token(self):
        """Test that invalid invite token returns error"""
        response = requests.get(f"{BASE_URL}/api/portal/invite/validate/invalid-token-12345")
        assert response.status_code == 404
        print(f"✓ Invalid invite token correctly rejected")


class TestPortalClientAuth:
    """Test client portal authentication flow"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def setup_client_with_password(self, auth_header):
        """Create a client and set their password"""
        # Create client
        test_email = f"auth_test_{uuid.uuid4().hex[:8]}@example.com"
        create_response = requests.post(f"{BASE_URL}/api/portal/clients",
            headers=auth_header,
            json={
                "first_name": "Auth",
                "last_name": "TestClient",
                "email": test_email
            }
        )
        assert create_response.status_code == 200
        client = create_response.json()
        
        # Generate invite
        invite_response = requests.post(f"{BASE_URL}/api/portal/clients/{client['id']}/invite",
            headers=auth_header
        )
        assert invite_response.status_code == 200
        invite_token = invite_response.json()["invite_token"]
        
        # Set password
        password = "TestPassword123!"
        set_password_response = requests.post(f"{BASE_URL}/api/portal/auth/set-password",
            json={
                "invite_token": invite_token,
                "password": password
            }
        )
        assert set_password_response.status_code == 200, f"Set password failed: {set_password_response.text}"
        
        return {
            "email": test_email,
            "password": password,
            "client": client
        }
    
    def test_client_login_success(self, setup_client_with_password):
        """Test client can login after setting password"""
        response = requests.post(f"{BASE_URL}/api/portal/auth/login",
            json={
                "email": setup_client_with_password["email"],
                "password": setup_client_with_password["password"]
            }
        )
        assert response.status_code == 200, f"Client login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "client" in data
        print(f"✓ Client login successful: {data['client']['first_name']}")
    
    def test_client_login_wrong_password(self, setup_client_with_password):
        """Test client login fails with wrong password"""
        response = requests.post(f"{BASE_URL}/api/portal/auth/login",
            json={
                "email": setup_client_with_password["email"],
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        print(f"✓ Wrong password correctly rejected")


class TestBookOfBusinessIntegration:
    """Test Book of Business to Portal integration"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_get_book_of_business_clients(self, auth_header):
        """Test getting Book of Business clients"""
        response = requests.get(f"{BASE_URL}/api/clients", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Book of Business clients retrieved: {len(data)} clients")
        return data
    
    def test_create_portal_client_from_book(self, auth_header):
        """Test creating portal client from Book of Business"""
        # First get a book of business client
        clients_response = requests.get(f"{BASE_URL}/api/clients", headers=auth_header)
        assert clients_response.status_code == 200
        clients = clients_response.json()
        
        if len(clients) == 0:
            pytest.skip("No Book of Business clients available for testing")
        
        # Use the first client
        book_client = clients[0]
        client_id = book_client["id"]
        
        # Create portal client from book
        response = requests.post(f"{BASE_URL}/api/portal/clients/from-book/{client_id}",
            headers=auth_header
        )
        assert response.status_code == 200, f"Create from book failed: {response.text}"
        data = response.json()
        assert "portal_client" in data
        assert "message" in data
        print(f"✓ Portal client created from Book of Business: {data['portal_client']['first_name']} {data['portal_client']['last_name']}")


class TestPortalPolicies:
    """Test portal policy management"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_header(self, admin_token):
        """Get authorization header"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def test_client(self, auth_header):
        """Create a test client for policy testing"""
        test_email = f"policy_test_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/portal/clients",
            headers=auth_header,
            json={
                "first_name": "Policy",
                "last_name": "TestClient",
                "email": test_email
            }
        )
        assert response.status_code == 200
        return response.json()
    
    def test_create_portal_policy(self, auth_header, test_client):
        """Test creating a policy for a portal client"""
        response = requests.post(f"{BASE_URL}/api/portal/policies",
            headers=auth_header,
            json={
                "client_id": test_client["id"],
                "carrier": "Test Carrier",
                "product_type": "IUL",
                "policy_number": "POL-12345",
                "premium": 5000,
                "status": "active",
                "is_visible": True
            }
        )
        assert response.status_code == 200, f"Create policy failed: {response.text}"
        data = response.json()
        assert data["carrier"] == "Test Carrier"
        assert data["product_type"] == "IUL"
        print(f"✓ Portal policy created: {data['id']}")
        return data["id"]
    
    def test_get_client_policies(self, auth_header, test_client):
        """Test getting policies for a client"""
        response = requests.get(f"{BASE_URL}/api/portal/policies/client/{test_client['id']}",
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Client policies retrieved: {len(data)} policies")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
