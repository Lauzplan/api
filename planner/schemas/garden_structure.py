"""
    Graphene schemas for the structure of the garden
"""
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_gis.converter import gis_converter
import json

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
        garden = Garden.objects.get(id=id)
        garden.name = name
        garden.save()
        return UpdateGarden(garden)

class CreateGarden(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        postal_code = graphene.String(required=True)
    
    Output = GardenType

    def mutate(self, info, name, postal_code):
        new_garden = Garden.objects.create(name=name, postal_code=postal_code)
        new_garden.users.add(info.context.user)
        return new_garden

class CreateParcel(graphene.Mutation):
    class Arguments:
        garden_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        geometry = graphene.String(required=True)
    
    Output = ParcelType

    def mutate(self, info, garden_id, name, geometry):
        garden = Garden.objects.get(id=garden_id)
        parcel = Parcel.objects.create(garden=garden, name=name, geometry=json.loads(geometry))
        return parcel

class UpdateParcel(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        geometry = graphene.String(required=False)

    Output = ParcelType
    def mutate(self, info, id, name = None, geometry = None):
        parcel = Parcel.objects.get(id=id)
        if(name is not None):
            parcel.name = name
        if(geometry is not None):
            parcel.geometry = json.loads(geometry)
        
        parcel.save()
        return parcel

class DeleteParcel(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    def mutate(self, info, id):
        parcel = Parcel.objects.get(id=id)
        if parcel is not None:
            parcel.delete()
            return DeleteParcel(ok=True)
        
        return DeleteParcel(ok=False)

class Query(graphene.ObjectType):
    gardens = graphene.List(GardenType)
    garden = graphene.Field(GardenType, id=graphene.ID(required=True))

    def resolve_garden (self, info, id):
        user = info.context.user
        queryset = Garden.objects.all()
        return Garden.objects.get(users=user, id=id)

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
    update_parcel = UpdateParcel.Field()
    delete_parcel = DeleteParcel.Field()