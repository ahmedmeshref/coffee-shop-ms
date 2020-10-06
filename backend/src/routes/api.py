from flask import jsonify, abort, current_app, request
from flask_cors import CORS
import json

from src.models import db, Drink
from src.auth.auth import AuthError
from src.auth.auth import require_auth

app = current_app
CORS(app)


# -------------------------------------------------------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------------------------------------------------------

@app.route("/drinks")
def get_drinks():
    """Get a list of short representation for all drinks in DB.
    ---
    permission:
        Accessible for all users.
    responses:
        200:
            description: A list of all drinks in DB.
            example:
            {
                "success": True,
                "drinks": [{
                  "id": 2,
                  "recipe": [
                    {
                      "color": "red",
                      "parts": 2
                    }
                  ],
                  "title": "Coca"
                }]
            }
        500:
            description: A server error occurred
    """
    error = False
    # try:
    drinks = [drink.short() for drink in db.session.query(Drink).all()]
    # except Exception as e:
    #     error = True
    # finally:
    #     db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200


@app.route("/drinks-detail")
@require_auth("get:drinks-detail")
def drinksDetails(payload):
    """Get a list of long representation for all drinks in DB.
    ---
    parameters:
      - name: payload
        in: path
        type: string
        required: true
        description: The login payload
    permission:
        Accessible for managers and barista.
    responses:
        200:
            description: A list of all drinks in DB.
            example:
            {
                "success": True,
                "drinks": [{
                  "id": 2,
                  "recipe": [
                    {
                      "color": "red",
                      "name": "cocacola"
                      "parts": 2
                    }
                  ],
                  "title": "Coca"
                }]
            }
        401:
            description: User was not authenticated (logged in).
        500:
            description: A server error occurred
    """
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


@app.route("/drinks", methods=["POST"])
@require_auth("post:drinks")
def create_drink(payload):
    """Create a new drink.
    ---
    parameters:
      - name: payload
        in: path
        type: string
        required: true
        description: The login payload
    permission:
        Accessible for managers only.
    Request:
        - JSON object that includes Title and recipe details.
        example:
        {
            "title": "banana",
            "recipe": [{"color": "yellow", "name": "ba", "parts":10}]
        }
    responses:
        200:
            description: A list contains the newly added drink.
            example:
                {
                "success": True,
                "drinks": [{
                  "id": 10,
                  "recipe": [
                    {
                      "color": "yellow",
                      "name": "ba"
                      "parts": 10
                    }
                  ],
                  "title": "Banana"
                }]
               }
        401:
            description: User was not authenticated (logged in).
        403:
            description: User was not authorized to create a new drink.
        500:
            description: A server error occurred
        400:
            description: Bad request was sent, either title, recipe, or both were missing from the request body.
    """
    new_drink = request.get_json()
    recipe = new_drink.get('recipe', None)
    title = new_drink.get("title", None)
    # if request doesn't contain recipe or a title, return 400: bad request error.
    if not (recipe and title):
        abort(400)

    error = False

    try:
        # format given recipe
        if isinstance(recipe, dict):
            recipe = [recipe]
        drink = Drink()
        drink.title = title.title()
        drink.recipe = json.dumps(recipe)
        drink.insert()
        formatted_drink = [drink.long()]
    except Exception as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(500)
    return jsonify({
        "success": True,
        "drinks": formatted_drink
    }), 200


@app.route("/drinks/<int:id>", methods=["PATCH"])
@require_auth("patch:drinks")
def update_drink(payload, id):
    """Update the data of an existing drink.
    ---
    parameters:
      - name: payload
        in: path
        type: string
        required: true
        description: The login payload
      - name: id
        in: path
        type: int
        required: true
        description: The id of the target drink to update
    permission:
        Accessible for managers only.
    request:
        - JSON object that includes Title and/or recipe details.
        example:
        {
            "recipe": [{"color": "brown", "name": "KZ", "parts":8}]
        }
    responses:
        200:
            description: A list contains the update drink.
            example:
                {
                "success": True,
                "drinks": [{
                  "id": 10,
                  "recipe": [
                    {
                      "color": "brown",
                      "name": "KZ"
                      "parts": 8
                    }
                  ],
                  "title": "Banana"
                }]
               }
        401:
            description: User was not authenticated (logged in).
        403:
            description: User was not authorized to create a new drink.
        500:
            description: A server error occurred
        400:
            description: Bad/empty request was sent, or giving id doesn't match any existing drink.
    """
    # get the drink to update if id exist, otherwise abort not found error
    drink = db.session.query(Drink).get_or_404(id)
    req_body = request.get_json()
    # if no data to update, return 400: bad request error.
    if not req_body:
        abort(400)
    error = False

    try:
        new_title = req_body.get("title")
        new_recipe = req_body.get("recipe")
        if new_title:
            # format the new title
            drink.title = new_title.title()
        if new_recipe:
            drink.recipe = json.dumps(new_recipe)
        drink.update()
        formatted_drink = [drink.long()]
    except Exception as e:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    return jsonify({
        "success": True,
        "drink": formatted_drink
    }), 200


@app.route("/drinks/<int:id>", methods=["DELETE"])
@require_auth("delete:drinks")
def delete_drink(payload, id):
    """Delete an existing drink giving its id.
    ---
    parameters:
      - name: payload
        in: path
        type: string
        required: true
        description: The login payload
      - name: id
        in: path
        type: int
        required: true
        description: The id of the target drink to delete
    permission:
        Accessible for managers only.
    responses:
        200:
            description: A list contains the update drink.
            example:
                {
                "success": True,
                "id": 10
               }
        401:
            description: User was not authenticated (logged in).
        403:
            description: User was not authorized to create a new drink.
        500:
            description: A server error occurred
        400:
            description: Bad request was sent (id doesn't match any existing drink).
    """
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
