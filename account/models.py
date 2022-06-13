from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from solo.models import SingletonModel
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True, unique=True)
    telegram_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    claim_datetime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    claim_point = models.FloatField(default=0)
    referral = models.ForeignKey(
        "self", null=True, blank=True, related_name="subset", on_delete=models.SET_NULL
    )
    subset_point = models.FloatField(default=0)
    total_withdraw = models.FloatField(default=0)
    last_withdraw = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)


class SystemSetting(SingletonModel):
    claim_point = models.FloatField(default=1, blank=True)
    subset_point = models.FloatField(
        default=1, blank=True, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    claim_period = models.IntegerField(default=600, blank=True)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    text = models.TextField()


class GlobalInfo(SingletonModel):
    socials = ArrayField(JSONField(default=dict), default=list, null=True, blank=True)
    extra = JSONField(default=dict, null=True, blank=True)
