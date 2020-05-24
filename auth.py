from os import environ
import jwt
from collections.abc import Iterable
from models.errors import AuthError
from flask import request
from functools import wraps
import random
import string
import hashlib
import datetime


JWT_SECRET = environ.get('JWT_SECRET', 'vkeojrkewmfdeoiwrjkewmfew')


def get_hash(identifier):
    hash_object = hashlib.md5(identifier.encode())
    return hash_object.hexdigest()


def get_token_auth_header():
    ###
    # extracts the bearer token from authorization header
    # raises an AuthError when authorization header is missing or malformed
    ###
    auth = request.headers.get("Authorization", None)
    if auth is None:
        raise AuthError(
            {'code': 'no_autorization_header',
             'description': 'authorization header is missing'},
            401)
    else:
        auth_parts = auth.split(' ')
        if len(auth_parts) != 2:
            raise AuthError(
                {'code': 'invalid_header',
                 'description': 'authentication header malformed. No bearer'},
                401)

        if auth_parts[0].lower() != 'bearer':
            raise AuthError(
                {'code': 'invalid_header',
                 'description': 'authentication header malformed. No bearer'},
                401)
    return auth_parts[1]


def check_permissions(permission, payload):
    ###
    # checks if required permission is granted in payload
    # @INPUTS
    #    permission: string permission (i.e. 'patch:feedback')
    #    payload: decoded jwt payload
    # raises an Auth Error, if no permissions are included in the payload
    # or the requested permission is not in the payload permissions array
    ###
    expire = payload.get('exp', None)
    if expire is None:
        raise AuthError(
            {'code': 'no_expiration_date',
             'description': 'no expiration date in token'},
            400
         )

    if expire < datetime.datetime.utcnow().timestamp():
        raise AuthError(
            {'code': 'token expired',
             'description': 'JWT Token is expired'},
            401
         )

    roles = payload.get('roles', None)
    if roles is None:
        raise AuthError(
            {'code': 'no_roles',
             'description': 'no roles in token'},
            400
        )
    if not isinstance(roles, Iterable):
        raise AuthError(
            {'code': 'roles_no_list',
             'description': 'roles are not a list'},
            400
        )
    permissions = set_permissions_by_role(roles)
    if permission not in permissions:
        raise AuthError(
            {'code': 'permission_not_granted',
             'description':
             'required permission {} is not granted'.format(permission)},
            403
        )
    return True


def set_permissions_by_role(roles):
    permissions = []
    if 'Author' in roles:
        permissions.append('complete:feedback')
        permissions.append('get:publication')
        permissions.append('get:feedback')
        permissions.append('giveokto:publication')
    if 'Curator' in roles:
        permissions.append('get:feedback')
        permissions.append('patch:feedback')
        permissions.append('post:feedback')
        permissions.append('delete:feedback')
        permissions.append('get:publication')
    if 'Admin' in roles:
        permissions.append('get:publications')
        permissions.append('get:publication')
        permissions.append('publish:publication')
        permissions.append('export:publication')
        permissions.append('post:publication')
        permissions.append('delete:publication')
        permissions.append('add:user')
    return permissions


def encode_jwt(payload):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(days=2)
    payload['exp'] = exp_time
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256').decode('utf-8')
    return token


def randomString(stringLength=6):
    return ''.join(
        [random.choice(string.ascii_letters) for n in range(stringLength)]
        )


def decode_jwt(token):
    ###
    # decodes and verifys JWT
    # expects JWT token
    # returns verified payload
    ###
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e:
        raise AuthError(
            {'code': 'jwt_not_decodeable',
             'description':
             'JWT token is not decodeable: {}'.format(e)
             },
            401
        )
    return payload


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = decode_jwt(token)
            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
