from flask import Flask, jsonify, abort, current_app, request
from flask_cors import CORS
import json

from src.models import db, Drink
from src.auth.auth import AuthError

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
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the 
    newly created drink pr appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
def create_drink():
    new_drink = request.get_json()
    recipe = new_drink.get("recipe")
    title = new_drink.get("title")
    if not (recipe and title):
        abort(400)
    error = False
    unique = True

    try:
        # format given title
        title = title.title()
        unique = is_unique(title)
        if unique:
            if isinstance(recipe, dict):
                recipe = [recipe]
            drink = Drink()
            drink.title = title
            drink.recipe = json.dumps(recipe)
            drink.insert()
            formatted_drink = drink.long()
    except Exception as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(500)
    return jsonify({
        "success": True,
        "drinks": [formatted_drink]
    }), 200


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


@app.route("/drinks/<int:id>", methods=["PATCH"])
def update_drink(id):
    # get the drink to update if id exist, otherwise abort not found error
    drink = db.session.query(Drink).get_or_404(id)
    req_body = request.get_json()
    # if no data to update, abort bad request error
    if not req_body:
        abort(400)
    error = False
    # unique refers to the uniqueness of the new given title
    unique = True

    try:
        new_title = req_body.get("title")
        new_recipe = req_body.get("recipe")
        if new_title:
            # format the new title
            new_title = new_title.title()
            # verify that a new title is unique
            unique = is_unique(new_title)
            if unique:
                drink.title = new_title
        if unique:
            if new_recipe:
                drink.recipe = json.dumps(new_recipe)
            drink.update()
            formatted_drink = drink.long()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    elif not unique:
        abort(400)
    return jsonify({
        "success": True,
        "drink": [formatted_drink]
    }), 200





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


@app.route("/drinks/<int:id>", methods=["DELETE"])
def delete_drink(id):
    drink = db.session.query(Drink).get_or_404(id)
    error = False

    try:
        drink.delete()
    except Exception as e:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    return jsonify({
        "success": True,
        "delete": id
    })


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


# --------------------------------------------------------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------------------------------------------------------
def is_unique(title: str) -> bool:
    """
    check whether a given title is unique or has been used before
    :return: True if title is unique, False otherwise
    """
    return not db.session.query(Drink).filter(Drink.title == title).first()