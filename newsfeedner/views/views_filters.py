import json
import logging
import sys

import django.db
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from newsfeedner.models import (
    TradeEvent,
    TradeEventRelevant,
)
from newsfeedner.serializers.serializers_main import (
    EventSerializerRead,
    EventRelevantSerializerRead,
)
from newsfeedner.utils.trade_funcs import (
    get_data_from_db_and_transform,
    get_api_region_relations,
    get_api_region_countries,
    get_api_relation_countries,
    get_api_country_products,
    get_all_product_branch_products,
    get_api_product_branches,
    get_api_region_products,
)

from newsfeedner.utils.trade_utils import (
    query_regions_dict as query_regions,
    smtk_product_all,
    relations,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

default_annotation_path = staticfiles_storage.path("newsfeedner/annotation_config.json")
with open(default_annotation_path) as f:
    default_config = json.load(f)
annotation_config = None
if not annotation_config:
    annotation_config = default_config


class FiltersView(APIView):
    """
    get_region_relations
        Возвращает словарик вида {"region": ["relation_1", "relation_2"...]
        Со всеми возможными регионами для каждого региона

    get_region_countries
        Возвращает словарик вида {"region": ["country_1", "country_2"]
        Со всеми возможными странами для каждого региона

    get_relation_countries
        Возвращает словарь типа {отношение_1:
                                {регион_1:
                                    [страна_1, страна_2],
                                регион_2:
                                    [страна_3, страна_4]}
                            отношение_2:
                                {регион_1:
                                    [страна_1, страна_2],
                                регион_2:
                                    [страна_3, страна_4]}}
    get_country_products
        Возвращает словарь {country_1:[itc_code_1, itc_code_2], country_2: [itc_code_1, itc_code_3]}
        Со всеми товарными группами для каждой страны, которые есть в базе.

    get_countries
        Возвращает список (list) всех стран

    get_product_branches
        Возвращает список ("value", "display name") tuples
    """

    serializer_class = EventSerializerRead
    permission_classes = (permissions.IsAuthenticated,)

    # get data with all values from db
    query_dict = get_data_from_db_and_transform(TradeEvent)
    # getting data to populate filters
    region_countries, countries = get_api_region_countries(query_dict)
    regions = list(region_countries.keys())
    region_relations = get_api_region_relations(query_dict)
    region_products = get_api_region_products(query_dict)
    relation_countries = get_api_relation_countries(query_dict)
    country_products = get_api_country_products(query_dict)
    product_branch_products_dict = get_all_product_branch_products(query_dict)
    product_branches = get_api_product_branches(query_dict)
    slug = None

    @csrf_exempt
    @swagger_auto_schema(
        query_serializer=serializer_class,
    )
    def get(self, request):
        # TODO add description to API depending on slug
        """ """
        if self.slug == "get_region_relations":
            return Response(self.region_relations)

        elif self.slug == "get_region_countries":
            return Response(self.region_countries)

        elif self.slug == "get_relation_countries":
            return Response(self.relation_countries)

        elif self.slug == "get_country_products":
            return Response(self.country_products)

        elif self.slug == "get_countries":
            return Response(self.countries)

        elif self.slug == "get_product_branches":
            return Response(self.product_branches)

        elif self.slug == "get_regions":
            return Response(self.regions)
        else:
            return Response(
                "Please check API address",
            )


class FilterViewRelevant(FiltersView):
    serializer_class = EventRelevantSerializerRead
    permission_classes = (permissions.AllowAny,)
    try:
        query_dict = get_data_from_db_and_transform(TradeEventRelevant)
    except django.db.Error:
        query_dict = {}
    # getting data to populate filters
    region_countries, countries = get_api_region_countries(query_dict)
    # print(region_countries)
    regions = list(region_countries.keys())
    region_relations = get_api_region_relations(query_dict)
    region_products = get_api_region_products(query_dict)
    relation_countries = get_api_relation_countries(query_dict)
    country_products = get_api_country_products(query_dict)
    product_branch_products_dict = get_all_product_branch_products(query_dict)
    product_branches = get_api_product_branches(query_dict)
    slug = None
    @csrf_exempt
    @swagger_auto_schema(
        query_serializer=serializer_class,
    )
    def get(self, request):
        return super().get(self.request)


class ConstantsView(APIView):
    permission_classes = (permissions.AllowAny,)
    const_regions = [*query_regions.keys()]
    const_countries_regions = const_regions + sorted(
        set([loc for k, v in query_regions.items() for loc in v])
    )
    const_countries_regions = [
        "Разные " + loc if loc.startswith("Страны") else loc
        for loc in const_countries_regions
    ]
    const_prods = smtk_product_all

    slug = None

    @csrf_exempt
    @swagger_auto_schema()
    def get(self, request):
        if self.slug == "get_const_relations":
            return Response(relations)

        elif self.slug == "get_const_countries":
            return Response(self.const_countries_regions)

        elif self.slug == "get_const_product":
            return Response(self.const_prods)

        else:
            return Response(
                "Please check API address",
            )
