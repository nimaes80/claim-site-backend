from datetime import timedelta

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import get_object_or_404
from account.api.serializers import (
    AdminTokenObtainPairSerializer,
    CustomTokenObtainPairSerializer,
    FAQSerializer,
    SystemSettingSerializer,
    UserSerializer,
    WithdrawSerializer,
    GlobalInfoSerializer,
    ContactUsSerializer,
)
from account.models import FAQ, ContactUs, GlobalInfo, SystemSetting, User
from utils.permissions import IsAdmin
from utils.utils import gs


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
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "claim":
            return None
        if self.action == "withdraw":
            return WithdrawSerializer
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
        user.claim_datetime = now + timedelta(seconds=system_setting.claim_period * 60)
        user.save()
        return Response("ok")

    @action(methods=["GET"], detail=False)
    def my_profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False)
    def withdraw(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["amount"]
        user = self.request.user
        balance = user.claim_point + user.subset_point
        if balance - (amount + user.withdraw) < 0:
            raise ValidationError("User does not have enough balance")
        user.total_withdraw += amount
        user.last_withdraw = amount
        user.save()
        return Response("ok")

    @action(methods=["POST"], detail=False)
    def pay(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        if user_id:
            user = get_object_or_404(User, id=user_id)
            if user.last_withdraw > 0:
                user.last_withdraw = 0
                user.save()
                return Response("OK")
            return Response("User don't want to pay", status=200)
        return Response("User ID is not provided", status=400)


class SystemSettingViewSet(
    viewsets.GenericViewSet,
):
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(methods=["GET"], detail=False)
    def get_setting(self, request, *args, **kwargs):
        serializer = self.get_serializer(SystemSetting.get_solo())
        return Response(serializer.data)

    @action(methods=["PATCH"], detail=False)
    def update_setting(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            SystemSetting.get_solo(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FAQViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = FAQ.objects.all().order_by("id")

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated, IsAdmin]
        if self.action == "list":
            self.permission_classes = []

        return super().get_permissions()


class ContactUsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all().order_by("id")

    def get_permissions(self):
        self.permission_classes = []
        if self.action in ["list", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAdmin]

        return super().get_permissions()


class GlobalInfoViewSet(
    viewsets.GenericViewSet,
):
    serializer_class = GlobalInfoSerializer

    def get_permissions(self):
        self.permission_classes = (IsAuthenticated, IsAdmin)
        if self.action == "get_info":
            self.permission_classes = ()
        return super().get_permissions()

    @action(methods=["GET"], detail=False)
    def get_info(self, request, *args, **kwargs):
        serializer = self.get_serializer(GlobalInfo.get_solo())
        return Response(serializer.data)

    @action(methods=["PATCH"], detail=False)
    def update_info(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            GlobalInfo.get_solo(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
