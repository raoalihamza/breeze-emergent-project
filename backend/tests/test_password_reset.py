"""
Test suite for Password Reset Flow (Email integration feature)
Tests: Forgot Password, Verify Reset Token, Reset Password with Token
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials from previous iterations
ADMIN_EMAIL = "kyle@breezewealthmanagement.com"
ADMIN_PASSWORD = "Breeze2026!"


class TestPasswordResetFlow:
    """Password Reset Flow Tests"""
    
    def test_forgot_password_valid_email(self):
        """Test forgot password endpoint with valid existing email"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": ADMIN_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        # Should always return success message (prevents email enumeration)
        assert "message" in data
        assert "password reset link has been sent" in data["message"].lower() or "if an account exists" in data["message"].lower()
        print(f"✓ Forgot password request successful for existing email")
    
    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email - should still return success"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent_user_12345@example.com"}
        )
        # Should return 200 to prevent email enumeration
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Forgot password for non-existent email returns success (security)")
    
    def test_forgot_password_missing_email(self):
        """Test forgot password with missing email"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={}
        )
        assert response.status_code == 400
        print(f"✓ Missing email returns 400 error")
    
    def test_verify_reset_token_invalid(self):
        """Test verify reset token with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/verify-reset-token?token=invalid_token_12345"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert "message" in data
        print(f"✓ Invalid token returns valid=False with message: {data['message']}")
    
    def test_verify_reset_token_missing(self):
        """Test verify reset token with missing token parameter"""
        response = requests.get(
            f"{BASE_URL}/api/auth/verify-reset-token"
        )
        # FastAPI should return 422 for missing required param or 200 with valid=False
        assert response.status_code in [200, 422]
        print(f"✓ Missing token handled correctly")
    
    def test_reset_password_invalid_token(self):
        """Test reset password with invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={
                "token": "invalid_token_xyz123",
                "password": "NewPassword123!"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
        print(f"✓ Reset password with invalid token returns 400")
    
    def test_reset_password_missing_token(self):
        """Test reset password with missing token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"password": "NewPassword123!"}
        )
        assert response.status_code == 400
        print(f"✓ Missing token returns 400")
    
    def test_reset_password_missing_password(self):
        """Test reset password with missing password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": "some_token"}
        )
        assert response.status_code == 400
        print(f"✓ Missing password returns 400")
    
    def test_reset_password_short_password(self):
        """Test reset password with password less than 8 characters"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={
                "token": "some_token",
                "password": "short"
            }
        )
        # Could be 400 for short password or 400 for invalid token (token checked first)
        assert response.status_code == 400
        print(f"✓ Short password handled correctly")
    
    def test_rate_limiting(self):
        """Test rate limiting for forgot password"""
        # Make multiple requests to test rate limiting
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/auth/forgot-password",
                json={"email": "rate_limit_test@example.com"}
            )
            # First 3 should succeed
            assert response.status_code == 200
        
        # 4th request should be rate limited (429)
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "rate_limit_test@example.com"}
        )
        assert response.status_code == 429
        data = response.json()
        assert "too many" in data["detail"].lower()
        print(f"✓ Rate limiting working after 3 requests")


class TestChangePassword:
    """Test authenticated password change (different from reset)"""
    
    def test_change_password_unauthenticated(self):
        """Test change password without authentication"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"new_password": "NewPassword123!"}
        )
        assert response.status_code in [401, 403]
        print(f"✓ Change password requires authentication")


class TestAuthLogin:
    """Test login works to verify existing auth still functional"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Login successful for admin user")
        return data["token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        print(f"✓ Invalid credentials returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
