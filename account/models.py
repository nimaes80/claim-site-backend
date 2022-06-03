from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from solo.models import SingletonModel


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    telegram_id = models.CharField(max_length=255, null=True, blank=True)
    claim_datetime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    claim_point = models.FloatField(default=0)
    referral = models.ForeignKey(
        "self", null=True, blank=True, related_name="subset", on_delete=models.SET_NULL
    )
    subset_point = models.FloatField(default=0)
    withdraw = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)


class SystemSetting(SingletonModel):
    claim_point = models.FloatField(default=1)
    subset_point = models.FloatField(default=1)
    claim_period = models.IntegerField(default=600)


class PublicInfo(SingletonModel):
    about_us = models.TextField(null=True, blank=True)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
