"""
    graphene schemas related to the usage of products
"""
from graphene_django import DjangoObjectType
from planner.models import PhytosanitaireUsage, IncomingPhytosanitaire

class PhytosanitaireUsageType(DjangoObjectType):
    class Meta:
        model = PhytosanitaireUsage


class IncomingPhytosanitaireType(DjangoObjectType):
    class Meta:
        model = IncomingPhytosanitaire

