from datetime import datetime
import requests
from rest_framework import serializers

from sample_pack.google_auth.google_oauth_kit import get_google_oauth_data
from .model import OAuthConnection
from rest_framework_simplejwt.tokens import RefreshToken
from core_config import settings
from django.utils import timezone
from account.models import User


class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True)
    redirect_url = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        data = {}
        try:
            data = get_google_oauth_data(attrs["redirect_url"], attrs["access_token"])
        except Exception as e:
            raise serializers.ValidationError(e.message)
        return data

    def get_access_data(self, user):
        # here can cen send any type of access data
        # because in our services we mostly use jwt
        # I implented jwt as default access token

        token = RefreshToken.for_user(user)
        expire_date = (
            datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
            + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        )
        return {
            "access": token.access_token,
            "refresh": token,
            "expire_date": expire_date.isoformat(),
        }

    def create(self, validated_data):
        id_token = validated_data["id_token"]
        google_id = id_token["sub"]
        connection = OAuthConnection.objects.filter(google_id=google_id).first()
        connection_data = dict(
            google_id=google_id,
            token=validated_data["token"],
            refresh_token=validated_data["refresh_token"],
            scopes=validated_data["scopes"],
            id_token=id_token,
        )

        if connection:
            # update connection with new income data
            for k, v in connection_data.items():
                setattr(connection, k, v)
            connection.save()
            return self.get_access_data(connection.user)

        new_connection = OAuthConnection(**connection_data)
        user = User.objects.filter(email=id_token["email"]).first()
        if user:
            new_connection.user = user
            new_connection.save()
            if not user.is_email_active:
                user.is_email_active = id_token["email_verified"]
                user.save()
            return self.get_access_data(user)

        user = User(
            is_email_active=id_token["email_verified"],
            username=id_token["email"],
            email=id_token["email"],
            first_name=id_token["name"],
        )

        # create a random password that can't use for login
        user.set_password(None)

        # if your model has avatar you can fetch 
        # and save users google avatar with below code 
        # 
        #from django.core.files import File
        #from tempfile import NamedTemporaryFile
        #
        #r = requests.get(id_token["picture"])
        #img_temp = NamedTemporaryFile(delete=True)
        #img_temp.write(r.content)
        #img_temp.flush()
        #user.avatar.save(
        #    f"{id_token['sub']}-{id_token['name']}.jpg", File(img_temp), save=True
        #)

        user.save()
        new_connection.user = user
        new_connection.save()
        return self.get_access_data(user)
