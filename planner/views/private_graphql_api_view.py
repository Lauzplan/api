from graphene_django.views import GraphQLView
from django.core.exceptions import PermissionDenied
from jwkaas import JWKaas
import requests
from django.contrib.auth import get_user_model


AUTH0_DOMAIN = 'dev-mrhtglpw.eu.auth0.com'
API_AUDIENCE = 'http://localhost:3000'
ALGORITHMS = ["RS256"]

class PrivateGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):

        auth = request.headers.get("Authorization", None)
        if not auth:
            raise PermissionDenied({"code": "authorization_header_missing",
                            "description":
                                "Authorization header is expected"}, 401)

        parts = auth.split()

        if parts[0].lower() != "bearer":
            raise PermissionDenied({"code": "invalid_header",
                            "description":
                                "Authorization header must start with"
                                " Bearer"}, 401)
        elif len(parts) == 1:
            raise PermissionDenied({"code": "invalid_header",
                            "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise PermissionDenied({"code": "invalid_header",
                            "description":
                                "Authorization header must be"
                                " Bearer token"}, 401)



        token = parts[1]

        my_jwkaas = JWKaas('localhost:8080', 
                'https://lauzplan.eu.auth0.com/',
                jwks_url='https://lauzplan.eu.auth0.com/.well-known/jwks.json',
                )
        my_jwkaas.JWK_ALLOWED_ALGORITHMS = ['RS256']

        token_info = my_jwkaas.get_token_info(token)
        print(token_info)

        r = requests.get('https://lauzplan.eu.auth0.com/userinfo', headers={'Authorization': auth})

        user_infos = r.json()

        request.user = get_user_model().objects.get(username=user_infos['nickname'])

        if token_info is not None:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied({"code": "token_not_valid",
                                "description":
                                    "The provided token is not valid"}, 401) 