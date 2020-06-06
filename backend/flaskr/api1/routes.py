# routes.py
# for rendering api routes
from flaskr import db
from flaskr.models import Question, Category
from . import api1
from flask import abort, request, jsonify, current_app
from sqlalchemy import func

import random


@api1.after_request
def after_request(response):
    '''defining extra headers'''
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    response.headers.add('Content-Type', 'application/json')
    return response


@api1.route('/categories')
def get_categories():
    '''get all categories'''
    categories = Category.query.all()
    category_dict = {category.id: category.type for category in categories}
    if len(category_dict) == 0:  # no categories available, return a 404 error
        abort(404)
    return jsonify({
        'success': True,
        'categories': category_dict
    })


@api1.route('/questions')
def get_questions():
    '''gett all questions'''
    # paginate questions, and store the current page questions in a list
    page = request.args.get('page', 1, type=int)
    selection = Question.query.order_by(Question.id).paginate(
        page, current_app.config['QUESTIONS_PER_PAGE'], True)
    total_questions = selection.total
    if total_questions == 0:
        # no questions are found, abort with a 404 error.
        abort(404)
    current_questions = [question.format() for question in selection.items]
    # load all categories from db
    categories = Category.query.all()
    category_dict = {category.id: category.type for category in categories}
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': category_dict
    })


@api1.route('/questions/search', methods=['POST'])
def search_questions():
    '''search for a question in the database'''
    body = request.get_json()
    if not body:
        # posting an envalid json should return a 400 error.
        abort(400)
    if body.get('searchTerm'):
        # searchTerm is available in the request body
        search_term = body.get('searchTerm')
        # query the database for paginated results, store the current page results in a list
        page = request.args.get('page', 1, type=int)
        selection = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).paginate(page, current_app.config['QUESTIONS_PER_PAGE'], True)
        total_questions = selection.total
        if total_questions == 0:
            # no questions are available in the search results
            abort(404)
        current_questions = [question.format() for question in selection.items]
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions
        })
    else:
        # if searchTerm was not posted, return a 400 error
        abort(400)


@api1.route('/questions', methods=['POST'])
def post_new_question():
    body = request.get_json()
    if not body:
        # posting an envalid json should return a 400 error.
        abort(400)
    if (body.get('question') and body.get('answer') and body.get('difficulty') and body.get('category')):
        # posted a new question
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')
        # insure that difficulty is only from 1 to 5
        if not 1 <= int(new_difficulty) < 6:
            abort(400)
        try:
            # insert the new question to the database
            question = Question(new_question, new_answer,
                                new_category, new_difficulty)
            question.insert()
            # query the database for all questions
            page = request.args.get('page', 1, type=int)
            selection = Question.query.order_by(Question.id).paginate(
                page, current_app.config['QUESTIONS_PER_PAGE'], True)
            total_questions = selection.total
            if total_questions == 0:
                # no questions were found, return a 404 error.
                abort(404)
            current_questions = [question.format()
                                 for question in selection.items]
            return jsonify({
                'success': True,
                'id': question.id,
                'question': question.question,
                'questions': current_questions,
                'total_questions': total_questions
            })
        except:
            # creating the question failed, rollback and close the connection
            db.session.rollback()
            abort(422)
    else:
        # anything else posted in the body should return a 400 error
        abort(400)


@api1.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    '''Delete a question from the database'''
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
        # rollback and close the connection
        db.session.rollback()
        abort(422)


@api1.route('/categories/<category_id>/questions')
def get_questions_by_category(category_id):
    '''Get all questions for a specific category'''
    category = Category.query.filter(Category.id == category_id).one_or_none()
    # abort with a 404 error if category is unavailable
    if category is None:
        abort(404)
    # paginate questions, and store the current page questions in a list
    page = request.args.get('page', 1, type=int)
    selection = Question.query.filter(
        Question.category == category.id).order_by(Question.id).paginate(page, current_app.config['QUESTIONS_PER_PAGE'], True)
    total_questions = selection.total
    if total_questions == 0:
        # if there are no questions for this category, return a 404 error
        abort(404)
    total_questions = selection.total
    current_questions = [question.format() for question in selection.items]
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'current_category': category.type
    })


@api1.route('/quizzes', methods=['POST'])
def play_quiz():
    '''play quiz game'''
    # load the request body
    body = request.get_json()
    if not body:
        # posting an envalid json should return a 400 error.
        abort(400)
    if (body.get('previous_questions') is None or body.get('quiz_category') is None):
        # if previous_questions or quiz_category are missing, return a 400 error
        abort(400)
    previous_questions = body.get('previous_questions')
    if type(previous_questions) != list:
        # previous_questions should be a list, otherwise return a 400 error
        abort(400)
    category = body.get('quiz_category')
    # just incase, convert category id to integer
    category_id = int(category['id'])
    # insure that there are questions to be played.
    if category_id == 0:
        # if category id is 0, query the database for a random object of all questions
        selection = Question.query.order_by(func.random())
    else:
        # load a random object of questions from the specified category
        selection = Question.query.filter(
            Question.category == category_id).order_by(func.random())
    if not selection.all():
        # No questions available, abort with a 404 error
        abort(404)
    else:
        # load a random question from our previous query, which is not in the previous_questions list.
        question = selection.filter(Question.id.notin_(
            previous_questions)).first()
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


@api1.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal error'
    }), 500
