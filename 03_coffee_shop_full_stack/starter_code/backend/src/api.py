import os
import traceback
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    short_drinks = [drink.short() for drink in all_drinks]

    return jsonify({'success': True, 'drinks': short_drinks}), 200


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    all_drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in all_drinks]

    return jsonify({'success': True, 'drinks': long_drinks}), 200


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    data = request.get_json()

    try:
        recipe = data['recipe']
        if isinstance(recipe, dict):
            recipe = [recipe]

        drink = Drink(title=data['title'], recipe=json.dumps(recipe))
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt, id):
    try:
        drink = find_drink_by_id(id)
        body = get_request_body()
        update_drink_properties(drink, body)
        drink.update()
        drinks = get_all_drinks()
        return jsonify({"success": True, "drinks": drinks}), 200
    except Exception as e:
        abort(422)


def find_drink_by_id(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    return drink


def get_request_body():
    request_body = request.get_json()
    if request_body is None:
        abort(404)
    return request_body


def update_drink_properties(drink, body):
    title = body.get('title')
    recipe = body.get('recipe')

    if title:
        drink.title = title

    if recipe:
        drink.recipe = recipe


def get_all_drinks():
    all_drinks = []
    drinks = Drink.query.all()
    for drink in drinks:
        all_drinks.append(drink.long())
    return all_drinks


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    deleted_drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not deleted_drink:
        abort(404)
    deleted_drink.delete()

    return jsonify({'success': True, 'deleted': id}), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def handle_unprocessable(error):
    response = {
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }
    return jsonify(response), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = {
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }
    return jsonify(response), error.status_code
