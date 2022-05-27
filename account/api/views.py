from datetime import timedelta

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.api.serializers import (
    AdminTokenObtainPairSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
)
from account.models import SystemSetting
from utils.permissions import IsAdmin
from utils.utils import gs
from rest_framework.response import Response


class DecoratedTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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


class AdminDecoratedTokenObtainPairView(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: gs(
                serializer_name="AdminTokenObtainPairResponseSerializer",
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


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action == "claim":
            return None
        return UserSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action == "list":
            self.permission_classes.append(IsAdmin)

        return super().get_permissions()

    @action(methods=["POST"], detail=False)
    def claim(self, request, *args, **kwargs):
        user = self.request.user
        now = timezone.now()
        if user.claim_datetime > timezone.now():
            raise ValidationError("Claim time does not arrived")

        system_setting = SystemSetting.get_solo()
        user.claim_point += system_setting.claim_point
        if user.referral:
            user.referral.subset_point = system_setting.subset_point
        user.claim_datetime = now + timedelta(seconds=system_setting.claim_period)
        user.save()
        return Response("ok")

    @action(methods=["GET"], detail=False)
    def my_profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)
