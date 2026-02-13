#!/usr/bin/env python3
"""
Digital Learning Platform
Complete e-learning platform with courses, progress tracking, and interactive content.
Built with Flask and modern web technologies.
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# In-memory storage for demo
courses = []
students = []
enrollments = []
progress = []
quizzes = []

# Module-level ID counters to avoid collision
_next_enrollment_id = 1
_next_progress_id = 1

def initialize_sample_data():
    global courses, students, enrollments, progress, quizzes
    
    # Sample courses
    courses.extend([
        {
            'id': 1,
            'title': 'Python Programming Fundamentals',
            'description': 'Learn Python from scratch with hands-on projects and real-world applications',
            'instructor': 'Dr. Sarah Johnson',
            'duration': '8 weeks',
            'level': 'beginner',
            'price': 99.99,
            'rating': 4.8,
            'students_count': 1250,
            'category': 'programming',
            'image': '/static/images/python_course.jpg',
            'modules': [
                {'id': 1, 'title': 'Introduction to Python', 'duration': '2 hours', 'completed': False},
                {'id': 2, 'title': 'Variables and Data Types', 'duration': '1.5 hours', 'completed': False},
                {'id': 3, 'title': 'Control Structures', 'duration': '2.5 hours', 'completed': False},
                {'id': 4, 'title': 'Functions and Modules', 'duration': '3 hours', 'completed': False},
                {'id': 5, 'title': 'Object-Oriented Programming', 'duration': '4 hours', 'completed': False}
            ],
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 2,
            'title': 'Data Science with R',
            'description': 'Master data analysis and visualization using R programming language',
            'instructor': 'Prof. Mike Chen',
            'duration': '10 weeks',
            'level': 'intermediate',
            'price': 149.99,
            'rating': 4.6,
            'students_count': 890,
            'category': 'data-science',
            'image': '/static/images/r_course.jpg',
            'modules': [
                {'id': 1, 'title': 'R Basics and RStudio', 'duration': '2 hours', 'completed': False},
                {'id': 2, 'title': 'Data Manipulation with dplyr', 'duration': '3 hours', 'completed': False},
                {'id': 3, 'title': 'Data Visualization with ggplot2', 'duration': '3.5 hours', 'completed': False},
                {'id': 4, 'title': 'Statistical Analysis', 'duration': '4 hours', 'completed': False},
                {'id': 5, 'title': 'Machine Learning in R', 'duration': '5 hours', 'completed': False}
            ],
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 3,
            'title': 'Web Development with React',
            'description': 'Build modern web applications using React, JavaScript, and modern tools',
            'instructor': 'Emily Davis',
            'duration': '12 weeks',
            'level': 'intermediate',
            'price': 199.99,
            'rating': 4.9,
            'students_count': 2100,
            'category': 'web-development',
            'image': '/static/images/react_course.jpg',
            'modules': [
                {'id': 1, 'title': 'JavaScript ES6+ Fundamentals', 'duration': '3 hours', 'completed': False},
                {'id': 2, 'title': 'React Components and JSX', 'duration': '2.5 hours', 'completed': False},
                {'id': 3, 'title': 'State Management and Hooks', 'duration': '4 hours', 'completed': False},
                {'id': 4, 'title': 'Routing and Navigation', 'duration': '2 hours', 'completed': False},
                {'id': 5, 'title': 'API Integration and Deployment', 'duration': '3.5 hours', 'completed': False}
            ],
            'created_at': datetime.now().isoformat()
        }
    ])
    
    # Sample students
    students.extend([
        {
            'id': 1,
            'name': 'John Smith',
            'email': 'john@email.com',
            'joined_date': datetime.now().isoformat(),
            'courses_completed': 2,
            'total_hours': 45
        },
        {
            'id': 2,
            'name': 'Jane Doe',
            'email': 'jane@email.com',
            'joined_date': datetime.now().isoformat(),
            'courses_completed': 1,
            'total_hours': 28
        }
    ])
    
    # Sample quizzes
    quizzes.extend([
        {
            'id': 1,
            'course_id': 1,
            'module_id': 1,
            'title': 'Python Basics Quiz',
            'questions': [
                {
                    'id': 1,
                    'question': 'What is the correct way to create a variable in Python?',
                    'options': ['var x = 5', 'x = 5', 'int x = 5', 'x := 5'],
                    'correct_answer': 1
                },
                {
                    'id': 2,
                    'question': 'Which of the following is a Python data type?',
                    'options': ['string', 'list', 'dictionary', 'all of the above'],
                    'correct_answer': 3
                }
            ]
        }
    ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/courses', methods=['GET'])
def get_courses():
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search', '').lower()
    
    filtered_courses = courses.copy()
    
    if category:
        filtered_courses = [c for c in filtered_courses if c['category'] == category]
    
    if level:
        filtered_courses = [c for c in filtered_courses if c['level'] == level]
    
    if search:
        filtered_courses = [c for c in filtered_courses if 
                          search in c['title'].lower() or 
                          search in c['description'].lower() or
                          search in c['instructor'].lower()]
    
    return jsonify(filtered_courses)

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = next((c for c in courses if c['id'] == course_id), None)
    if course:
        return jsonify(course)
    return jsonify({'error': 'Course not found'}), 404

@app.route('/api/enroll', methods=['POST'])
def enroll_student():
    global _next_enrollment_id
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    
    # Check if already enrolled
    existing = next((e for e in enrollments if e['student_id'] == student_id and e['course_id'] == course_id), None)
    if existing:
        return jsonify({'message': 'Already enrolled'}), 400
    
    new_enrollment = {
        'id': _next_enrollment_id,
        'student_id': student_id,
        'course_id': course_id,
        'enrolled_date': datetime.now().isoformat(),
        'progress_percentage': 0,
        'completed': False
    }
    _next_enrollment_id += 1
    enrollments.append(new_enrollment)
    return jsonify(new_enrollment), 201

@app.route('/api/progress', methods=['GET'])
def get_progress():
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    
    if student_id and course_id:
        student_progress = [p for p in progress if p['student_id'] == student_id and p['course_id'] == course_id]
        return jsonify(student_progress)
    
    return jsonify([])

@app.route('/api/progress', methods=['POST'])
def update_progress():
    global _next_progress_id
    data = request.get_json()
    
    new_progress = {
        'id': _next_progress_id,
        'student_id': data.get('student_id'),
        'course_id': data.get('course_id'),
        'module_id': data.get('module_id'),
        'completed': data.get('completed', False),
        'completion_date': datetime.now().isoformat() if data.get('completed') else None,
        'time_spent': data.get('time_spent', 0)
    }
    _next_progress_id += 1
    progress.append(new_progress)
    
    # Update enrollment progress
    enrollment = next((e for e in enrollments if 
                      e['student_id'] == new_progress['student_id'] and 
                      e['course_id'] == new_progress['course_id']), None)
    
    if enrollment:
        course = next((c for c in courses if c['id'] == new_progress['course_id']), None)
        if course:
            completed_modules = len([p for p in progress if 
                                   p['student_id'] == new_progress['student_id'] and 
                                   p['course_id'] == new_progress['course_id'] and 
                                   p['completed']])
            total_modules = len(course['modules'])
            enrollment['progress_percentage'] = (completed_modules / total_modules) * 100
            enrollment['completed'] = enrollment['progress_percentage'] == 100
    
    return jsonify(new_progress), 201

@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    quiz = next((q for q in quizzes if q['id'] == quiz_id), None)
    if quiz:
        return jsonify(quiz)
    return jsonify({'error': 'Quiz not found'}), 404

@app.route('/api/quizzes/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    data = request.get_json()
    answers = data.get('answers')
    student_id = data.get('student_id')
    
    quiz = next((q for q in quizzes if q['id'] == quiz_id), None)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    # Calculate score
    correct_answers = 0
    total_questions = len(quiz['questions'])
    
    for question in quiz['questions']:
        question_id = question['id']
        if str(question_id) in answers:
            if int(answers[str(question_id)]) == question['correct_answer']:
                correct_answers += 1
    
    score = (correct_answers / total_questions) * 100
    
    quiz_result = {
        'id': str(uuid.uuid4()),
        'quiz_id': quiz_id,
        'student_id': student_id,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'submitted_at': datetime.now().isoformat()
    }
    
    return jsonify(quiz_result)

@app.route('/api/dashboard/<int:student_id>', methods=['GET'])
def get_dashboard(student_id):
    # Get student enrollments
    student_enrollments = [e for e in enrollments if e['student_id'] == student_id]
    
    # Get enrolled courses with progress
    enrolled_courses = []
    for enrollment in student_enrollments:
        course = next((c for c in courses if c['id'] == enrollment['course_id']), None)
        if course:
            course_with_progress = course.copy()
            course_with_progress['progress'] = enrollment['progress_percentage']
            course_with_progress['completed'] = enrollment['completed']
            enrolled_courses.append(course_with_progress)
    
    # Calculate statistics
    total_courses = len(enrolled_courses)
    completed_courses = len([c for c in enrolled_courses if c['completed']])
    in_progress_courses = total_courses - completed_courses
    avg_progress = sum(c['progress'] for c in enrolled_courses) / total_courses if total_courses > 0 else 0
    
    # Recent activity
    recent_progress = sorted([p for p in progress if p['student_id'] == student_id], 
                           key=lambda x: x.get('completion_date', ''), reverse=True)[:5]
    
    return jsonify({
        'enrolled_courses': enrolled_courses,
        'statistics': {
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'in_progress_courses': in_progress_courses,
            'average_progress': avg_progress
        },
        'recent_activity': recent_progress
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(set(course['category'] for course in courses))
    category_stats = {}
    
    for category in categories:
        category_courses = [c for c in courses if c['category'] == category]
        category_stats[category] = {
            'name': category.replace('-', ' ').title(),
            'course_count': len(category_courses),
            'avg_rating': sum(c['rating'] for c in category_courses) / len(category_courses),
            'total_students': sum(c['students_count'] for c in category_courses)
        }
    
    return jsonify(category_stats)

if __name__ == '__main__':
    initialize_sample_data()
    app.run(debug=False, host='0.0.0.0', port=5000)

