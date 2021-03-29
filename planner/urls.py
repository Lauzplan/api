from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from planner.schemas import schema

from graphene_django.views import GraphQLView
from django.core.exceptions import PermissionDenied

from django.contrib.auth import authenticate, login

app_name = 'planner'


class PrivateGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        if (not request.user.is_authenticated):
            user = authenticate(request)
            if user is None:
                raise PermissionDenied()
            else:
                login(request, user)
        return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    path("graphql",
         csrf_exempt(PrivateGraphQLView.as_view(graphiql=False,
                                                schema=schema))),
]
