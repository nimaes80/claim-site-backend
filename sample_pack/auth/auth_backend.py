from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q


class MultiIdentifierBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.filter(
            (Q(username=username) | Q(email=username)) & Q(is_active=True)
        ).first()
        if user and user.check_password(password):
            return user

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id).first()
