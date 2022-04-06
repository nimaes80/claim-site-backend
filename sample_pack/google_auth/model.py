from django.db import models
from django.contrib.postgres.fields import ArrayField


class OAuthConnection(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    google_id = models.TextField(null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    scopes = ArrayField(models.TextField(), null=True, blank=True)
    id_token = models.JSONField(null=True, blank=True)
