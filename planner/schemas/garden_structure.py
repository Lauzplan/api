"""
    Graphene schemas for the structure of the garden
"""
import graphene
from graphql.language import ast
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from graphene_gis.converter import gis_converter
from graphene_gis import scalars

from planner.models import Bed, Parcel, Garden
from planner.models import History, HistoryItem
from .history import HistoryItemType
from itertools import tee
from shapely import wkt
from shapely.geometry import LineString, Point, box, MultiLineString

from django.contrib.gis.geos import GEOSGeometry
from shapely.geometry import mapping
from arcgis.geometry import Geometry

from shapely.ops import transform
import pyproj
import requests

wgs84 = pyproj.CRS('EPSG:4326')
utm = pyproj.CRS('EPSG:31370')

project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return list(zip(a, b))


def get_line_vector(line):
    (x1, y1) = line.coords[0]
    (x2, y2) = line.coords[-1]
    return (x2 - x1, y2 - y1)


def cross_product(v, w):
    (vx, vy) = v
    (wx, wy) = w
    return (vx * wx + vy * wy)


def extend_line_to_bbox(line, extent):
    minx, miny, maxx, maxy = extent
    bounding_box = box(minx, miny, maxx, maxy)
    a, b = line.boundary
    if a.x == b.x:  # vertical line
        extended_line = LineString([(a.x, miny), (a.x, maxy)])
    elif a.y == b.y:  # horizonthal line
        extended_line = LineString([(minx, a.y), (maxx, a.y)])
    else:
        # linear equation: y = k*x + m
        k = (b.y - a.y) / (b.x - a.x)
        m = a.y - k * a.x
        y0 = k * minx + m
        y1 = k * maxx + m
        x0 = (miny - m) / k
        x1 = (maxy - m) / k
        points_on_boundary_lines = [
            Point(minx, y0),
            Point(maxx, y1),
            Point(x0, miny),
            Point(x1, maxy)
        ]
        points_sorted_by_distance = sorted(points_on_boundary_lines,
                                           key=bounding_box.distance)

        extended_line = LineString(points_sorted_by_distance[:2])

    return extended_line


def generate_lines(line, polygon, offset, start_offset=0):
    def offset_line(line, polygon, offset):
        new_line = line.parallel_offset(offset)
        return extend_line_to_bbox(new_line, polygon.bounds)

    original_vector = get_line_vector(line)
    if start_offset > 0:
        line = offset_line(line, polygon, start_offset)

    while True:
        new_vector = get_line_vector(line)

        if cross_product(original_vector, new_vector) < 0:
            line = LineString(line.coords[::-1])

        if line.intersects(polygon):
            yield line
            line = offset_line(line, polygon, offset)
        else:
            break


def create_beds(parcel, start_segment, bed_width, bed_spacing):
    geometry = parcel.geometry.transform(31370, clone=True)

    geometry = wkt.loads(geometry.wkt)

    start_segment.transform(31370)
    selected_segment = wkt.loads(start_segment.wkt)

    total_offset = (bed_spacing + bed_width) / 100

    lines = zip(
        generate_lines(selected_segment, geometry, total_offset,
                       bed_spacing / 100),
        generate_lines(selected_segment, geometry, total_offset, total_offset))
    polygons = map(lambda line_pair: MultiLineString(line_pair).convex_hull,
                   lines)
    intersection_polygon = map(lambda polygon: geometry.intersection(polygon),
                               polygons)
    geos_polygons = map(lambda polygon: GEOSGeometry(polygon.wkt, srid=31370),
                        intersection_polygon)
    web_mercator_geos = map(lambda polygon: polygon.transform(4326, True),
                            geos_polygons)

    return web_mercator_geos


class LineStringScalar(scalars.LineStringScalar):
    @classmethod
    def parse_literal(cls, node):
        assert isinstance(node, ast.StringValue)
        return GEOSGeometry(node.value)

    @classmethod
    def parse_value(cls, value):
        return GEOSGeometry(value)


class GardenType(DjangoObjectType):
    """
        The whole cultural area that a gardner has
    """
    class Meta:
        model = Garden

    @classmethod
    def get_queryset(self, queryset, info):
        user = info.context.user
        # TODO: put that in the logic layer
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(users=user)


class SoilType(graphene.ObjectType):
    code = graphene.Int()
    description = graphene.String()
    area = graphene.Float()
    proportion = graphene.Float()


class ParcelType(DjangoObjectType):
    """
        A parcel of a garden
    """
    class Meta:
        model = Parcel

    soil_type = graphene.List(SoilType)
    area = graphene.Int()
    cultivable_area = graphene.Int()

    def resolve_cultivable_area(self, info):
        beds = Bed.objects.filter(parcel=self)
        area = 0
        for b in beds:
            geom = b.geometry.transform(31370, clone=True)
            area += geom.area
        return round(area)

    def resolve_area(self, info):
        return round(self.geometry.transform(31370, clone=True).area)

    def resolve_soil_type(self, info):
        parcel_geometry = transform(project, wkt.loads(self.geometry.wkt))

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
            raise GraphQLError('Could not define the soil type')

        if "error" in response.json().keys():
            raise GraphQLError(response.json())

        soil_type_data = {}
        for data in response.json()["results"]:
            geometry = wkt.loads(Geometry(data["geometry"]).WKT)
            code = data["attributes"]["CODE"]
            soil_type_data[code] = {
                "code": code,
                "description": data["attributes"]["DESCRIPTION"],
                "area": 0
            }
            for p in geometry:
                intersection = p.intersection(parcel_geometry)
                soil_type_data[code]["area"] += intersection.area

        for val in soil_type_data.values():
            val["proportion"] = val["area"] / parcel_geometry.area

        return soil_type_data.values()


class BedType(DjangoObjectType):
    """
        A bed of a parcel
    """
    class Meta:
        model = Bed

    area = graphene.Int()

    def resolve_area(self, info):

        return round(self.geometry.transform(31370, clone=True).area)


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
        parcel = Parcel.objects.create(garden=garden,
                                       name=name,
                                       geometry=geometry)
        return parcel


class UpdateParcel(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        geometry = graphene.String(required=False)

    Output = ParcelType

    def mutate(self, info, id, name=None, geometry=None):
        parcel = Parcel.objects.get(id=id)
        if (name is not None):
            parcel.name = name
        if (geometry is not None):
            parcel.geometry = geometry

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


class SelectOrientation(graphene.Mutation):
    class Arguments:
        parcel_id = graphene.ID(required=True)
        start_segment = graphene.Argument(LineStringScalar, required=True)
        bed_width = graphene.Int(required=True)
        bed_spacing = graphene.Int(required=True)

    beds = graphene.List(BedType)

    def mutate(self, info, parcel_id, start_segment, bed_width, bed_spacing):
        parcel = Parcel.objects.get(id=parcel_id)
        Bed.objects.filter(parcel=parcel).delete()
        beds_geometry = create_beds(parcel, start_segment, bed_width,
                                    bed_spacing)
        beds = map(
            lambda geom: Bed.objects.create(name='name',
                                            garden=parcel.garden,
                                            parcel=parcel,
                                            geometry=geom), beds_geometry)
        bed_list = list(beds)
        return SelectOrientation(beds=bed_list)


class Query(graphene.ObjectType):
    gardens = graphene.List(GardenType)
    garden = graphene.Field(GardenType, id=graphene.ID(required=True))
    parcel = graphene.Field(ParcelType, id=graphene.ID(required=True))

    def resolve_garden(self, info, id):
        user = info.context.user
        return Garden.objects.get(users=user, id=id)

    def resolve_gardens(self, info):
        user = info.context.user
        queryset = Garden.objects.all()
        # TODO: put that in the logic layer
        if user.is_superuser:
            return queryset
        else:
            return queryset.filter(users=user)

    def resolve_parcel(self, info, id):
        parcel = Parcel.objects.get(id=id)
        UserModel = get_user_model()
        if parcel.garden.users.get(pk=UserModel.objects.last().id):
            return parcel
        return None


class Mutation(graphene.ObjectType):
    create_garden = CreateGarden.Field()
    create_parcel = CreateParcel.Field()
    update_garden = UpdateGarden.Field()
    update_parcel = UpdateParcel.Field()
    delete_parcel = DeleteParcel.Field()
    select_orientation = SelectOrientation.Field()