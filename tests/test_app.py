"""Tests for the Digital Learning Platform Flask API."""

import pytest
import sys
import os


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from app import app, initialize_sample_data, courses, enrollments, quizzes, progress


    @pytest.fixture
    def client():
        """Create a test client with fresh sample data."""
        app.config['TESTING'] = True
        # Clear and reinitialize data for each test
        courses.clear()
        enrollments.clear()
        quizzes.clear()
        progress.clear()
        initialize_sample_data()
        with app.test_client() as client:
            yield client


    def test_get_courses_returns_200_with_list(client):
        """GET /api/courses returns 200 and a list of courses."""
        response = client.get('/api/courses')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3


    def test_get_course_by_id(client):
        """GET /api/courses/<id> returns the correct course."""
        response = client.get('/api/courses/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['title'] == 'Python Programming Fundamentals'


    def test_get_course_not_found(client):
        """GET /api/courses/<id> returns 404 for missing course."""
        response = client.get('/api/courses/999')
        assert response.status_code == 404


    def test_enroll_student(client):
        """POST /api/enroll creates an enrollment."""
        response = client.post('/api/enroll', json={
            'student_id': 1,
            'course_id': 1
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['student_id'] == 1
        assert data['course_id'] == 1
        assert data['progress_percentage'] == 0


    def test_enroll_duplicate_rejected(client):
        """POST /api/enroll rejects duplicate enrollment."""
        client.post('/api/enroll', json={'student_id': 1, 'course_id': 1})
        response = client.post('/api/enroll', json={'student_id': 1, 'course_id': 1})
        assert response.status_code == 400


    def test_get_dashboard(client):
        """GET /api/dashboard/<student_id> returns stats."""
        # Enroll first so dashboard has data
        client.post('/api/enroll', json={'student_id': 1, 'course_id': 1})
        response = client.get('/api/dashboard/1')
        assert response.status_code == 200
        data = response.get_json()
        assert 'statistics' in data
        assert 'enrolled_courses' in data
        assert data['statistics']['total_courses'] == 1


    def test_submit_quiz_with_quiz_id(client):
        """POST /api/quizzes/<id>/submit works with quiz_id route param."""
        response = client.post('/api/quizzes/1/submit', json={
            'student_id': 1,
            'answers': {'1': 1, '2': 3}
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['quiz_id'] == 1
        assert data['score'] == 100.0
        assert data['correct_answers'] == 2


    def test_submit_quiz_not_found(client):
        """POST /api/quizzes/<id>/submit returns 404 for missing quiz."""
        response = client.post('/api/quizzes/999/submit', json={
            'student_id': 1,
            'answers': {}
        })
        assert response.status_code == 404


    def test_get_categories(client):
        """GET /api/categories returns category stats."""
        response = client.get('/api/categories')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'programming' in data
