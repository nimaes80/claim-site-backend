import requests
from rest_framework import serializers

from account.models import FAQ, ContactUs, PublicInfo, SystemSetting, User
from core_config import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login


class CustomTokenObtainPairSerializer(serializers.Serializer):
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    wallet_address = serializers.CharField(write_only=True)
    telegram_id = serializers.CharField(write_only=True)
    referral = serializers.SlugRelatedField(
        slug_field="uuid", queryset=User.objects.all(), required=False, write_only=True
    )
    if settings.CAPTCHA_TYPE == "recaptcha":
        captcha_token = serializers.CharField(write_only=True)

    def check_recaptcha(self, attrs):
        captcha_token = attrs.get("captcha_token")

        # https://developers.google.com/recaptcha/docs/verify#api_request
        data = requests.post(
            settings.CAPTCHA_URL,
            data={
                "secret": settings.CAPTCHA_SECRET,
                "response": captcha_token,
            },
        ).json()

        if not data.get("success"):
            raise serializers.ValidationError(
                f"Captcha is not valid, captcha service's response is `{data.get('error-codes')}`",
                "invalid_recaptcha",
            )

    def validate_wallet_address(self, value: str):
        if not value.startswith("0"):
            raise serializers.ValidationError("Enter a valid wallet address")
        return value

    def validate_telegram_id(self, value: str):
        if not value.startswith("@"):
            raise serializers.ValidationError("Enter a valid telegram id")
        return value

    def validate(self, attrs):
        # recaptcha service only work in production server so for
        # development we have to disable it
        if settings.CAPTCHA_TYPE == "recaptcha":
            self.check_recaptcha(attrs)

        wallet_address = attrs.pop("wallet_address")
        telegram_id = attrs.pop("telegram_id")
        self.user, is_created = User.objects.get_or_create(
            wallet_address=wallet_address, telegram_id=telegram_id
        )

        referral = attrs.pop("referral", None)
        if is_created and referral:
            self.user.referral = referral
            self.user.save()

        refresh = RefreshToken.for_user(self.user)

        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return attrs


class AdminTokenObtainPairSerializer(serializers.Serializer):
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    username = serializers.CharField()
    password = serializers.CharField()
    if settings.CAPTCHA_TYPE == "recaptcha":
        captcha_token = serializers.CharField(write_only=True)

    def check_recaptcha(self, attrs):
        captcha_token = attrs.get("captcha_token")

        # https://developers.google.com/recaptcha/docs/verify#api_request
        data = requests.post(
            settings.CAPTCHA_URL,
            data={
                "secret": settings.CAPTCHA_SECRET,
                "response": captcha_token,
            },
        ).json()

        if not data.get("success"):
            raise serializers.ValidationError(
                f"Captcha is not valid, captcha service's response is `{data.get('error-codes')}`",
                "invalid_recaptcha",
            )

    def validate(self, attrs):
        # recaptcha service only work in production server so for
        # development we have to disable it
        if settings.CAPTCHA_TYPE == "recaptcha":
            self.check_recaptcha(attrs)

        username = attrs.pop("username")
        password = attrs.pop("password")
        self.user = User.objects.filter(username=username).first()
        if (
            not self.user
            or not self.user.check_password(password)
            or not self.user.is_staff
        ):
            raise serializers.ValidationError("Incorrect credentials")

        refresh = RefreshToken.for_user(self.user)

        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "wallet_address",
            "telegram_id",
            "claim_datetime",
            "claim_point",
            "referral",
            "subset_point",
            "withdraw",
        ]


class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.FloatField()


class PublicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicInfo
        fields = "__all__"
