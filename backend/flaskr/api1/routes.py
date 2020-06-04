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
    if len(category_dict) == 0: #no categories available, return a 404 error
        abort(404)
    return jsonify({
        'success': True,
        'categories': category_dict
    })


@api1.route('/questions', methods=['GET', 'POST'])
def questions():
    '''getting and posting questions, as well as searching emplementation'''
    if request.method == 'POST':
        # load the request body
        body = request.get_json()
        if not body: # empty request body should return a 400 error
            abort(400)
        # if search term and question data are posted together, abort with bad request error
        if (body.get('searchTerm') and (body.get('question') or body.get('answer') or body.get('difficulty') or body.get('category'))):
            abort(400)
        if body.get('searchTerm'):
            # searchTerm is available in the request body
            search_term = body.get('searchTerm')
            # query the database for the results
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            total_questions = len(selection)
            if total_questions == 0:
                # no questions ara available in the search results
                abort(404)
            current_questions = paginate_questions(request, selection)
            if len(current_questions) == 0:
                # search results beyond a valid page should return a 404 error
                abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions
            })
        elif (body.get('question') and body.get('answer') and body.get('difficulty') and body.get('category')):
            # posted a new question
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')
            try:
                # insert the new question to the database
                question = Question(new_question, new_answer,
                                    new_category, new_difficulty)
                question.insert()
                # query the database for all questions
                selection = Question.query.order_by(Question.id).all()
                total_questions = len(selection)
                current_questions = paginate_questions(request, selection)
                if len(current_questions) == 0:
                    # return a 404 error for envalid pages
                    abort(404)
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
    else:
        # getting all questions
        selection = Question.query.order_by(Question.id).all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
        # load all categories from db
        categories = Category.query.all()
        category_dict = {category.id: category.type for category in categories}
        if len(current_questions) == 0:
            # return a 404 error for envalid page number
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': category_dict
        })


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
    selection = Question.query.filter(Question.category == category.id).order_by(Question.id).all()
    total_questions = len(selection)
    if total_questions == 0:
        # if there are no questions for this category, return a 404 error
        abort(404)
    current_questions = paginate_questions(request, selection)
    if len(current_questions) == 0:
        # return a 404 error for envalid page number
        abort(404)
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
    if category_id == 0:
        # if category id is 0, query the database for all questions
        selection = Question.query.all()
    else:
        # load the questions from the specified category
        selection = Question.query.filter(
        Question.category == category_id).all()
    if not selection:
        # if the category has no questions, return a 404 error
        abort(404)
    total_questions = len(selection)

    def get_random_question():
        '''a function used to get a random question from the database'''
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

    # get a random question
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
