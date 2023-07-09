from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from newsfeedner.serializers.serializers_auth import (
    LoginSerializer,
)


class GetTokenView(APIView):
    """
    Logs in an existing user.
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    @csrf_exempt
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: openapi.Response("response description", LoginSerializer)},
    )
    def post(self, request):
        """
        Checks if user exists.
        Username and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
