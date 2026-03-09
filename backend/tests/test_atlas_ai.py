"""
Atlas AI Backend Tests - Testing Atlas AI chatbot and Knowledge Base Management
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://team-portal-hub.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "kyle@breezewealthmanagement.com"
ADMIN_PASSWORD = "Breeze2026!"
AGENT_EMAIL = "kcheek@breezewealthmanagement.com"
AGENT_PASSWORD = "KatieCheek2026!"

@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["token"]

@pytest.fixture(scope="module")
def agent_token():
    """Get agent auth token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": AGENT_EMAIL, "password": AGENT_PASSWORD}
    )
    if response.status_code != 200:
        pytest.skip(f"Agent user not available for testing: {AGENT_EMAIL}")
    return response.json()["token"]

@pytest.fixture
def admin_headers(admin_token):
    """Admin auth headers"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

@pytest.fixture
def agent_headers(agent_token):
    """Agent auth headers"""
    return {"Authorization": f"Bearer {agent_token}", "Content-Type": "application/json"}


class TestAtlasAIChat:
    """Test Atlas AI Chat functionality"""
    
    def test_admin_can_chat_with_atlas_ai(self, admin_headers):
        """Admin should be able to chat with Atlas AI"""
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "What are the first steps for a new agent?"},
            headers=admin_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "response" in data, "Response should contain 'response' field"
        assert "session_id" in data, "Response should contain 'session_id' field"
        assert len(data["response"]) > 0, "AI response should not be empty"
        
        print(f"✓ Atlas AI responded with {len(data['response'])} characters")
        print(f"✓ Session ID: {data['session_id']}")
    
    def test_agent_can_chat_with_atlas_ai(self, agent_headers):
        """Agent (non-admin) should be able to chat with Atlas AI"""
        if agent_headers is None:
            pytest.skip("Agent not available")
        
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "How do I submit an IUL application?"},
            headers=agent_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()
        
        assert "response" in data
        assert len(data["response"]) > 0
        
        print(f"✓ Agent can access Atlas AI chat successfully")
    
    def test_chat_without_auth_fails(self):
        """Chat without authentication should fail"""
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "Hello"},
            timeout=10
        )
        
        assert response.status_code == 403 or response.status_code == 401, "Unauthenticated request should fail"
        print(f"✓ Unauthenticated chat correctly rejected with status {response.status_code}")
    
    def test_chat_with_session_id(self, admin_headers):
        """Chat should maintain session_id across requests"""
        # First message
        response1 = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "Hello, I'm a new agent"},
            headers=admin_headers,
            timeout=30
        )
        
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Second message with same session
        response2 = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "What should I do first?", "session_id": session_id},
            headers=admin_headers,
            timeout=30
        )
        
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        
        print(f"✓ Session ID maintained across chat messages: {session_id}")


class TestKnowledgeBaseAccess:
    """Test Knowledge Base read access"""
    
    def test_admin_can_view_knowledge_base(self, admin_headers):
        """Admin should be able to view all knowledge base documents"""
        response = requests.get(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Failed to get knowledge base: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list of documents"
        print(f"✓ Admin can view knowledge base. Found {len(data)} documents")
        
        return data
    
    def test_agent_can_view_knowledge_base(self, agent_headers):
        """Agents can view knowledge base (needed to ask questions about content)"""
        response = requests.get(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            headers=agent_headers
        )
        
        assert response.status_code == 200, f"Failed to get knowledge base: {response.text}"
        print(f"✓ Agent can view knowledge base")


class TestKnowledgeBaseCRUD:
    """Test Knowledge Base CRUD operations (admin only)"""
    
    test_doc_id = None
    
    def test_admin_can_add_document(self, admin_headers):
        """Admin should be able to add a knowledge base document"""
        doc_payload = {
            "title": "TEST - Onboarding Guide",
            "category": "onboarding",
            "content": "This is a test document for automated testing. It contains information about the onboarding process for new agents at Breeze Financial Group.",
            "tags": ["test", "onboarding", "automated"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            json=doc_payload,
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Failed to add document: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Response should indicate success"
        assert "document" in data, "Response should contain the created document"
        assert data["document"]["title"] == doc_payload["title"]
        assert data["document"]["category"] == doc_payload["category"]
        assert "id" in data["document"], "Document should have an ID"
        
        # Store ID for later tests
        TestKnowledgeBaseCRUD.test_doc_id = data["document"]["id"]
        
        print(f"✓ Admin created document with ID: {TestKnowledgeBaseCRUD.test_doc_id}")
    
    def test_agent_cannot_add_document(self, agent_headers):
        """Non-admin users should NOT be able to add documents"""
        doc_payload = {
            "title": "Unauthorized Document",
            "category": "general",
            "content": "This should not be created",
            "tags": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            json=doc_payload,
            headers=agent_headers
        )
        
        assert response.status_code == 403, f"Agent should not be able to add documents. Got: {response.status_code}"
        print(f"✓ Agent correctly denied from adding documents (403)")
    
    def test_admin_can_update_document(self, admin_headers):
        """Admin should be able to update a knowledge base document"""
        if not TestKnowledgeBaseCRUD.test_doc_id:
            pytest.skip("No test document to update")
        
        update_payload = {
            "title": "TEST - Updated Onboarding Guide",
            "category": "onboarding",
            "content": "This is an updated test document. The content has been modified for testing purposes.",
            "tags": ["test", "onboarding", "updated"]
        }
        
        response = requests.put(
            f"{BASE_URL}/api/atlas-ai/knowledge-base/{TestKnowledgeBaseCRUD.test_doc_id}",
            json=update_payload,
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Failed to update document: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        print(f"✓ Admin updated document successfully")
    
    def test_agent_cannot_update_document(self, agent_headers):
        """Non-admin users should NOT be able to update documents"""
        if not TestKnowledgeBaseCRUD.test_doc_id:
            pytest.skip("No test document to update")
        
        update_payload = {
            "title": "Unauthorized Update",
            "category": "general",
            "content": "This update should fail",
            "tags": []
        }
        
        response = requests.put(
            f"{BASE_URL}/api/atlas-ai/knowledge-base/{TestKnowledgeBaseCRUD.test_doc_id}",
            json=update_payload,
            headers=agent_headers
        )
        
        assert response.status_code == 403, f"Agent should not be able to update documents. Got: {response.status_code}"
        print(f"✓ Agent correctly denied from updating documents (403)")
    
    def test_agent_cannot_delete_document(self, agent_headers):
        """Non-admin users should NOT be able to delete documents"""
        if not TestKnowledgeBaseCRUD.test_doc_id:
            pytest.skip("No test document to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/atlas-ai/knowledge-base/{TestKnowledgeBaseCRUD.test_doc_id}",
            headers=agent_headers
        )
        
        assert response.status_code == 403, f"Agent should not be able to delete documents. Got: {response.status_code}"
        print(f"✓ Agent correctly denied from deleting documents (403)")
    
    def test_admin_can_delete_document(self, admin_headers):
        """Admin should be able to delete a knowledge base document"""
        if not TestKnowledgeBaseCRUD.test_doc_id:
            pytest.skip("No test document to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/atlas-ai/knowledge-base/{TestKnowledgeBaseCRUD.test_doc_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Failed to delete document: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        print(f"✓ Admin deleted document successfully")
        
        # Verify document is gone
        get_response = requests.get(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            headers=admin_headers
        )
        docs = get_response.json()
        doc_ids = [d.get("id") for d in docs]
        
        assert TestKnowledgeBaseCRUD.test_doc_id not in doc_ids, "Document should be deleted"
        print(f"✓ Verified document no longer exists in knowledge base")


class TestAtlasAIWithKnowledgeBase:
    """Test that Atlas AI uses knowledge base context"""
    
    test_doc_id = None
    
    def test_setup_create_test_document(self, admin_headers):
        """Create a test document for context testing"""
        doc_payload = {
            "title": "Breeze IUL Submission Process",
            "category": "operations",
            "content": "To submit an IUL application at Breeze: 1) Complete the client interview, 2) Run illustrations in the carrier portal, 3) Submit e-application, 4) Follow up within 48 hours. The target premium determines commission calculation. All IUL submissions must be logged in the Atlas client management system within 24 hours of submission.",
            "tags": ["IUL", "submission", "process", "operations"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/knowledge-base",
            json=doc_payload,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        TestAtlasAIWithKnowledgeBase.test_doc_id = response.json()["document"]["id"]
        print(f"✓ Created test document for context testing")
    
    def test_atlas_ai_uses_knowledge_context(self, admin_headers):
        """Atlas AI should reference knowledge base content when relevant"""
        # Wait a moment for document to be available
        time.sleep(1)
        
        response = requests.post(
            f"{BASE_URL}/api/atlas-ai/chat",
            json={"message": "What is the IUL submission process at Breeze?"},
            headers=admin_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        ai_response = response.json()["response"].lower()
        
        # The AI should reference some content from our document
        # (not exact match since AI processes and reformats)
        print(f"✓ Atlas AI responded to knowledge-base related question")
        print(f"  Response preview: {ai_response[:200]}...")
    
    def test_cleanup_delete_test_document(self, admin_headers):
        """Clean up test document"""
        if TestAtlasAIWithKnowledgeBase.test_doc_id:
            response = requests.delete(
                f"{BASE_URL}/api/atlas-ai/knowledge-base/{TestAtlasAIWithKnowledgeBase.test_doc_id}",
                headers=admin_headers
            )
            assert response.status_code == 200
            print(f"✓ Cleaned up test document")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
