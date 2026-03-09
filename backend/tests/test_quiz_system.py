"""
Test suite for the Quiz System in Breeze Matrix
Tests quiz questions, check-answer, submit, and progress endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://team-portal-hub.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "kyle@breezewealthmanagement.com"
TEST_PASSWORD = "Breeze2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestQuizQuestions:
    """Test quiz questions endpoint"""
    
    def test_get_iul_easy_questions(self, auth_headers):
        """Test getting IUL Easy questions"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=IUL&difficulty=Easy",
            headers=auth_headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 10, f"Expected 10 questions, got {len(questions)}"
        
        # Verify question structure
        for q in questions:
            assert "id" in q
            assert "question" in q
            assert "options" in q
            assert "product" in q
            assert "difficulty" in q
            assert "category" in q
            # Verify correct_answer is NOT exposed
            assert "correct_answer" not in q
            assert "explanation" not in q
    
    def test_get_fia_intermediate_questions(self, auth_headers):
        """Test getting FIA Intermediate questions"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=FIA&difficulty=Intermediate",
            headers=auth_headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 10
    
    def test_get_term_expert_questions(self, auth_headers):
        """Test getting Term Expert questions"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=Term&difficulty=Expert",
            headers=auth_headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 10
    
    def test_get_final_expense_questions(self, auth_headers):
        """Test getting Final Expense questions"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=Final Expense&difficulty=Easy",
            headers=auth_headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 10
    
    def test_invalid_product(self, auth_headers):
        """Test invalid product returns error"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=InvalidProduct&difficulty=Easy",
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_invalid_difficulty(self, auth_headers):
        """Test invalid difficulty returns error"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=IUL&difficulty=SuperHard",
            headers=auth_headers
        )
        assert response.status_code == 400


class TestCheckAnswer:
    """Test check-answer endpoint for immediate feedback"""
    
    def test_check_answer_correct(self, auth_headers):
        """Test checking a correct answer"""
        # First get questions
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=IUL&difficulty=Easy",
            headers=auth_headers
        )
        questions = response.json()
        question_id = questions[0]["id"]
        
        # Try each option until we find the correct one
        for option in ["A", "B", "C", "D"]:
            check_response = requests.post(
                f"{BASE_URL}/api/quiz/check-answer",
                headers=auth_headers,
                json={"question_id": question_id, "selected_answer": option}
            )
            assert check_response.status_code == 200
            result = check_response.json()
            
            # Verify response structure
            assert "question_id" in result
            assert "selected_answer" in result
            assert "correct_answer" in result
            assert "is_correct" in result
            assert "explanation" in result
            
            if result["is_correct"]:
                assert result["selected_answer"] == result["correct_answer"]
                break
    
    def test_check_answer_invalid_question(self, auth_headers):
        """Test checking answer for non-existent question"""
        response = requests.post(
            f"{BASE_URL}/api/quiz/check-answer",
            headers=auth_headers,
            json={"question_id": "invalid-id", "selected_answer": "A"}
        )
        assert response.status_code == 404


class TestQuizSubmission:
    """Test quiz submission endpoint"""
    
    def test_submit_quiz(self, auth_headers):
        """Test submitting a complete quiz"""
        # Get questions
        response = requests.get(
            f"{BASE_URL}/api/quiz/questions?product=IUL&difficulty=Easy",
            headers=auth_headers
        )
        questions = response.json()
        
        # Create answers (just pick A for all - some will be right, some wrong)
        answers = [
            {"question_id": q["id"], "selected_answer": "A"}
            for q in questions
        ]
        
        # Submit quiz
        submit_response = requests.post(
            f"{BASE_URL}/api/quiz/submit",
            headers=auth_headers,
            json={
                "product": "IUL",
                "difficulty": "Easy",
                "answers": answers
            }
        )
        assert submit_response.status_code == 200
        result = submit_response.json()
        
        # Verify response structure
        assert "score" in result
        assert "total_questions" in result
        assert "percentage" in result
        assert "passed" in result
        assert "question_results" in result
        assert "category_scores" in result
        
        # Verify values
        assert result["total_questions"] == 10
        assert 0 <= result["score"] <= 10
        assert 0 <= result["percentage"] <= 100
        assert result["passed"] == (result["percentage"] >= 70)
    
    def test_submit_quiz_wrong_answer_count(self, auth_headers):
        """Test submitting quiz with wrong number of answers"""
        response = requests.post(
            f"{BASE_URL}/api/quiz/submit",
            headers=auth_headers,
            json={
                "product": "IUL",
                "difficulty": "Easy",
                "answers": [{"question_id": "test", "selected_answer": "A"}]  # Only 1 answer
            }
        )
        assert response.status_code == 400


class TestQuizProgress:
    """Test quiz progress endpoint"""
    
    def test_get_progress(self, auth_headers):
        """Test getting user's quiz progress"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/progress",
            headers=auth_headers
        )
        assert response.status_code == 200
        progress = response.json()
        
        # Verify structure
        assert "user_id" in progress
        assert "total_quizzes_taken" in progress
        assert "total_passed" in progress
        assert "current_streak" in progress
        assert "best_streak" in progress
        assert "achievements" in progress
        assert "product_stats" in progress
        assert "recent_attempts" in progress


class TestQuizHistory:
    """Test quiz history endpoint"""
    
    def test_get_history(self, auth_headers):
        """Test getting quiz attempt history"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/history",
            headers=auth_headers
        )
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)


class TestAdminQuizEndpoints:
    """Test admin quiz management endpoints"""
    
    def test_admin_get_questions(self, auth_headers):
        """Test admin getting all questions"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/admin/questions",
            headers=auth_headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) > 0
    
    def test_admin_get_stats(self, auth_headers):
        """Test admin getting quiz stats"""
        response = requests.get(
            f"{BASE_URL}/api/quiz/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        assert "question_counts" in stats
        assert "total_attempts" in stats
        assert "pass_rate" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
