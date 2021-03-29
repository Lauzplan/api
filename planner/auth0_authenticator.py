from django.contrib.auth.backends import BaseBackend
from jwkaas import JWKaas
import requests
from django.contrib.auth import get_user_model

AUTH0_DOMAIN = 'dev-mrhtglpw.eu.auth0.com'
API_AUDIENCE = 'http://localhost:3000'
ALGORITHMS = ["RS256"]

User = get_user_model()

class MyBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request):
        auth = request.headers.get("Authorization", None)
        if not auth:
            print("no auth header")
            return None

        parts = auth.split()

        if parts[0].lower() != "bearer":
            print("no bearer")
            return None
        elif len(parts) == 1:
            print("no token")
            return None
        elif len(parts) > 2:
            print("header to long")
            return None

        token = parts[1]

        my_jwkaas = JWKaas(
            'localhost:8080',
            'https://lauzplan.eu.auth0.com/',
            jwks_url='https://lauzplan.eu.auth0.com/.well-known/jwks.json',
        )
        my_jwkaas.JWK_ALLOWED_ALGORITHMS = ['RS256']

        token_info = my_jwkaas.get_token_info(token)
        print(token_info)

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(id=token_info['sub'])
            user.is_staff = True
            user.is_superuser = True
        except UserModel.DoesNotExist:
            print("user does not exist")
            try:
                r = requests.get('https://lauzplan.eu.auth0.com/userinfo',
                                 headers={'Authorization': auth})
            except:
                return None

            if (not r.ok):
                user = UserModel.objects.create(id=token_info['sub'])
                user.is_staff = True
                user.is_superuser = True
                return user
            user_infos = r.json()
            user = UserModel.objects.create(id=token_info['sub'],
                                            username=user_infos['nickname'],
                                            email=user_infos['email'])
            user.set_unusable_password()

        return user
