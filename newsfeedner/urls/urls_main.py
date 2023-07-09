from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from newsfeedner.views.views_dupl_search import GetDuplicated, AddDuplicated

from newsfeedner.views.views_auth import GetTokenView
from newsfeedner.views.views_filters import (
    FiltersView,
    FilterViewRelevant,
)
from newsfeedner.views.views_main import (
    EventList,
    # EventApiView,
    EventApiViewRelevant,
    # EventApiViewApproval,
    EventApiViewRelevant_to_xlsx,
    # NewsList,
    NewsApiView,
    NewsApiViewApproval,
)
from newsfeedner.views.views_post_ids import (
    AddToExceptions,
    AddToApproval,
    AddToChecked,
    EditStatusView,
)

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
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", cache_page(60 * 60)(EventList.as_view()), name="main_page"),
    # Добавлено 03.03.2023
    path("api_news/news", csrf_exempt(NewsApiView.as_view())),
    path("api_news/news_approval", csrf_exempt(NewsApiViewApproval.as_view())),
    # path("api/events", csrf_exempt(EventApiViewRelevant.as_view())),
    path("api_news/news_relevant", csrf_exempt(EventApiViewRelevant.as_view())),
    # Конец добавлено
    # data from db table with NLP found data
    path("api_raw/add_to_exceptions", AddToExceptions.as_view(), name="add_to_exceptions"),
    path("api_raw/add_to_checked", AddToChecked.as_view(), name="add_to_checked"),
    # path("api_raw/events", csrf_exempt(EventApiView.as_view())),
    # Добавлено 07.02.2023
    path("api_news/news_relevant_to_xlsx", csrf_exempt(EventApiViewRelevant_to_xlsx.as_view())),
    # Конец добавлено
    path("api_raw/get_region_relations", FiltersView.as_view(slug="get_region_relations")),
    path("api_raw/get_region_countries", FiltersView.as_view(slug="get_region_countries")),
    path(
        "api_raw/get_relation_countries",
        FiltersView.as_view(slug="get_relation_countries"),
    ),
    path("api_raw/get_country_products", FiltersView.as_view(slug="get_country_products")),
    path("api_raw/get_countries", FiltersView.as_view(slug="get_countries")),
    path("api_raw/get_regions", FiltersView.as_view(slug="get_regions")),
    path("api_raw/get_product_branches", FiltersView.as_view(slug="get_product_branches")),
    # data from db table checked by annotator for approving by approver
    path("api_raw/add_to_approved", AddToApproval.as_view(), name="add_to_approved"),
    # path("api_approval/events", csrf_exempt(EventApiViewApproval.as_view())),
    # data from db table checked by annotator and approved by approver
    path(
        "api/get_region_relations",
        FilterViewRelevant.as_view(slug="get_region_relations"),
    ),
    path(
        "api/get_region_countries",
        FilterViewRelevant.as_view(slug="get_region_countries"),
    ),
    path(
        "api/get_relation_countries",
        FilterViewRelevant.as_view(slug="get_relation_countries"),
    ),
    path(
        "api/get_country_products",
        FilterViewRelevant.as_view(slug="get_country_products"),
    ),
    path("api/get_countries", FilterViewRelevant.as_view(slug="get_countries")),
    path("api/get_regions", FilterViewRelevant.as_view(slug="get_regions")),
    path(
        "api/get_product_branches",
        FilterViewRelevant.as_view(slug="get_product_branches"),
    ),
    path("get_token", GetTokenView.as_view(), name="get_token"),
    path("edit_status", EditStatusView.as_view(), name="edit_status"),
    path("duplicated/get", GetDuplicated.as_view(), name="get_duplicated"),
    path("duplicated/add", AddDuplicated.as_view(), name="add_duplicated"),
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
        name="schblackema-redoc",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
