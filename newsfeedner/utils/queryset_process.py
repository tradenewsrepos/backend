import re
from collections import defaultdict
from typing import List, Tuple, Dict

import pymorphy2
import razdel

from newsfeedner.utils.trade_utils import loc_dict
from newsfeedner.utils.trade_utils import (
    names_upper_case,
    stoplist,
    countries_and_regions,
    query_regions_dict_reversed,
)
from newsfeedner.utils.trade_utils import query_regions_dict as query_regions

morph = pymorphy2.MorphAnalyzer()


def get_known_locations(locations: List) -> List:
    """
    Функция проверяет есть ли страны локация у нас в константах, и если есть записывает их в список.
    Это позволит убрать названия локация (сел, городов), о которых мы не знаем.
    В unknown записываются неизвестные локации, по которым возможно будет расширить данные.
    """
    known_locations = set()
    unknown = set()
    for loc in locations:
        loc = loc.replace("Разные ", "")
        if loc in countries_and_regions:
            known_locations.add(loc)
        else:
            unknown.add(loc)
    known_locations = sorted(known_locations)
    return known_locations, unknown


def process_queryset_classes(q):
    q.classes = "; ".join(q.classes)
    q.classes = "; ".join(sorted(set(q.classes.split("; "))))


def process_queryset_dates(q):
    dates = [d[:10] for d in q.dates]
    dates = sorted(set(dates))
    q.dates = dates[-1]


def get_article_abstract(
    article_body: str,
    search_countries: List[str],
    region_locations: List[str] = None,
):
    """
    article_body - это title + "\n\n" + text
    search_countries - список стран, каждая страна не обязательно из одного слова (['Турецкая Республика', 'Турция'])
                    + могут быть прилагательные (['Сербия', 'Словакия', 'Турция', 'словацкие'])

    """
    stoplist_middle = [
        "Читайте нас на:",
    ]
    stoplist_end = [
        "Читайте также",
        "Читайте нас в Telegram",
        "Почему так произошло, читайте здесь",
        "Читайте полный текст",
        "Читайте еще",
        "Полный текст статьи читайте",
        "Полный текст интервью",
        "Читайте ранее",
        "Читайте подробнее",
        "Подробнее по этой теме читайте",
        "Подробнее читайте в",
        "Все новости Белоруссии читайте на",
        "Подписывайтесь на видео-новости",
    ]
    # подготовка строк локаций
    search_countries_parts = []
    for sc in search_countries:
        if " " in sc:
            for sc_part in sc.split():
                search_countries_parts.append(sc_part)
        else:
            search_countries_parts.append(sc)
    search_countries = [sc.lower()[:-1] for sc in search_countries_parts]

    # очистка
    for pattern in stoplist_middle:
        article_body = re.sub(pattern, "", article_body, flags=re.I)
    for pattern in stoplist_end:
        article_body = re.sub(f"{pattern}.+", "", article_body, flags=re.I)

    # добавить пробелы, если в изначальном тексте слипшиеся предложения
    article_body = re.sub(r"\.([а-яА-яёЁa-zA-Z])", r". \1", article_body)

    # разделение заголовка и текста новости
    title = article_body
    text = ""
    for split_chars in ["\\n\\n", "\n\n"]:
        if split_chars in article_body:
            splited_text = article_body.split(split_chars)
            if len(splited_text) <= 2:
                title, text = splited_text
            else:
                title, text = splited_text[:2]

    article_body = title
    sents = []

    # только предложения, содержащие указанные локации и регионы
    if search_countries:
        sents = razdel.sentenize(text)
        if region_locations:
            sents = [
                s
                for s in sents
                if any(a.lower() in s.text.lower() for a in region_locations)
                or any(sc in s.text.lower() for sc in search_countries)
            ]
        else:
            sents = [
                s for s in sents if any(sc in s.text.lower() for sc in search_countries)
            ]

        sents = [
            s
            for s in sents
            if len(s.text) > 10
            and (s.text not in title)
            and (title not in s.text)  # без повторения заголовка
            and not any(
                [
                    term in s.text
                    for term in ["sputnik.", "ria.ru", "http", "Rosiya Segodnya"]
                ]
            )
            # посторонний текст в спутнике и риа
        ]
        # Leave only 5 sentences
        sents = sents[:5]

        abstract = " ".join([s.text for s in sents])  # абстракт
        if abstract:
            article_body = title + ". " + abstract  # заголовок + абстракт
    for s in sents:
        # len("\\n\\n") == 4
        s.start += len(title) + 4
        s.stop += len(title) + 4
    sents = [razdel.substring.Substring(0, len(title) + 1, title)] + sents

    return article_body, sents


def remove_location_duplicates(locations: List) -> List:
    to_del = []
    for l_i, l in enumerate(locations):
        if l_i == len(locations) - 1:
            break
        if l in locations[l_i + 1]:
            to_del.append(l_i)
    locations = [loc for l_i, loc in enumerate(locations) if l_i not in to_del]

    to_del = []
    for l_i, l in enumerate(locations):
        if l_i == 0:
            continue
        if l in locations[l_i - 1]:
            to_del.append(l_i)
    locations = [loc for l_i, loc in enumerate(locations) if l_i not in to_del]

    return locations


def normalize_locations(locations: List) -> List:
    """
    Названия стран приводятся к нормальному значению.
    Прилагательные типа "британская", приводятся к нормальному виду и далее заменяются значением из словаря.
    """
    # британско-шведский -> Великобритания, Швеция
    new_countries = []
    for l_i, l in enumerate(locations):
        if l in countries_and_regions:
            continue
        normal_form = morph.parse(l)[0].normal_form
        if normal_form in stoplist:
            locations[l_i] = ""
            continue

        new_form = loc_dict.get(normal_form.lower())
        if new_form:
            new_form = new_form.split(", ")
            new_countries.extend(new_form)
            locations[l_i] = ""

        if normal_form in names_upper_case:
            normal_form = normal_form.upper()
        else:
            normal_form = normal_form.capitalize()

        region = query_regions_dict_reversed.get(normal_form)
        if region:
            locations[l_i] = normal_form
    locations.extend(new_countries)
    locations = [loc for loc in locations if loc]
    locations = set(sorted(locations))
    return locations


def get_regions_from_countries(locations: List) -> Dict:
    """
    Из списка стран и регионов делаем словарь регион - страны.
    В словаре сохраняем только географические регионы.
    Если в списке locations уже есть регион, то оставляем его в виде ключа с пустым списком стран.
    """
    regions = defaultdict(set)
    for loc in locations:
        region = query_regions_dict_reversed.get(loc)
        loc = loc.replace("Разные ", "")
        if loc in query_regions and "Страны" not in loc:
            regions[loc].add(loc)
        if region:
            for reg in region:
                if "Страны" in reg:
                    regions[reg].add(loc)
    regions = {
        r: c for r, c in sorted(regions.items(), key=lambda x: len(x[1]), reverse=True)
    }

    return regions


def process_text_locations(
    location_str: str, region=None, country: str = ""
) -> Tuple[List, Dict]:
    """
    Функция преобразует список стран из базы в список стран из известных.
    Выполняются следующие преобразования:
    - удаляются дубликаты;
    - названия стран приводят к нормальным, прилагательные преобразуются в существительные;
    - список сокращается до списка стран и регионов, названия которых изначально заданы;
    - по известным странам составляем словарь вида {регион_1: [страна_1, страна_2], регион_2: [страна_3, страна_4]}
    - к названиям регионов добавляем "Разные", например "Страны Африки" -> "Разные Страны Африки"
    """
    locations = location_str.split(", ")
    locations = remove_location_duplicates(locations)
    locations = normalize_locations(locations)
    locations, _ = get_known_locations(locations)
    regions = get_regions_from_countries(locations)
    # add "Разные " to region name
    locations = [("Разные " + loc) if "Страны" in loc else loc for loc in locations]

    locations = sorted(set(locations))
    return locations, regions
