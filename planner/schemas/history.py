"""
    graphene schemas for the history managment
"""
import graphene
from planner.schemas.planning import CultivatedAreaType, ForthcomingOperationType
from .auth import UserType

class HistoryItemType(graphene.Interface):
    """
       Something that has been done in the field. Can be an observation or a task that is done
    """

    id = graphene.ID(required=True)
    concered_area = graphene.Field(CultivatedAreaType)
    executor = graphene.Field(UserType)
    # garden = graphene.Field(GardenType)
    execution_date = graphene.String()

    def resolve_id(self, _):
        return self.id

    def resolve_concered_area(self, _):
        return self.concered_area

    def resolve_executor(self, _):
        return self.executor

    def resolve_garden(self, _):
        return self.history.garden

    def resolve_execution_date(self, _):
        return self.execution_date.isoformat()

    @classmethod
    def resolve_type(cls, instance, info):
        if instance.__class__.__name__ == 'Operation':
            return OperationType
        elif instance.__class__.__name__ == 'Observation':
            return ObservationType

class OperationType(graphene.ObjectType):
    """
        A cultural operation that has been done
    """
    class Meta:
        interfaces = (HistoryItemType, )
    
    original_alert = graphene.Field(ForthcomingOperationType)
    duration = graphene.Int()
    is_deletion = graphene.Boolean()
    name = graphene.String()
    note = graphene.String()

    def resolve_original_alert(self, _):
        return self.original_alert
        
    def resolve_duration(self, _):
        return self.duration

    def resolve_is_deletion(self, _):
        return self.is_deletion    
        
    def resolve_name(self, _):
        return self.name

    def resolve_note(self, _):
        return self.note

class ObservationType(graphene.ObjectType):
    """
        An observation that has been made
    """
    class Meta:
        interfaces = (HistoryItemType, )

    description = graphene.String()

    def resolve_description(self, _):
        return self.description
