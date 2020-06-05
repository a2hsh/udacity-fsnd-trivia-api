# tests for the API
import json
from flaskr import create_app, db
from flaskr.models import Question, Category
import math
# generating random queries for the data
from sqlalchemy import func, desc
import unittest


class TriviaAPI(unittest.TestCase):
    '''
    base class for testing the API
    '''

    # Setup and teardown methods
    # executed before and after each test.
    def setUp(self):
        # creating the application
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        # push the application context with all extentions
        self.app_context.push()
        with self.app.test_client():
            self.client = self.app.test_client()

    def tearDown(self):
        # pop the app context
        self.app_context.pop()

    def test_get_paginated_questions(self):
        '''
        tests getting all questions with pagination
        '''
        # get response json, then load the data
        response = self.client.get('/api/v1/questions')
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # questions and total_questions should be present in data
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        # questions and total_questions length should be more than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)

    def test_envalid_question_page(self):
        # get total questions from DB
        total_questions = len(Question.query.all())
        # get response json, requesting the page dynamically, then load the data
        response = self.client.get(
            f'/api/v1/questions?page={math.ceil(total_questions / 10) + 1}')
        data = json.loads(response.data)
        # status code should be 404
        self.assertEqual(response.status_code, 404)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'resource not found'
        self.assertEqual(data['message'], 'resource not found')

    def test_empty_post_questions(self):
        '''
        tests posting an empty questions json
        '''
        # get response json, then load the data
        response = self.client.post('/api/v1/questions',
                                    json={})
        data = json.loads(response.data)
        # status code should be 400
        self.assertEqual(response.status_code, 400)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'bad request'
        self.assertEqual(data['message'], 'bad request')

    def test_post_search_questions(self):
        '''
        tests posting a search for questions
        '''
        # get response json, then load the data
        response = self.client.post('/api/v1/questions/search',
                                    json={'searchTerm': 'title'})
        data = json.loads(response.data)
        # success should be true
        self.assertTrue(data['success'])
        # questions and total_questions should be present in data
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        # questions and total_questions length should be more than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)

    def test_envalid_post_search_questions(self):
        '''
        tests posting an envalid search for questions
        '''
        # get response json, then load the data
        response = self.client.post('/api/v1/questions/search',
                                    json={'searchTerm': 'blahblahblah'})
        data = json.loads(response.data)
        # status code should be 404
        self.assertEqual(response.status_code, 404)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'resource not found'
        self.assertEqual(data['message'], 'resource not found')

    def test_bad_post_search_questions(self):
        '''
        tests posting an empty search for questions
        '''
        # get response json, then load the data
        response = self.client.post('/api/v1/questions/search',
                                    json={'searchTerm': ''})
        data = json.loads(response.data)
        # status code should be 400
        self.assertEqual(response.status_code, 400)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'bad request'
        self.assertEqual(data['message'], 'bad request')

    def test_post_new_question(self):
        '''
        tests posting a new question
        '''
        # get response json, then load the data
        response = self.client.post('/api/v1/questions', json={
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 3,
            'category': 1})
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # questions, question.id, question.question and total_questions should be present
        self.assertIn('questions', data)
        self.assertIn('id', data)
        self.assertIn('question', data)
        self.assertIn('total_questions', data)
        # questions and total_questions length should be more than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)
        # compair total_questions with length from db
        questions_before_delete = len(Question.query.all())
        self.assertEqual(data['total_questions'], questions_before_delete)
        # cleanup the DB.
        question = Question.query.get(data['id'])
        question.delete()
        # this insures that the app returns to its origional state before the test
        questions_after_delete = len(Question.query.all())
        self.assertEqual(questions_before_delete - questions_after_delete, 1)

    def test_get_category_questions(self):
        '''
        tests getting questions by category
        '''
        # get the first random category from db
        category = Category.query.order_by(func.random()).first()
        # get response json, then load the data
        response = self.client.get(
            f'/api/v1/categories/{category.id}/questions')
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # questions and total_questions should be present
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        # questions and total_questions length should be more than 0
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        # total_questions should be an integer
        self.assertEqual(type(data['total_questions']), int)
        # current_category equals to category.type
        self.assertEqual(data['current_category'], category.type)
        # for each question, category id should be the same id from db
        for question in data['questions']:
            self.assertEqual(question['category'], category.id)

    def test_get_envalid_category(self):
        '''
        tests getting questions by envalid category
        '''
        # get the first random category from db
        category = Category.query.order_by(desc(Category.id)).first()
        # get response json, then load the data
        response = self.client.get(
            f'/api/v1/categories/{category.id + 1}/questions')
        data = json.loads(response.data)
        # status code should be 404
        self.assertEqual(response.status_code, 404)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'resource not found'
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        '''
        tests getting all categories
        '''
        # get response json, then load the data
        response = self.client.get('/api/v1/categories')
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # categories should be present
        self.assertTrue(data['categories'])
        # categories length should be more than 0
        self.assertGreater(len(data['categories']), 0)

    def test_play_quiz(self):
        '''
        tests playing a quizs
        '''
        # query db for 2 random questions
        questions = Question.query.order_by(func.random()).limit(2).all()
        previous_questions = [question.id for question in questions]
        # post response json, then load the data
        response = self.client.post('/api/v1/quizzes', json={
            'previous_questions': previous_questions,
            'quiz_category': {'id': 2}
        })
        data = json.loads(response.data)
        # status code should be 200
        self.assertEqual(response.status_code, 200)
        # success should be true
        self.assertTrue(data['success'])
        # question should be present
        self.assertTrue(data['question'])

    def test_failed_play_quiz(self):
        '''
        tests playing a quizs with empty json
        '''
        # post empty json response json, then load the data
        response = self.client.post('/api/v1/quizzes', json={})
        data = json.loads(response.data)
        # status code should be 400
        self.assertEqual(response.status_code, 400)
        # success should be false
        self.assertFalse(data['success'])
        # message should be 'bad request'
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
