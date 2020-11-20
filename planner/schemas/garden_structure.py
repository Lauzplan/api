"""
    Graphene schemas for the structure of the garden
"""
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphql_jwt.decorators import login_required

from planner.models import Bed, Parcel, Garden
from planner.models import History, HistoryItem
from .history import HistoryItemType


class GardenType(DjangoObjectType):
    """
        The whole cultural area that a gardner has
    """
    class Meta:
        model = Garden

    history = graphene.List(HistoryItemType)

    def resolve_history(self, info):
        history = History.objects.get(garden=self)
        return HistoryItem.objects.select_subclasses().filter(history=history)

    @classmethod
    def get_queryset(self, queryset, info):
        user = info.context.user
        # TODO: put that in the logic layer
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(users=user) 

class ParcelType(DjangoObjectType):
    """
        A parcel of a garden
    """
    class Meta:
        model = Parcel

class BedType(DjangoObjectType):
    """
        A bed of a parcel
    """
    class Meta:
        model = Bed

class UpdateGarden(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
    
    garden = graphene.Field(GardenType)

    def mutate(self, info, id, name):
        print("muuuutaaaationnnn")
        print(name)
        garden = Garden.objects.get(id=id)
        garden.name = name
        garden.save()
        return UpdateGarden(garden)

class CreateGarden(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        postal_code = graphene.String(required=True)
    
    garden = graphene.Field(GardenType)

    def mutate(self, info, name, postal_code):
        new_garden = Garden.objects.create(name=name, postal_code=postal_code)
        new_garden.users.add(info.context.user)
        return CreateGarden(garden=new_garden)

class CreateParcel(graphene.Mutation):
    class Arguments:
        garden_id = graphene.ID(required=True)
        name = graphene.String(required=True)
    
    parcel = graphene.Field(ParcelType)

    def mutate(self, info, garden_id, name):
        garden = Garden.objects.get(id=garden_id)
        parcel = Parcel.objects.create(garden=garden, name=name)
        return CreateParcel(parcel=parcel)

class Query(graphene.ObjectType):
    gardens = graphene.List(GardenType)

    def resolve_gardens(self, info):
        user = info.context.user
        queryset = Garden.objects.all()
        # TODO: put that in the logic layer
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(users=user) 

class Mutation(graphene.ObjectType):
    create_garden = CreateGarden.Field()
    create_parcel = CreateParcel.Field()
    update_garden = UpdateGarden.Field()