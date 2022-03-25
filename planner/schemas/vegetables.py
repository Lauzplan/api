
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene import ObjectType, String, Schema


from common.models import BaseSpecies, BaseVariety, BaseOperation
from vegetables_library.models import LibrarySpecies
from planner.models import Bed, PerformedOperation, Plantation, Variety
from datetime import time, timedelta, datetime
import itertools

from graphene.types import Scalar
from graphql.language import ast


class Duration(Scalar):

    @staticmethod
    def serialize(duration):
        return duration.total_seconds()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.IntValue):
            return timedelta(node.value)

    @staticmethod
    def parse_value(value):
        return timedelta(value)


class SpeciesType(DjangoObjectType):
    class Meta:
        model = BaseSpecies


class VarietyType(DjangoObjectType):
    class Meta:
        model = BaseVariety


class OperationType(DjangoObjectType):
    class Meta:
        model = BaseOperation


class PerformedOperationType(DjangoObjectType):
    class Meta:
        model = PerformedOperation

    total_work_time = Duration()


class PlantationType(DjangoObjectType):
    class Meta:
        model = Plantation


class DeleteHistoryItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        PerformedOperation.objects.get(id=id).delete()
        return DeleteHistoryItem(ok=True)


class EditHistoryItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        variety_id = graphene.ID(required=False)
        date = graphene.Date(required=False)
        start_time = graphene.Time(required=False)
        end_time = graphene.Time(required=False)
        number_of_worker = graphene.Int(required=False)
        comment = graphene.String(required=False)

    Output = PerformedOperationType

    def mutate(self, info, id, variety_id=None, date=None, start_time=None, end_time=None, number_of_worker=None, comment=None):

        operation = PerformedOperation.objects.get(id=id)

        if(variety_id is not None):
            operation.variety_id = variety_id

        if(date is not None):
            operation.date = date

        if(start_time is not None):
            operation.start_time = start_time

        if(end_time is not None):
            operation.end_time = end_time

        if(number_of_worker is not None):
            operation.number_of_worker = number_of_worker

        if(comment is not None):
            operation.comment = comment

        operation.save()
        return operation


def save_datetime(variety_id, start_datetime, end_datetime, number_of_worker=None, comment=None):
    if(start_datetime >= end_datetime):
        return False

    date = start_datetime.date()
    start_time = start_datetime.time()

    if(end_datetime.date() > date):
        end_time = time.max
        opp = PerformedOperation.objects.create(variety_id=variety_id, date=date, start_time=start_time,
                                                end_time=end_time, number_of_worker=number_of_worker, comment=comment)
        if opp is None:
            return False

        new_start_datetime = datetime.combine(date + timedelta(days=1), time.min, tzinfo=start_datetime.tzinfo)
        return save_datetime(variety_id, new_start_datetime, end_datetime, number_of_worker=number_of_worker, comment=comment)
    else:
        opp = PerformedOperation.objects.create(variety_id=variety_id, date=date, start_time=start_time,
                                                end_time=end_datetime.time(), number_of_worker=number_of_worker, comment=comment)
        if opp is None:
            return False

    return True


class WithDateInput(graphene.InputObjectType):
    date = graphene.Date(required=True)
    start_time = graphene.Time(required=True)
    end_time = graphene.Time(required=True)


class WithDatetimeInput(graphene.InputObjectType):
    start_datetime = graphene.DateTime(required=True)
    end_datetime = graphene.DateTime(required=True)


class AddHistoryItemOnVariety(graphene.Mutation):
    class Arguments:
        variety_id = graphene.ID(required=True)
        number_of_worker = graphene.Int(required=False)
        comment = graphene.String(required=False)
        with_date = WithDateInput(required=False)
        with_datetime = WithDatetimeInput(required=False)

    ok = graphene.Boolean()

    def mutate(self, info, variety_id, number_of_worker=None, comment=None, with_date=None, with_datetime=None):

        if(with_date is not None):
            if(with_date.start_time >= with_date.end_time):
                return AddHistoryItemOnVariety(ok=False)

            opp = PerformedOperation.objects.create(variety_id=variety_id, date=with_date.date, start_time=with_date.start_time,
                                                    end_time=with_date.end_time, number_of_worker=number_of_worker, comment=comment)
            if opp is not None:
                return AddHistoryItemOnVariety(ok=True)

        elif(with_datetime is not None):
            ok = save_datetime(variety_id, with_datetime.start_datetime, with_datetime.end_datetime, number_of_worker, comment)
            if(ok):
                return AddHistoryItemOnVariety(ok=True)

        return AddHistoryItemOnVariety(ok=False)


class AddPlantation(graphene.Mutation):
    class Arguments:
        area = graphene.Int(required=True)
        start_bed_id = graphene.ID(required=True)
        variety_id = graphene.ID(required=True)

    Output = graphene.List(PlantationType)

    def mutate(self, info, area, start_bed_id, variety_id):
        def acc_function(acc, bed):
            free_area = bed.area - bed.total_planted_area
            if(free_area <= acc[0]):
                return (acc[0]-free_area, bed, free_area)
            return (0, bed, acc[0])
        start_bed = Bed.objects.get(id=start_bed_id)
        beds = start_bed.parcel.beds.filter(index__gte=start_bed.index)

        all_plantations = itertools.accumulate(beds, acc_function, initial=(area, None, 0))
        next(all_plantations)
        plantations_tuple = itertools.takewhile(lambda p: p[2] >= 0, all_plantations)
        plantations = [Plantation(variety_id=variety_id, bed=p[1], area=p[2]) for p in plantations_tuple if p[2] > 0]
        pks = [p.pk for p in Plantation.objects.bulk_create(plantations)]

        return Plantation.objects.filter(pk__in=pks)


class Query(graphene.ObjectType):
    species = DjangoListField(SpeciesType)
    varieties = DjangoListField(VarietyType, species_id=graphene.ID(required=True))
    performed_operations = DjangoListField(PerformedOperationType)
    plantations = DjangoListField(PlantationType)

    def resolve_species(self, info):
        return BaseSpecies.objects.filter(libraryspecies__isnull=False)

    def resolve_varieties(self, info, species_id):
        return BaseSpecies.objects.get(id=species_id).basevariety_set


class Mutation(graphene.ObjectType):
    add_history_item_on_Variety = AddHistoryItemOnVariety.Field()
    edit_history_item = EditHistoryItem.Field()
    delete_history_item = DeleteHistoryItem.Field()
    add_plantation = AddPlantation.Field()
