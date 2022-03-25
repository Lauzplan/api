from django.contrib.auth import authenticate
import json

from urllib import request
import requests as rq
from jose import jwt


def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    jwks = request.urlopen('https://lauzplan.eu.auth0.com/.well-known/jwks.json')
    issuer = 'https://lauzplan.eu.auth0.com/'
    payload = jwt.decode(token, jwks.read(), algorithms=['RS256'], audience='localhost:8080', issuer=issuer)

    return payload
