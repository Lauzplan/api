import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene import ObjectType, String, Schema


from common.models import BaseSpecies, BaseVariety, BaseOperation
from vegetables_library.models import LibrarySpecies


class SpeciesType(DjangoObjectType):
    class Meta:
        model = BaseSpecies


class VarietyType(DjangoObjectType):
    class Meta:
        model = BaseVariety


class OperationType(DjangoObjectType):
    class Meta:
        model = BaseOperation


class Query(graphene.ObjectType):
    species = DjangoListField(SpeciesType)

    def resolve_species(self, info):
        return BaseSpecies.objects.filter(libraryspecies__isnull=False)


class Mutation(graphene.ObjectType):
    pass
