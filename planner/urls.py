from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from planner.schemas import schema

from graphene_django.views import GraphQLView
from rest_framework.decorators import api_view
from rest_framework.request import Request

app_name = 'planner'


class RTGraphQLView(GraphQLView):

    def parse_body(self, request):
        if type(request) is Request:
            return request.data
        return super().parse_body(request)


def graphql_token_view():
    view = RTGraphQLView.as_view(schema=schema)
    view = api_view(['GET', 'POST'])(view)
    return view


urlpatterns = [
    path("graphql", graphql_token_view()),
]
