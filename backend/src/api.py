from flask import Flask, jsonify, abort, current_app
from flask_cors import CORS

from .models import db, Drink
from .auth.auth import AuthError

app = current_app
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_drinks():
    error = False
    try:
        drinks = [drink.short() for drink in db.session.query(Drink).all()]
    except Exception as e:
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200


'''
@TODO implement Permission
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
def drinksDetails():
    error = False
    try:
        drinks = [drink.long() for drink in db.session.query(Drink).all()]
    except Exception as e:
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# --------------------------------------------------------------------------------------------------------------------
# Error Handling
# --------------------------------------------------------------------------------------------------------------------
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource is Not Found."
    }), 404


@app.errorhandler(500)
def serverError(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server Error."
    }), 500


@app.errorhandler(400)
def badRequest(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request."
    }), 400


@app.errorhandler(401)
def unauthenticated(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthenticated "
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden, Not Authorized."
    }), 403


# Auth0 Authentication error handler
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
