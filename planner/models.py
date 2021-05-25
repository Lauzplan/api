from datetime import timedelta
from math import inf

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
from shapely import wkb

from django.contrib.gis.geos import Polygon

from common.models import BaseSpecies, BaseVariety, BaseOperation
from django.db.models.functions import Cast
from django.contrib.gis.db.models.functions import Area, AsGeoJSON, Transform
import requests
from shapely import wkt
from arcgis.geometry import Geometry
from shapely.geometry import mapping
from shapely.ops import cascaded_union


from functools import reduce

NAME_MAX_LENGTH = 200
TYPE_MAX_LENGTH = 100
USER_ID_LENGTH = 128


class User(AbstractUser):
    pass


class WithAreaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(_area=Area('geometry'))


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

    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    @property
    def duration(self):
        return self.end_time - self.start_time


class Vegetable(models.Model):
    name = models.CharField(max_length=100, verbose_name='Espèce')
    variety = models.CharField(max_length=100, blank=True, default="", verbose_name="Variété")
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    # Field filled with primary key of vegetable from the library when exporting
    extern_id = models.IntegerField(null=True)

    def __str__(self):
        if self.variety:
            return self.name + " - " + self.variety
        else:
            return self.name

    class Meta:
        unique_together = ('name', 'variety', 'garden')


class Parcel(models.Model):
    class Meta:
        db_constraints = {
            'geometery_one_ring': 'CHECK (ST_NRings(geometry::geometry) = 1)',
            "no_concave_geometry": "CHECK (ST_equals(ST_ConvexHull(ST_Boundary(geometry::geometry)), geometry::geometry))"
        }
        default_related_name = "parcels"

    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name="Nom")
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    geometry = models.PolygonField(geography=True)
    orientation_segment = models.IntegerField(default=0)

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().annotate(_area=Area('geometry'), geom=Cast('geometry', output_field=models.GeometryField()), transformed=Transform('geom', 31370))

    objects = Manager()

    @property
    def area(self):
        return round(self._area.sq_m)

    def cultivable_area(self):
        return reduce(lambda acc, bed: acc + bed.area, self.beds.all(), 0)

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

    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, null=True, verbose_name="Parcelle")
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Nom')
    geometry = models.PolygonField(geography=True)

    class Manager(models.Manager):

        def get_queryset(self):
            return super().get_queryset().annotate(_area=Area('geometry'), _geoJSON=AsGeoJSON('geometry'))

    objects = Manager()

    @property
    def area(self):
        print("area", self._area)
        return round(self._area.sq_m)

    def __str__(self):
        return self.name


class CultivatedArea(models.Model):
    vegetable = models.ForeignKey(Vegetable, blank=True, null=True, on_delete=models.SET_NULL,
                                  verbose_name='Légume cultivé')
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    surface = models.ForeignKey(Bed, on_delete=models.CASCADE, verbose_name="Planche")
    label = models.TextField(verbose_name="Label de la culture")
    # Following attributes are related to the harvest of this cultivated area
    is_active = models.BooleanField(default=True)  # Set to false when we harvest this cropping
    harvest_date = models.DateField(null=True, verbose_name="Date de récolte")
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    kg_produced = models.IntegerField(blank=True, default=0, verbose_name="Quantité récoltée (kg)")
    total_selling_price = models.IntegerField(blank=True, default=0, verbose_name="Prix de vente total (€)")

    def __str__(self):
        return self.label + ' - ' + self.surface.name


class History(models.Model):
    garden = models.OneToOneField(Garden, on_delete=models.CASCADE)


class HistoryItem(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE)
    execution_date = models.DateField(verbose_name="Date d'exécution")
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    area_concerned = models.ForeignKey(CultivatedArea, on_delete=models.SET_NULL, blank=True, null=True,
                                       verbose_name="Culture concernée")


class Observation(HistoryItem):
    class Meta:
        default_related_name = "observations"
    description = models.TextField(verbose_name="Description")


KILO = 'kg'
GRAM = 'g'
LITER = 'l'

UNITY_CHOICES = (
    (KILO, KILO),
    (GRAM, GRAM),
    (LITER, LITER),
)
