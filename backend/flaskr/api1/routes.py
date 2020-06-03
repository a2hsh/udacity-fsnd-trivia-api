# routes.py
# for rendering api routes
from flaskr import db
from flaskr.models import Question, Category
from . import api1
from flask import abort, request, jsonify, current_app
import random

# Defining global variables.
QUESTIONS_PER_PAGE = 10

# pagination utility


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


@api1.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response


@api1.route('/categories')
def get_categories():
    categories = Category.query.all()
    category_dict = {category.id: category.type for category in categories}
    if len(category_dict) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'categories': category_dict
    })


@api1.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        body = request.get_json()
        if not body:
            abort(400)
        # if search term and question data are posted together, abort with bad request error
        if (body.get('searchTerm') and (body.get('question') or body.get('answer') or body.get('difficulty') or body.get('category'))):
            abort(400)
        if body.get('searchTerm'):
            search_term = body.get('searchTerm')
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            total_questions = len(selection)
            if total_questions == 0:
                abort(404)
            current_questions = paginate_questions(request, selection)
            if len(current_questions) == 0:
                abort(400)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions
            })
        elif (body.get('question') and body.get('answer') and body.get('difficulty') and body.get('category')):
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')
            try:
                question = Question(new_question, new_answer,
                                    new_category, new_difficulty)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                total_questions = len(selection)
                current_questions = paginate_questions(request, selection)
                if len(current_questions) == 0:
                    abort(404)
                return jsonify({
                    'success': True,
                    'id': question.id,
                    'question': question.question,
                    'questions': current_questions,
                    'total_questions': total_questions
                })
            except:
                abort(422)
        else:
            abort(400)
    else:
        selection = Question.query.order_by(Question.id).all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()
        category_dict = {category.id: category.type for category in categories}
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': category_dict
        })


@api1.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        # return 404 if question is not available
        if question is None:
            abort(404)
        question.delete()
        return jsonify({
            'success': True,
            'deleted': question_id
        })
    except:
        abort(422)


@api1.route('/categories/<category_id>/questions')
def get_questions_by_category(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()
    if category is None:
        abort(400)
    selection = Question.query.filter(Question.category == category.id).all()
    if selection is None:
        abort(404)
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)
    if len(current_questions) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'current_category': category.type
    })


@api1.route('/quizzes', methods=['POST'])
def play_quiz():
    try:
        body = request.get_json()
        if (body.get('previous_questions') is None or body.get('quiz_category') is None):
            abort(400)
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        if quiz_category['id'] == 0:
            selection = Question.query.all()
        else:
            selection = Question.query.filter(
                Question.category == quiz_category['id']).all()
        total_questions = len(selection)

        def get_random_question():
            # check if there are no questions left to be randomized before getting stuck in a while loop
            if len(previous_questions) == total_questions:
                # All questions were played, let's get outa here
                return None
            while True:
                question = selection[random.randrange(0, len(selection), 1)]
                # Continue to randomize until finding a question that's not played before
                if question.id in previous_questions:
                    continue
                else:
                    # found a question, so break out of the while loop
                    break
            return question

        question = get_random_question()
        if question is None:
            # all questions were played, returning a success message without a question signifies the end of the game
            return jsonify({
                'success': True
            })
        # Found a question that wasn't played before, let's return it to the user
        return jsonify({
            'success': True,
            'question': question.format()
        })
    except:
        abort(400)

# error handlers


@api1.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@api1.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@api1.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405


@api1.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422
