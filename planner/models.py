from datetime import datetime, timedelta
from math import inf

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.expressions import F, ExpressionWrapper, Func, Value
from django.db.models.fields import BooleanField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
from shapely import wkb

from django.contrib.gis.geos import Polygon
from django.db.models import Sum

from common.models import BaseSpecies, BaseVariety, BaseOperation
from django.db.models.functions import Cast, Round
from django.contrib.gis.db.models.functions import Area, AsGeoJSON, Transform, GeoFunc
import requests
from shapely import wkt
from arcgis.geometry import Geometry
from shapely.geometry import mapping
from shapely.ops import cascaded_union
from django.db.models.functions import Coalesce


from functools import reduce

NAME_MAX_LENGTH = 200
TYPE_MAX_LENGTH = 100
USER_ID_LENGTH = 128


class User(AbstractUser):
    pass


class WithAreaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(area=Cast(Round(Area('geometry')), models.IntegerField()))


class Garden(models.Model):
    class Meta:
        default_related_name = "gardens"

    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Nom du jardin")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    # Confidentiality fields, if set to true, the garden's data are accessible for research
    details_available_for_research = models.BooleanField(default=True,
                                                         verbose_name="J'accepte que les données de mon jardin soient accessibles pour la recherche universitaire")
    activity_data_available_for_research = models.BooleanField(default=True,
                                                               verbose_name="J'accepte que les données de mes récoltes soient accessibles pour la recherche universitaire")

    def __str__(self):
        return "Garden: " + self.name


class Species(BaseSpecies):
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)


class Variety(BaseVariety):
    pass


class Operation(BaseOperation):
    pass


class PerformedOperation(models.Model):
    class Meta:
        default_related_name = "performed_operations"
        base_manager_name = "objects"

    operation = models.ForeignKey(Operation, null=True, on_delete=models.CASCADE)
    variety = models.ForeignKey(BaseVariety, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    number_of_worker = models.IntegerField(default=1)
    comment = models.CharField(max_length=255, default='')

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().annotate(total_work_time=ExpressionWrapper((F('end_time')-F('start_time'))*F('number_of_worker'), output_field=models.DurationField()))

    objects = Manager()


class Parcel(models.Model):
    class Meta:
        db_constraints = {
            'geometery_one_ring': 'CHECK (ST_NRings(geometry::geometry) = 1)',
            "no_concave_geometry": "CHECK (ST_equals(ST_ConvexHull(ST_Boundary(geometry::geometry)), geometry::geometry))"
        }
        default_related_name = "parcels"
        base_manager_name = "objects"

    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Nom")
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    geometry = models.PolygonField(geography=True)
    orientation_segment = models.IntegerField(default=0)

    class Manager(WithAreaManager):
        def get_queryset(self):
            return super().get_queryset().annotate(cultivable_area=Sum(Cast(Round(Area('beds__geometry')), models.IntegerField())), geom=Cast('geometry', output_field=models.GeometryField()), transformed=Transform('geom', 31370))

    objects = Manager()

    def soil_type(self):
        parcel_geometry = wkt.loads(self.transformed.wkt)
        geometry_map = mapping(parcel_geometry)

        esriPolygon = {
            "spatialReference": {
                "wkid": 31370
            },
            "rings":
            [[list(p) for p in r] for r in geometry_map["coordinates"]]
        }

        response = requests.get(
            f"https://geoservices.wallonie.be/arcgis/rest/services/SOL_SOUS_SOL/CNSW__PRINC_TYPES_SOLS/MapServer/identify?f=json&geometry={esriPolygon}&tolerance=0&mapExtent={parcel_geometry.bounds}&sr=31370&imageDisplay=1,1,1&layers=all&geometryType=esriGeometryPolygon&geometryPrecision=4"
        )

        if not response.ok:
            raise 'Could not define the soil type'

        if "error" in response.json().keys():
            raise response.json()

        soil_type_data = {}

        for data in response.json()["results"]:
            geometry = wkt.loads(Geometry(data["geometry"]).WKT)

            code = data["attributes"]["CODE"]
            soil_type_data[code] = {
                "code": code,
                "description": data["attributes"]["DESCRIPTION"],
                "area": 0
            }
            geometry = cascaded_union(geometry).buffer(0)
            intersection = geometry.intersection(parcel_geometry)
            soil_type_data[code]["area"] += intersection.area

        for val in soil_type_data.values():
            val["proportion"] = val["area"] / parcel_geometry.area

        return soil_type_data.values()

    def __str__(self):
        return self.name


class Bed(models.Model):
    class Meta:
        default_related_name = "beds"
        ordering = ["parcel_id", "index"]
        base_manager_name = "objects"

    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, null=True, verbose_name="Parcelle")
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Nom')
    geometry = models.PolygonField(geography=True)
    index = models.PositiveIntegerField(editable=False)

    class Manager(WithAreaManager):
        def get_queryset(self):
            return super().get_queryset().annotate(_geoJSON=AsGeoJSON('geometry'), total_planted_area=Coalesce(Sum('plantations__area'), 0))

    objects = Manager()


class IsAreaOk(Func):
    function = 'isareaok'
    arity = 0
    output_field = BooleanField()


class Plantation(models.Model):
    variety = models.ForeignKey(BaseVariety, verbose_name='Légume cultivé', on_delete=models.PROTECT)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    area = models.PositiveIntegerField()

    class Meta:
        default_related_name = "plantations"
        constraints = [
            models.CheckConstraint(
                check=models.Q(area__gt=0),
                name="%(app_label)s_%(class)s_greater_than_0",
            ),
        ]


class Invitation(models.Model):
    email = models.EmailField()
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
