"""
    graphene schemas linked to the vegetables
"""
import graphene
from graphene_django import DjangoObjectType, DjangoListField

from planner.models import Vegetable, CulturalOperation


class CulturalOperationType(graphene.Interface):
    """
        An operation that must be done for a vegatable
    """

    name = graphene.String()
    duration = graphene.Float()
    date = graphene.String()

    def resolve_name(self, _):
        return self.name

    def resolve_duration(self, _):
        return self.duration.total_seconds()

    def resolve_date(self, _):
        return self.get_date().isoformat()

    @classmethod
    def resolve_type(cls, instance, info):
        if instance.__class__.__name__ == 'COWithOffset':
            return COWithOffsetType
        elif instance.__class__.__name__ == 'COWithDate':
            return COWithDateType


class COWithDateType(graphene.ObjectType):
    """
        An operation that should be done at a date
    """
    class Meta:
        interfaces = (CulturalOperationType, )


class COWithOffsetType(graphene.ObjectType):
    """
        An operation that must be done after another one
    """
    class Meta:
        interfaces = (CulturalOperationType, )

    offset_in_days = graphene.Int()
    previous_operation = graphene.Field(CulturalOperationType)

    def resolve_offset_in_days(self, _):
        return self.offset_in_days

    def resolve_previous_operation(self, _):
        return CulturalOperation.objects.select_subclasses().get(id=self.previous_operation.id)

class VegetableType(DjangoObjectType):
    """
        A vegetable that the gardner can plant
    """
    class Meta:
        model = Vegetable

    culturaloperationSet = graphene.List(CulturalOperationType)

    def resolve_culturaloperationSet(self, _):
        return CulturalOperation.objects.select_subclasses()


class Query(graphene.ObjectType):
    vegetables = DjangoListField(VegetableType)
