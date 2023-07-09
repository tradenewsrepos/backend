from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from newsfeedner.permissions import ApproverPermissions
from newsfeedner.serializers.serializers_post_ids import (
    AddToExceptionsSerializer,
    ApprovedIDSerializer,
    CheckedIDSerializer,
    EditStatusSerializer,
    EditStatusSerializerDelete,
)
from newsfeedner.serializers.serializers_main import (
    EventSerializerWrite,
    EventApprovalSerializerWriteStatus,
)
from newsfeedner.models import (
    TradeEditStatus,
    TradeEvent,
    TradeEventForApproval,
)
from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist


class AddToExceptions(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddToExceptionsSerializer
    write_event_serializer_class = EventSerializerWrite
    write_approval_serializer_class = EventApprovalSerializerWriteStatus

    def status_update(self, article_ids):
        """
        При отметке новости как нерелевантной вызывается этот метод для
        изменения статуса новости в таблице вызова.
        Если вызывается из trade_news_for_approval, то необходимо изменить статус только в этой таблице.
        Если объекта с таким id нет в trade_news_for_approval, то метод вызывается из trade_news_events
        Соответственно возвращаем serializer.
        Объект достается из базы через равенство списку из article_id, которые для каждой записи является уникальным.
        """
        status_update = {"status": "excluded"}
        try:
            obj = TradeEventForApproval.objects.get(article_ids=article_ids)
            serializer = self.write_approval_serializer_class(
                obj, data=status_update, partial=True
            )
        except ObjectDoesNotExist:
            obj = TradeEvent.objects.get(article_ids=article_ids)
            serializer = self.write_event_serializer_class(
                obj, data=status_update, partial=True
            )
        if serializer.is_valid():
            return serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @swagger_auto_schema(
        request_body=AddToExceptionsSerializer,
        responses={
            200: openapi.Response("response description", AddToExceptionsSerializer)
        },
    )
    def post(self, request):
        """
        Добавляет article_id новостей в ExcludedIDs
        и обновляет статусы в таблице, из которой новость исключается
        """
        approved_ids = request.data.get("excluded_id")
        if approved_ids:
            approved_ids = approved_ids.split(",")
        req_data = [{"excluded_id": v} for v in approved_ids]
        serializer = self.serializer_class(data=req_data, many=True)
        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            obj = [o.excluded_id for o in obj]
            status_serializer = self.status_update(obj)
            status_serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToApproval(APIView):
    permission_classes = (permissions.IsAuthenticated, ApproverPermissions)
    serializer_class = ApprovedIDSerializer

    @csrf_exempt
    @swagger_auto_schema(
        request_body=serializer_class,
        responses={200: openapi.Response("response description", serializer_class)},
    )
    def post(self, request):
        """
        Add id to ApprovedIDs table. Ids of texts checked by annotation approver
        """
        approved_ids = request.data.get("approved_id")
        if approved_ids:
            approved_ids = approved_ids.split(",")
        req_data = [{"approved_id": v} for v in approved_ids]

        serializer = self.serializer_class(data=req_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToChecked(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CheckedIDSerializer

    @csrf_exempt
    @swagger_auto_schema(
        request_body=serializer_class,
        responses={200: openapi.Response("response description", serializer_class)},
    )
    def post(self, request):
        """
        Add id to CheckedIDs table. Ids of texts checked by annotator
        """
        checked_ids = request.data.get("checked_id")
        if checked_ids:
            checked_ids = checked_ids.split(",")
        req_data = [{"checked_id": v} for v in checked_ids]
        serializer = self.serializer_class(data=req_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class EditStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = EditStatusSerializer
    delete_serializer_class = EditStatusSerializerDelete

    def get_serializer_class(self):
        if self.request.method in ["POST", "GET"]:
            return self.serializer_class
        elif self.request.method == "DELETE":
            return self.delete_serializer_class

    # def get_object(self, pk):
    #     try:
    #         return TradeEditStatus.objects.get(pk=pk)
    #     except TradeEditStatus.DoesNotExist:
    #         raise Http404

    def get(self, request):
        queryset = TradeEditStatus.objects.all()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)

    @csrf_exempt
    @swagger_auto_schema(
        request_body=serializer_class,
        responses={200: openapi.Response("response description", serializer_class)},
    )
    def post(self, request):
        """
        Add article_id and user name to Edit Status table
        """
        data = request.data
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @csrf_exempt
    @swagger_auto_schema(
        request_body=delete_serializer_class,
        responses={
            "204":
            "Данные не возвращаются."
            },
        name="Not return data")


    def delete(self, request):
        key = request.data.get("id")
        if key:
            try:
                row = TradeEditStatus.objects.filter(id=key)
                row.delete()
            except TradeEditStatus.DoesNotExist:
                raise Http404
        return Response(status=status.HTTP_204_NO_CONTENT)
