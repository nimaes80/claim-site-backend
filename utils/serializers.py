import six

# noinspection PyProtectedMember
from psycopg2._range import NumericRange
from rest_framework import serializers
from rest_framework.utils import json


class CurrentContextDefault:
    def __init__(self, key):
        self.key = key
        self.value = None

    def set_context(self, serializer_field):
        self.value = serializer_field.context[self.key]

    def __call__(self):
        return self.value

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class PrimaryKeyRelatedDynamicQuerySetField(serializers.PrimaryKeyRelatedField):
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        # The method name defaults to `get_{field_name}_queryset`.
        if self.method_name is None:
            self.method_name = f"get_{field_name}_queryset"
        super().bind(field_name, parent)

    def get_queryset(self):
        method = getattr(self.parent, self.method_name)
        return method()


class RangeSerializer(serializers.Field):
    """
    Expected input format:
        {
        "start": 49,
         "end": 24
        }
    """

    type_name = "RangeField"
    type_label = "range"

    default_error_messages = {
        "invalid": "Enter a valid Range.",
    }

    def to_internal_value(self, value):
        """
        Parse json data and return a range object
        """
        if value in (None, "", [], (), {}) and not self.required:
            return None

        if isinstance(value, six.string_types):
            try:
                value = value.replace("'", '"')
                value = json.loads(value)
            except ValueError:
                self.fail("invalid")

        if value and isinstance(value, dict):
            try:
                return NumericRange(int(value["lower"]), int(value["upper"]))
            except (TypeError, ValueError, KeyError):
                self.fail("invalid")
        self.fail("invalid")

    def to_representation(self, value):
        if isinstance(value, NumericRange):
            value = {"lower": value.lower, "upper": value.upper}
        return value


class CustomChoiceField(serializers.ChoiceField):
    def to_representation(self, data):
        if data not in self.choices.keys():
            self.fail("invalid_choice", input=data)
        else:
            return self.choices[data]


class UpdateOrderSerializer(serializers.ModelSerializer):
    to_order = serializers.IntegerField(write_only=True)

    def update(self, instance, validated_data):
        to_order = validated_data.get("to_order", None)
        instance.update_order(to_order)

        return instance

    class Meta:
        fields = ["to_order"]
