from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from newsfeedner.views.views_filters import ConstantsView


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # get constant data to use in manual data correction
    path(
        "get_const_relations",
         ConstantsView.as_view(slug="get_const_relations")
    ),
    path(
        "get_const_countries",
        ConstantsView.as_view(slug="get_const_countries")
    ),
    path(
        "get_const_product",
        ConstantsView.as_view(slug="get_const_product"),
    ),
    # path(
    #     r"^swagger(?P<format>\.json|\.yaml)$",
    #     csrf_exempt(schema_view.without_ui(cache_timeout=0)),
    #     name="schema-json",
    # ),
    path(
        "swagger/",
        csrf_exempt(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        csrf_exempt(schema_view.with_ui("redoc", cache_timeout=0)),
        name="schema-redoc",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
