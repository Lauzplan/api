"""
 Generate the types and resolvers for the graphQL API
"""
import graphene
from graphene_django import DjangoObjectType, DjangoListField, converter, management
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from planner.models import Garden
from planner.models import Vegetable
from planner.models import CulturalOperation
from planner.models import COWithOffset
from planner.models import COWithDate
from planner.models import Parcel
from planner.models import Bed
from planner.models import CultivatedArea
from planner.models import ForthcomingOperation
from planner.models import History
from planner.models import HistoryItem
from planner.models import Observation
from planner.models import Operation
from planner.models import IncomingPhytosanitaire
from planner.models import PhytosanitaireUsage
from planner.models import TestInterface
from planner.models import SubOne
from planner.models import SubTwo










# class A(DjangoObjectType):
#     class Meta:
#         model = TestInterface

#     @classmethod
#     def resolve_type(cls, instance, info):
#         print("----------")
#         if instance.__class__.__name__ == 'SubOne':
#             return B
#         elif instance.__class__.__name__ == 'SubTwo':
#             return C

# class B(DjangoObjectType):
#     class Meta:
#         model = SubOne

# class C(DjangoObjectType):
#     class Meta:
#         model = SubTwo



