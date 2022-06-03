from datetime import timedelta

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.api.serializers import (
    AdminTokenObtainPairSerializer,
    CustomTokenObtainPairSerializer,
    FAQSerializer,
    SystemSettingSerializer,
    UserSerializer,
    WithdrawSerializer,
    GlobalInfoSerializer,
)
from account.models import FAQ, ContactUs, SystemSetting, User
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
        user.claim_datetime = now + timedelta(seconds=system_setting.claim_period*60)
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
        user.withdraw += amount
        user.save()
        return Response("ok")


class SystemSettingViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SystemSettingSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(SystemSetting.get_solo())
        return Response(serializer.data)


    def get_permissions(self):
        self.permission_classes = [IsAuthenticated, IsAdmin]
        
        return super().get_permissions()


    @action(methods=['PUT', 'PATCH'], detail=False)
    def updater(self, request, *args, **kwargs):
        setting = SystemSetting.objects.get()
        if request.data['claim_point']:
            setting.claim_point = float(request.data['claim_point'])
        if request.data['subset_point']:
            setting.claim_point = float(request.data['subset_point'])
        if request.data['claim_period']:
            setting.claim_point = int(request.data['claim_period'])
        if request.data['about_us']:
            setting.claim_point = request.data['about_us']
        setting.save()
        return Response('OK', 200)
        
        



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
    serializer_class = ContactUs
    queryset = ContactUs.objects.all().order_by("id")

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ["list", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAdmin]

        return super().get_permissions()




class GlobalInfoViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = GlobalInfoSerializer

    def get_permissions(self):
        if self.action != 'list':
            permissions = (IsAuthenticated, IsAdmin)
        else:
            permissions = ()
        
        return (Permission() for Permission in permissions)



