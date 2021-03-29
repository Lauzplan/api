"""
    graphene scemas
"""
import graphene
from graphql import GraphQLError

from .auth import Query as AuthQuery, Mutation as AuthMutation
from .garden_structure import GardenType, Query as GardenQuery, Mutation as GardenMutation


class Mutation(AuthMutation, GardenMutation, graphene.ObjectType):
    pass


class Query(GardenQuery, AuthQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
    )
