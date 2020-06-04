# pytests for the API
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app, db
from flaskr.models import Question, Category
import math
# generating random queries for the data
from sqlalchemy import func, desc
import pytest


@pytest.fixture
def app():
    app = create_app('testing')
    return app


def test_get_paginated_questions(client):
    '''
    tests getting all questions with pagination
    '''
    # get response json, then load the data
    response = client.get('/api/v1/questions')
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True
    # questions should be present
    assert 'questions' in data
    # questions length should not be 0
    assert len(data['questions']) != 0
    # total_questions should be present
    assert 'total_questions' in data
    # total_questions should be an integer
    assert type(data['total_questions']) is int
    # total_questions should not be 0
    assert data['total_questions'] != 0


def test_envalid_question_page(client):
    # get total questions from DB
    total_questions = len(Question.query.all())
    # get response json, requesting the page dynamically, then load the data
    response = client.get(
        f'/api/v1/questions?page={math.ceil(total_questions / 10) + 1}')
    data = json.loads(response.data)
    # status code should be 404
    assert response.status_code == 404
    # success should be false
    assert data['success'] is False
    # message should be 'resource not found'
    assert data['message'] == 'resource not found'


def test_empty_post_questions(client):
    '''
    tests posting an empty questions json
    '''
    # get response json, then load the data
    response = client.post('/api/v1/questions',
                           json={})
    data = json.loads(response.data)
    # status code should be 404
    assert response.status_code == 400
    # success should be false
    assert data['success'] is False
    # message should be 'bad request'
    assert data['message'] == 'bad request'


def test_post_search_questions(client):
    '''
    tests posting a search for questions
    '''
    # get response json, then load the data
    response = client.post('/api/v1/questions', json={'searchTerm': 'title'})
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True
    # questions should be present
    assert 'questions' in data
    # questions length should not be 0
    assert len(data['questions']) != 0


def test_envalid_post_search_questions(client):
    '''
    tests posting an envalid search for questions
    '''
    # get response json, then load the data
    response = client.post('/api/v1/questions',
                           json={'searchTerm': 'blahblahblah'})
    data = json.loads(response.data)
    # status code should be 404
    assert response.status_code == 404
    # success should be false
    assert data['success'] is False
    # message should be 'resource not found'
    assert data['message'] == 'resource not found'


def test_bad_post_search_questions(client):
    '''
    tests posting an empty search for questions
    '''
    # get response json, then load the data
    response = client.post('/api/v1/questions',
                           json={'searchTerm': ''})
    data = json.loads(response.data)
    # status code should be 400
    assert response.status_code == 400
    # success should be false
    assert data['success'] is False
    # message should be 'bad request'
    assert data['message'] == 'bad request'


def test_post_new_question(client):
    '''
    tests posting a new question
    '''
    # get response json, then load the data
    response = client.post('/api/v1/questions', json={
        'question': 'test question',
        'answer': 'test answer',
        'difficulty': 3,
        'category': 1})
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True
    # questions, question.id, and question.question should be present
    assert 'questions' in data
    assert 'id' in data
    assert 'question' in data
    # current_questions length should not be 0
    assert len(data['questions']) != 0
    # compair total_questions with length from db
    questions_before_delete = len(Question.query.all())
    assert data['total_questions'] == questions_before_delete
    # cleanup the DB.
    question = Question.query.get(data['id'])
    question.delete()
    # this insures that the app returns to its origional state before the test
    questions_after_delete = len(Question.query.all())
    assert questions_before_delete - questions_after_delete == 1


def test_get_category_questions(client):
    '''
    tests getting questions by category
    '''
    # get the first random category from db
    category = Category.query.order_by(func.random()).first()
    # get response json, then load the data
    response = client.get(f'/api/v1/categories/{category.id}/questions')
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True
    # questions should be present
    assert 'questions' in data
    # questions length should not be 0
    assert len(data['questions']) != 0
    # current_category equals to category.type
    assert data['current_category'] == category.type

    # for each question, category id should be the same id from db
    for question in data['questions']:
        assert question['category'] == category.id


def test_get_envalid_category(client):
    '''
    tests getting questions by envalid category
    '''
    # get the first random category from db
    category = Category.query.order_by(desc(Category.id)).first()
    # get response json, then load the data
    response = client.get(f'/api/v1/categories/{category.id + 1}/questions')
    data = json.loads(response.data)
    # status code should be 404
    assert response.status_code == 404
    # success should be false
    assert data['success'] is False
    # message should be 'resource not found'
    assert data['message'] == 'resource not found'


def test_get_categories(client):
    '''
    tests getting all categories
    '''
    # get response json, then load the data
    response = client.get('/api/v1/categories')
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True
    # categories should be present
    assert 'categories' in data
    # categories length should not be 0
    assert len(data['categories']) != 0


def test_play_quiz(client):
    '''
    tests playing a quizs
    '''
    # query db for 2 random questions
    questions = Question.query.order_by(func.random()).limit(2).all()
    previous_questions = [question.id for question in questions]
    # post response json, then load the data
    response = client.post('/api/v1/quizzes', json={
        'previous_questions': previous_questions,
        'quiz_category': {'id': 2}
    })
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 200
    # success should be true
    assert data['success'] is True


def test_failed_play_quiz(client):
    '''
    tests playing a quizs with empty json
    '''
    # post empty json response json, then load the data
    response = client.post('/api/v1/quizzes', json={})
    data = json.loads(response.data)
    # status code should be 200
    assert response.status_code == 400
    # success should be true
    assert data['success'] is False
    # message should be 'bad request'
    assert data['message'] == 'bad request'
