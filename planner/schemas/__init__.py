"""
    graphene scemas
"""
import graphene
from graphql import GraphQLError

from graphene_django import DjangoListField
from .auth import Query as AuthQuery, Mutation as AuthMutation
from .garden_structure import GardenType, Query as GardenQuery, Mutation as GardenMutation
from .vegetable import COWithDateType, COWithOffsetType
from .history import OperationType, ObservationType

class Mutation(AuthMutation, GardenMutation, graphene.ObjectType):
    pass

class Query(GardenQuery, AuthQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation, types=[COWithDateType, COWithOffsetType, OperationType, ObservationType])
