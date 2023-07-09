import os
from typing import List

import requests
from django.db import transaction
from django.db.models import QuerySet
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from newsfeedner.models import (
    TradeEventRelevant,
    TradeEventForApproval,
    TradeEvent,
)
from newsfeedner.serializers.serializers_dupl_search import (
    DuplicatedSerializer,
    TextSerializer,
)
from newsfeedner.serializers.serializers_post_ids import (
    DuplicatedIDSerializer, )

from newsfeedner.serializers.serializers_main import (
    EventApprovalSerializerRead,
    EventSerializerWrite,
    EventApprovalSerializerWriteStatus,
)
from newsfeedner.utils.queryset_process import (
    process_queryset_classes,
    process_queryset_dates,
)

DUPLICATES_SERVICE = os.getenv("DUPLICATES_SERVICE")


class AddDuplicated(ListAPIView):
    """ """

    http_method_names = ["post"]

    permission_classes = (permissions.IsAuthenticated, )

    write_serializer_class = DuplicatedSerializer
    read_serializer_class = EventApprovalSerializerRead
    duplicated_ids_serializer = DuplicatedIDSerializer
    write_event_serializer_class = EventSerializerWrite
    write_approval_serializer_class = EventApprovalSerializerWriteStatus

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.write_serializer_class
        elif self.request.method == "GET":
            return self.read_serializer_class
        else:
            return self.serializer_class

    def post_article_ids(self, request, is_many):
        """
        Метод сохраняет значения article_ids в approved_ids при сохранении данных в тадлицу trade_news_relevant
        Return: serializer.data
        """
        if is_many:
            ids = request.data[0].get("article_ids_1")
        else:
            ids = request.data.get("article_ids_1")
        if ids:
            ids = ids.split(",")
        req_data = [{"duplicated_id": v} for v in ids]
        serializer = self.duplicated_ids_serializer(data=req_data, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer

    def status_update(self, pk):
        """
        При отметке новости как дубликата вызывается этот метод для
         изменения статуса новости в таблице вызова.
         Если вызывается из trade_news_for_approval, то необходимо изменить статус только в этой таблице.
         Если объекта с таким id нет в trade_news_for_approval, значит метод вызывается из trade_news_events
         Соответственно возвращаем serializer.
        """
        status_update = {"status": "duplicated"}
        try:
            obj = TradeEventForApproval.objects.get(pk=pk)
            serializer = self.write_approval_serializer_class(
                obj, data=status_update, partial=True)
        except ObjectDoesNotExist:
            obj = TradeEvent.objects.get(pk=pk)
            serializer = self.write_event_serializer_class(obj,
                                                           data=status_update,
                                                           partial=True)
        if serializer.is_valid():
            return serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        is_many = isinstance(request.data, list)
        article_ids_serializer = self.post_article_ids(request, is_many)
        if is_many:
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        with transaction.atomic():
            article_ids_serializer.save()
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            if isinstance(obj, list):
                obj = obj[0]
            status_serializer = self.status_update(obj.id_1)
            status_serializer.save()
        return Response(serializer.data)


class GetDuplicated(ListAPIView):
    """
    Класс выполняет следующее:
    - по заданному тексту осуществляет запрос на внешний сервис
    - возвращает список id 3-х новостей, максимально похожих на заданный текст
    - достает из базы новости из таблиц trade_news_for_approval и trade_new_relevant по этим id
    - возвращает список новостей
    """

    http_method_names = ["post"]
    permission_classes = (permissions.IsAuthenticated, )
    post_serializer_class = TextSerializer
    read_serializer_class = EventApprovalSerializerRead

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.post_serializer_class
        else:
            return self.serializer_class

    def get_similiar_ids(self, text_id, text) -> List:
        result = requests.post(DUPLICATES_SERVICE,
                               json={
                                   "text_id": text_id,
                                   "text": text
                               }).json()
        if not "similarities_ids" in result:
            print("Error: сервис поиска дубликатов не отвечает")
            return result
        return result["similarities_ids"]

    def get_queryset(self, uuids) -> QuerySet:
        """
        По заданным uuid в таблицах trade_news_relevant и trade_news_for_approval
        находим новости этой таблицы
        """
        queryset_relevant = TradeEventRelevant.objects.filter(id__in=uuids)
        queryset_approval = TradeEventForApproval.objects.filter(
            id__in=uuids).exclude(id__in=queryset_relevant.values_list("id"))
        return queryset_relevant, queryset_approval

    def process_queryset(self, queryset):
        queryset_processed = []
        for q in queryset:
            process_queryset_classes(q)
            process_queryset_dates(q)
            queryset_processed.append(q)
        return queryset_processed

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        similiar_uuids = self.get_similiar_ids(**serializer.data)

        queryset_rel, queryset_approval = self.get_queryset(similiar_uuids)
        queryset_rel = self.process_queryset(queryset_rel)
        queryset_approval = self.process_queryset(queryset_approval)
        serializer_rel = self.read_serializer_class(queryset_rel, many=True)
        serializer_approval = self.read_serializer_class(queryset_approval,
                                                         many=True)
        output_data = serializer_rel.data + serializer_approval.data
        return Response(output_data)
