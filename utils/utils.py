from functools import reduce
from secrets import token_hex
from rest_framework import serializers
from django.utils.decorators import method_decorator

from django.utils.deconstruct import deconstructible
from django.core import validators
from django.utils.translation import gettext_lazy as _
import random
import json


def get_webpack_context(request):
    with open('static/webpack-assets.json') as f:
        return {"webpack": json.load(f)}


@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r'^(\+98|0)?9\d{9}$'
    message = _(
        'Enter a valid phone number'
    )
    flags = 0


def phone_maker():
    return '09' + f'{random.randint(100000000, 999999999)}'


def gs(**kwargs):
    return type(token_hex(10), (serializers.Serializer,), kwargs)


def multi_method_decorator(decorator, methods: list):
    def _dec(obj):
        for method in methods:
            operation = method_decorator(decorator, method)
            operation(obj)
        return obj
    return _dec


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def getattrd(obj, name, default=None):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """

    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError:
        return default
