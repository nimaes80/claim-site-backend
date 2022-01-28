from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector, NotHandled
from drf_yasg.inspectors.field import get_parent_serializer, get_model_field, get_basic_type_info, \
    get_basic_type_info_from_hint
from drf_yasg.utils import field_value_to_representation
from rest_framework import serializers

from utils.serializers import RangeSerializer


class RangeFieldInspector(FieldInspector):
    """Provides conversions for ``PointField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        # noinspection PyPep8Naming
        SwaggerType, _ = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        if not (isinstance(field, RangeSerializer) and swagger_object_type == openapi.Schema):
            return NotHandled

        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ('lower', openapi.Schema(type=openapi.TYPE_NUMBER)),
                ('upper', openapi.Schema(type=openapi.TYPE_NUMBER)),
            )),
            required=['lower', 'upper']
        )


class ChoiceFieldInspector(FieldInspector):
    """Provides conversions for ``ChoiceField`` and ``MultipleChoiceField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):  # noqa: C901
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if not isinstance(field, serializers.ChoiceField):
            return NotHandled

        enum_type = openapi.TYPE_STRING
        enum_values = []
        enum_value_types = set()
        for choice, hint in field.choices.items():
            if isinstance(field, serializers.MultipleChoiceField):
                choice = field_value_to_representation(field, [choice])[0]
            else:
                choice = field_value_to_representation(field, choice)
            enum_value_types.add(type(choice))
            enum_values.append(f'{choice} => {hint}')

        serializer = get_parent_serializer(field)

        if len(enum_value_types) == 1:
            values_type = get_basic_type_info_from_hint(next(iter(enum_value_types)))
            if values_type:
                enum_type = values_type.get('type', enum_type)
        elif isinstance(serializer, serializers.ModelSerializer):
            model = getattr(getattr(serializer, 'Meta'), 'model')
            # Use the parent source for nested fields
            model_field = get_model_field(model, field.source or field.parent.source)
            # If the field has a base_field its type must be used
            if getattr(model_field, "base_field", None):
                model_field = model_field.base_field
            if model_field:
                model_type = get_basic_type_info(model_field)
                if model_type:
                    enum_type = model_type.get('type', enum_type)

        if isinstance(field, serializers.MultipleChoiceField):
            result = SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=ChildSwaggerType(
                    type=enum_type,
                    enum=enum_values
                )
            )
            if swagger_object_type == openapi.Parameter and result['in'] in (openapi.IN_FORM, openapi.IN_QUERY):
                result.collection_format = 'multi'
        else:
            result = SwaggerType(type=enum_type, enum=enum_values)

        return result
