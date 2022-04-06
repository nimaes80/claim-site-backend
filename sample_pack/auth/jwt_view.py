# for more information
# see:https://django-rest-framework-simplejwt.readthedocs.io/en/latest/drf_yasg_integration.html

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from utils.utils import gs


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: gs(
                serializer_name="TokenObtainPairResponseSerializer",
                access=serializers.CharField(),
                refresh=serializers.CharField(),
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: gs(
                serializer_name="TokenRefreshResponseSerializer",
                access=serializers.CharField(),
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
