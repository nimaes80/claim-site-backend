from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core_config import settings


api_patterns = []

urlpatterns = (
    [
        path("api/", include(api_patterns)),
        path("admin/", admin.site.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

schema_view = get_schema_view(
    openapi.Info(
        title=f"{settings.PROJECT_NAME.capitalize()} API",
        default_version="v1",
        description="",
    ),
    permission_classes=(permissions.AllowAny,),
    public=True,
    patterns=urlpatterns,
)

urlpatterns += [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
    ),
]
