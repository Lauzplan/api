"""
    graphene schemas related to users and authentication managment
"""
import graphene
from graphene_django import DjangoObjectType, DjangoListField

from django.contrib.auth import get_user_model

class UserType(DjangoObjectType):
    """
        A user of the application
    """
    class Meta:
        model = get_user_model()

    is_researcher = graphene.Boolean()

    def resolve_is_researcher(self, _):
        return self.has_perm('research.is_researcher')


class Query(graphene.ObjectType):
    users = DjangoListField(UserType)
    me = graphene.Field(UserType)

    def resolve_me(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    pass
