from collections import defaultdict, OrderedDict
from typing import List, AnyStr, Tuple, Dict, Set

import django.db
import psycopg2

import pymorphy2

from .trade_utils import (
    query_regions_dict_reversed,
    loc_dict,
    smtk_branches,
    countries_and_regions,
)

morph = pymorphy2.MorphAnalyzer()
loc_dict.update({v.lower(): v for v in loc_dict.values()})


def process_db_itc_codes(itc_code_str: str) -> Dict[AnyStr, Set[AnyStr]]:
    itc_codes = itc_code_str.split(";; ")

    # getting itc branch
    smtkbranch_smtk = defaultdict(set)
    for itc in set(itc_codes):
        if not itc[0].isdigit():
            continue
        smtk_branch_id = int(itc[0])
        smtk_branch = smtk_branches[smtk_branch_id]
        itc = itc.strip()
        if smtk_branch in smtkbranch_smtk:
            smtkbranch_smtk[smtk_branch].add(itc)
        else:
            smtkbranch_smtk[smtk_branch] = {itc}
    return smtkbranch_smtk


def process_db_locations(location_str: str) -> Set[AnyStr]:
    """
    Функция нормализует названия стран или прилагательных, относящихся к стране.
    Например, белорусская -> белорусский -> Белоруссия
    """
    locations = sorted(location_str.split(", "))
    locations = set(locations)
    return locations


def add_regions_to_query(locations: Set[AnyStr]) -> Dict[AnyStr, Set[AnyStr]]:
    """
    Возвращает словарь вида {
                           регион_1: {страна_1, страна_2},
                            регион_2: {страна_3, страна_4}
                            }
    """
    regions = defaultdict(set)
    for loc in locations:
        region = query_regions_dict_reversed.get(loc)
        if not region:
            continue
        for reg in region:
            if not reg.startswith("Страны"):
                continue
            if reg in regions:
                regions[reg].add(loc)
            else:
                regions[reg] = {loc}
    return regions


def process_db_classes(relations: List[AnyStr]) -> Set:
    """
    Функция преобразует список отношений из базы в список отношений
    """
    relations = sorted(relations)
    relations = set(relations)
    return relations


def get_data_from_db_and_transform(model) -> Dict:
    """
    Функция берет из базы столбцы "classes", "Locations", "itc_codes" (отношения, локации, продукты).
    Преобразует строку локаций в названия стран, отношения список известных отношений и известные продукты,
     по странам определяем регионы.
    Как результат - оставляем только те записи, значения в которых нам известны.

    return Dict
    """
    # initializing dicts that we will return
    all_values_dict = {}
    try:
        query_values = model.objects.values_list("classes", "locations", "itc_codes")
        for rel, loc, prod in query_values:
            if not rel or not loc or not prod:
                continue
            locations: Set = process_db_locations(loc)
            relations: Set = process_db_classes(rel)
            regions: Dict = add_regions_to_query(locations)
            # getting dict smtk branch - smtk group
            itc_codes: Dict = process_db_itc_codes(prod)
            if not itc_codes or not regions or not relations:
                continue
            # make temp dict with values for current row
            # with dependent keys - relation - region - country - smtk_branch - smtk_group
            temp_dict = {}
            temp_dict_regions = {}
            for rel in relations:
                for region, countries in regions.items():
                    temp_dict_regions[region] = {}
                    for country in countries:
                        temp_dict_regions[region][country] = itc_codes
                temp_dict[rel] = temp_dict_regions

            for relation, region_dict in temp_dict.items():
                if relation not in all_values_dict:
                    all_values_dict[relation] = {}
                for region, country_dict in region_dict.items():
                    if region not in all_values_dict[relation]:
                        all_values_dict[relation][region] = {}
                    for country, smtk_branch_dict in country_dict.items():
                        if country not in all_values_dict[relation][region]:
                            all_values_dict[relation][region][country] = {}
                        for smtk_branch, smtk_codes in smtk_branch_dict.items():

                            if (
                                smtk_branch
                                not in all_values_dict[relation][region][country]
                            ):
                                all_values_dict[relation][region][country][
                                    smtk_branch
                                ] = set()
                            all_values_dict[relation][region][country][
                                smtk_branch
                            ].update(smtk_codes)

    except (django.db.ProgrammingError, psycopg2.ProgrammingError):
        return all_values_dict

    # # check result
    for relation, region_dict in all_values_dict.items():
        for region, country_dict in region_dict.items():
            for country, smtk_branch_dict in country_dict.items():
                for smtk_branch, smtk_codes in smtk_branch_dict.items():
                    if len(smtk_codes) >= 13:
                        raise Exception(
                            "Too much values from database."
                            " Check if data correct in database."
                        )
    return all_values_dict


def get_api_region_relations(query: Dict) -> Dict[AnyStr, List[AnyStr]]:
    """
    Функция принимает обработанные данные из базы: словарь словарей.
    Преобразуем в словарь.
    return {
            region_1: [relation_1, relation_2],
            region_2: [relation_2, relation_3]
            }
    """

    region_relations = defaultdict(set)
    for relation, regions_dict in query.items():
        for region in regions_dict.keys():
            if region not in region_relations:
                region_relations[region] = set()
            region_relations[region].add(relation)

    region_relations = {k: sorted(v) for k, v in region_relations.items()}

    return region_relations


def sort_api_region_countries(
    region_countries: Dict, countries: Set
) -> Tuple[Dict, List]:
    region_countries = {k: sorted(v) for k, v in region_countries.items()}
    countries = sorted(countries)
    return region_countries, countries


def get_api_region_countries(
    query: Dict,
) -> Tuple[Dict[AnyStr, List[AnyStr]], List[AnyStr]]:
    """
    Возвращает словарь {
                        регион_1: {страна_1, страна_2}
                        регион_2: {страна_3, страна_4}
                        }
            и список стран
    В словаре перечислены все регионы, страны которых представлены в базе
    """
    region_countries = defaultdict()
    db_countries = set()
    for relation, regions_dict in query.items():
        for region, countries_dict in regions_dict.items():
            countries = set(countries_dict.keys())
            if region not in region_countries:
                region_countries[region] = set()
            region_countries[region].update(countries)

            db_countries.update(countries)

    region_countries, countries = sort_api_region_countries(
        region_countries, db_countries
    )

    return region_countries, countries


def get_api_relation_countries(
    query: Dict,
) -> Dict[AnyStr, List[AnyStr]]:
    """
    Возвращает словрь вида {отношение_1:
                                {
                                регион_1:
                                    [страна_1, страна_2],
                                регион_2:
                                    [страна_3, страна_4]
                                }
                            отношение_2:
                                {
                                регион_1:
                                    [страна_1, страна_2],
                                регион_2:
                                    [страна_3, страна_4]
                                }
                            }
    """
    relation_countries = defaultdict()
    for relation, regions_dict in sorted(query.items()):
        relation_countries[relation] = {}

        for region, country_dict in sorted(regions_dict.items()):
            countries = country_dict.keys()
            relation_countries[relation][region] = countries

    # sort regions and countries
    for relation, region_dict in relation_countries.items():
        sorted_region_dict = sorted(region_dict.items())
        relation_countries[relation] = OrderedDict(sorted_region_dict)

        for region, countries in sorted_region_dict:
            relation_countries[relation][region] = sorted(countries)
    return relation_countries


def add_all_types_to_country_products(country_products: Dict) -> Dict:
    """
    Возвращает словарь с новым ключом "Все типы", значения в котором собраныы из всех прочих ключей словаря
    Для каждой страны добавляет ключ "Все товарные разделы" со значениями всех товарных групп
    """
    all_country_products = {}
    for relation, regions_dict in country_products.items():
        for country, prod_dict in regions_dict.items():
            if country not in all_country_products:
                all_country_products[country] = {}
            if "Все товарные разделы" not in all_country_products[country]:
                all_country_products[country]["Все товарные разделы"] = set()
            for prod_branch, products in prod_dict.items():
                if prod_branch != "Все товарные разделы":
                    if len(products) >= 13:
                        raise Exception(
                            "Too much values from database."
                            " Check if data correct in database."
                        )
                if prod_branch not in all_country_products[country]:
                    all_country_products[country][prod_branch] = set()
                all_country_products[country][prod_branch].update(products)

                all_country_products[country]["Все товарные разделы"].update(products)

    return all_country_products


def sort_country_products(relation_country_products: dict) -> Dict:
    """
    Функция возвращает отсортированный словарь словарей
    """
    for relation, country_dict in relation_country_products.items():
        sorted_country_dict = sorted(country_dict.items())
        relation_country_products[relation] = OrderedDict(sorted_country_dict)

        for country, prod_branch_dict in sorted_country_dict:
            sorted_prod_branch_dict: List[Tuple] = sorted(prod_branch_dict.items())
            relation_country_products[relation][country] = OrderedDict(
                sorted_prod_branch_dict
            )
            for prod_branch, products in sorted_prod_branch_dict:
                sorted_products = sorted(products)
                relation_country_products[relation][country][
                    prod_branch
                ] = sorted_products
    return relation_country_products


def get_api_country_products(query: Dict) -> Dict:
    """
    Возвращает словарь {relation_1:
                            {
                            country_1:
                                {
                                    itc_branch_1:
                                        [itc_prod_1, itc_prod_2],
                                   itc_branch_2:
                                        [itc_prod_3, itc_prod_4],
                                }

                            country_3:
                                [itc_branch_1, itc_branch_3]}
                            }
                        relation_2:
                            {
                            country_1:
                                [itc_branch_1, itc_branch_2],
                            country_2:
                                [itc_branch_1, itc_branch_3]}
                            }
                        }
    """
    relation_country_products = OrderedDict()
    for relation, regions_dict in sorted(query.items()):
        relation_country_products[relation] = {}

        for region, country_dict in regions_dict.items():

            for country, prod_branch_dict in country_dict.items():

                if country not in relation_country_products[relation]:
                    relation_country_products[relation][country] = {}

                if "Все страны" not in relation_country_products[relation]:
                    relation_country_products[relation]["Все страны"] = {}

                if (
                    "Все товарные разделы"
                    not in relation_country_products[relation][country]
                ):
                    relation_country_products[relation][country][
                        "Все товарные разделы"
                    ] = set()

                if (
                    "Все товарные разделы"
                    not in relation_country_products[relation]["Все страны"]
                ):
                    relation_country_products[relation]["Все страны"][
                        "Все товарные разделы"
                    ] = set()

                for branch, products in prod_branch_dict.items():
                    products -= {branch}
                    if not products:
                        continue
                    if len(products) >= 13:
                        raise Exception(
                            "Too much values from database."
                            " Check if data correct in database."
                        )

                    if branch not in relation_country_products[relation][country]:
                        relation_country_products[relation][country][branch] = set()
                    relation_country_products[relation][country][branch].update(
                        products
                    )

                    if branch not in relation_country_products[relation]["Все страны"]:
                        relation_country_products[relation]["Все страны"][
                            branch
                        ] = set()
                    relation_country_products[relation]["Все страны"][branch].update(
                        products
                    )

                    relation_country_products[relation][country][
                        "Все товарные разделы"
                    ].update(products)
                    relation_country_products[relation]["Все страны"][
                        "Все товарные разделы"
                    ].update(products)
    # combine all relations and product branches
    relation_country_products["Все типы"] = add_all_types_to_country_products(
        relation_country_products
    )

    # sort all values
    relation_country_products = sort_country_products(relation_country_products)

    return relation_country_products


def sort_region_products(region_products: Dict) -> Dict:
    """
    Функция возвращает отсортированный словарь словарей
    """
    for region, prod_branch_dict in sorted(region_products.items()):
        sorted_prod_branch = sorted(prod_branch_dict.items())
        region_products[region] = OrderedDict(sorted_prod_branch)

        for prod_branch, products in sorted_prod_branch:
            if prod_branch != "Все товарные разделы":
                if len(products) >= 13:
                    raise Exception(
                        "Too much values from database."
                        " Check if data correct in database."
                    )
            region_products[region][prod_branch] = sorted(products)
    return region_products


def get_api_region_products(query: Dict) -> Dict:
    """
    Возвращает товары, если выбраны все типы отношений и все страны.
    Словарь вида
                            {регион_1:
                                {
                                товарный_раздел_1:
                                    [товарная_группа_1, товарная_группа_2],
                                товарный_раздел_2:
                                    [товарная_группа_3, товарная_группа_4]
                                }
                            регион_2:
                                {
                                товарный_раздел_1:
                                    [товарная_группа_1, товарная_группа_2],
                                товарный_раздел_3:
                                    [товарная_группа_5, товарная_группа_6]
                                }
                            }
    """
    region_products = {}
    for _, regions_dict in query.items():

        for region, country_dict in regions_dict.items():
            if region not in region_products:
                region_products[region] = {}
            if "Все товарные разделы" not in region_products[region]:
                region_products[region]["Все товарные разделы"] = set()
            for _, prod_branch_dict in country_dict.items():

                for branch, products in prod_branch_dict.items():
                    products -= {branch}
                    if not products:
                        continue
                    if len(products) >= 13:
                        raise Exception(
                            "Too much values from database."
                            " Check if data correct in database."
                        )

                    if branch not in region_products[region]:
                        region_products[region][branch] = set()

                    region_products[region][branch].update(products)
                    region_products[region]["Все товарные разделы"].update(products)

    region_products = sort_region_products(region_products)

    return region_products


def get_api_product_branches(query: Dict) -> List[AnyStr]:
    """
    Возвращает список товарных разделов {prod_branch_1, prod_branch_2...}
    """
    product_branches = set()
    for relation, regions_dict in query.items():
        for region, country_dict in regions_dict.items():
            for country, prod_branch_dict in country_dict.items():
                prod_branches = set(prod_branch_dict.keys())
                product_branches.update(prod_branches)
    product_branches = sorted(product_branches)
    return product_branches


def get_api_products(query: Dict) -> List[AnyStr]:
    """
    Возвращает список товарных групп {prod_1, prod_2...}
    """
    all_products = set()
    for relation, regions_dict in query.items():
        for region, country_dict in regions_dict.items():
            for country, prod_branch_dict in country_dict.items():
                for product_branch, products in prod_branch_dict.items():
                    all_products.update(products)
    all_products = sorted(all_products)
    return all_products


def get_all_product_branch_products(query: Dict) -> Dict[AnyStr, Set[AnyStr]]:
    """
    Возвращает словарь вида {
                                product_branch_1:[product_1, product_2],
                                product_branch_2:[product_3, product_4]
                                }
    """
    product_branch_products = {}
    for _, regions_dict in query.items():
        for _, country_dict in regions_dict.items():
            for _, prod_branch_dict in country_dict.items():
                for branch, products in prod_branch_dict.items():
                    products -= {branch}
                    if not products:
                        continue
                    if branch not in product_branch_products:
                        product_branch_products[branch] = set()
                    product_branch_products[branch].update(products)

    products_sorted_values = {k: sorted(v) for k, v in product_branch_products.items()}
    product_branch_products = OrderedDict(sorted(products_sorted_values.items()))
    return product_branch_products
