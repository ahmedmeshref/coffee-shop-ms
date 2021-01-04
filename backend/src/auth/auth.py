import os
# verify JWT from AUTH0
import json
from urllib.request import urlopen
from jose import jwt
from flask import request, abort
from functools import wraps

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
ALGORITHMS = os.environ['ALGORITHMS']
API_AUDIENCE = os.environ['API_AUDIENCE']


# /server.py
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access JWT Token from the Authorization Header.
    ---
    responses:
        200:
            description: String that represents the authentication JWT token.
        401:
            description: Authentication error.
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
    """Decode and verify a given JWT token.
    ---
    parameters:
      - name: token
        in: path
        type: string
        required: true
        description: The login JWT token
    responses:
        200:
            description: payload.
        401:
            description: Authentication error due to invalid/expired token.
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
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
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def check_permission(payload, permission):
    """Verify whether the user permission meets the required permission.
    ---
    parameters:
      - name: payload
        in: path
        type: string
        required: true
        description: decoded payload contains the authentication request information.
      - name: permission
        in: path
        type: string
        required: true
        description: permission required to authorize a user.
    responses:
        200:
            description: The user is authorized.
        300:
            description: permission is missing from the payload.
        403:
            description: The user permission doesn't match the required one hence, user is not authorized.
    """
    if 'permissions' not in payload:
        abort(400)
    if permission not in payload["permissions"]:
        abort(403)
    return True


# Decorator for verifying the JWT
def require_auth(permission=''):
    def require_auth_decor(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # extract jwt token from auth header
            token = get_token_auth_header()
            try:
                # decode and verify the token
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            # validate the user authorization (user permission should match required permission by the endpoint)
            check_permission(payload, permission)
            return f(payload, *args, **kwargs)
        return wrapper
    return require_auth_decor
