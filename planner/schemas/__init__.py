"""
    graphene scemas
"""
import graphene
from graphql import GraphQLError

from .auth import Query as AuthQuery, Mutation as AuthMutation
from .garden_structure import Query as GardenQuery, Mutation as GardenMutation
from .vegetables import Query as VegetablesQuery, Mutation as VegetablesMutation


class Mutation(AuthMutation, GardenMutation, VegetablesMutation, graphene.ObjectType):
    pass


class Query(GardenQuery, AuthQuery, VegetablesQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
