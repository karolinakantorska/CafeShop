import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps
import logging
from jose import jwt
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# AUTH

AUTH0_DOMAIN = 'dev-tx01717ldfxm6fwx.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'caffe'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
    print("DEBUG: Starting JWT verification")
    print("DEBUG: Token received:", token)

    try:
        jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        print("DEBUG: JWKS fetched successfully")
    except Exception as e:
        print("DEBUG: Failed to fetch JWKS:", e)
        raise AuthError({
            'code': 'jwks_fetch_error',
            'description': 'Failed to fetch JWKS'
        }, 500)

    try:
        unverified_header = jwt.get_unverified_header(token)
        print("DEBUG: Unverified JWT header:", unverified_header)
    except jwt.DecodeError as e:
        print("DEBUG: Failed to decode JWT header:", e)
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to decode token header'
        }, 400)

    rsa_key = {}
    if 'kid' not in unverified_header:
        print("DEBUG: 'kid' not found in JWT header")
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            print("DEBUG: Matching key found in JWKS")
            break

    if not rsa_key:
        print("DEBUG: No matching key found for 'kid'")
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key.'
        }, 400)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer='https://' + AUTH0_DOMAIN + '/'
        )
        print("DEBUG: JWT decoded successfully, payload:", payload)
        payload.setdefault("permissions", [])
        return payload

    except jwt.ExpiredSignatureError:
        print("DEBUG: Token expired")
        raise AuthError({
            'code': 'token_expired',
            'description': 'Token expired.'
        }, 401)

    except jwt.JWTClaimsError as e:
        print("DEBUG: Invalid claims:", e)
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims. Check audience and issuer.'
        }, 401)

    except jwt.InvalidTokenError as e:
        print("DEBUG: Invalid token:", e)
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Token decoding failed'
        }, 401)

    except jwt.exceptions.MissingRequiredClaimError as e:
        print("DEBUG: Missing required claim:", e)
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'Missing required permission'
        }, 401)

    except Exception as e:
        print("DEBUG: Unexpected error during JWT decoding:", e)
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
        }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            # Permission check outside try-except
            permissions = payload.get('permissions', [])
            if permission and permission not in permissions:
                raise AuthError({
                    'code': 'unauthorized',
                    'description': 'Permission not found.'
                }, 403)

            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


def formatt_drinks_short(drinks_response):
    if not drinks_response:
        return []

    formatted_drinks = [drink.short() for drink in drinks_response]

    return formatted_drinks


@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()
    formated_drinks = formatt_drinks_short(drinks)
    print(formated_drinks)

    return jsonify(
        {
            "success": True,
            "drinks": formated_drinks
        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


def formatt_drinks_long(drinks_response):
    if not drinks_response:
        return []

    formatted_drinks = [drink.long() for drink in drinks_response]

    return formatted_drinks


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    print("payload", payload)
    drinks = Drink.query.all()
    formated_drinks = formatt_drinks_long(drinks)

    return jsonify(
        {
            "success": True,
            "drinks": formated_drinks
        }
    )


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    print("DEBUG: Payload received:", payload)
    body = request.get_json()

    if not body:
        abort(400, description="Missing JSON body")

    form_recipe = body.get("recipe", None)
    form_title = body.get("title", None)

    if form_title is None:
        abort(400, description="No title provided")
    if form_recipe is None:
        abort(400, description="No recipe provided")

    form_recipe = json.dumps(form_recipe)

    new_drink = Drink(
        recipe=form_recipe,
        title=form_title,
    )
    print("new_drink", new_drink)

    try:
        new_drink.insert()
        created_drink = new_drink.long()

    except BaseException:
        db.session.rollback()
        abort(500, description="Couldn't add a question")
    finally:
        db.session.close()

    return jsonify({
        "success": True,
        "drinks": created_drink
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


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404, description="Drink not found")

    body = request.get_json()

    form_recipe = body.get("recipe", None)
    form_title = body.get("title", None)

    if form_title is None:
        abort(400, description="No title provided")
    if form_recipe is None:
        abort(400, description="No recipe provided")

    form_recipe = json.dumps(form_recipe)

    drink.recipe = form_recipe
    drink.title = form_title

    try:
        drink.update()
        updated_drink = drink.long()

    except BaseException:
        db.session.rollback()
        abort(500, description="Couldn't add a question")
    finally:
        db.session.close()
    return jsonify({
        "success": True,
        "drinks": updated_drink
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


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404, description="Drink not found")

    try:
        drink.delete()

    except BaseException:
        db.session.rollback()
        abort(500, description="Couldn't add a question")
    finally:
        db.session.close()
    return jsonify({
        "success": True,
        "delete": drink_id
    }), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": str(error.description)
    }), 400


@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": str('Auth error')
    }), 400


@app.errorhandler(422)
def unprocesable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable content "
    }), 422


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False,
                    "error": 405,
                   "message": "method not allowed "
                    }), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def auth_error(error):

    return jsonify({
        "success": False,
        "error": 401,
        "message": "autentification error: "
    }), 401


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['description']
    }), ex.status_code
