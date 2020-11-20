"""
    graphene schemas related to the planning manamgent
"""
import graphene
from graphene_django import DjangoObjectType
from planner.models import CultivatedArea, ForthcomingOperation, CulturalOperation
from .vegetable import CulturalOperationType

class CultivatedAreaType(DjangoObjectType):
    """
        A bed that is beeing cultivated. That is, one where you add vegetabels on it. 
    """
    class Meta:
        model = CultivatedArea


class ForthcomingOperationType(DjangoObjectType):
    """
        On operation that is planned for a vegetable on an area
    """
    class Meta:
        model = ForthcomingOperation

    cultural_operation = graphene.Field(CulturalOperationType)

    def resolve_cultural_operation(self, _):
        return CulturalOperation.objects.select_subclasses().get(id=self.original_cultural_operation.id)
