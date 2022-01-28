from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import DjangoRestResponsePagination
from drf_yasg.inspectors import SwaggerAutoSchema

from utils.views import CustomPagination


class CustomPaginationSchema(DjangoRestResponsePagination):
    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        if not isinstance(paginator, CustomPagination):
            return None

        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ('num_of_pages', openapi.Schema(type=openapi.TYPE_INTEGER)),
                ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                ('data', response_schema),
            )),
            required=['data']
        )


class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    class BlankMeta:
        pass

    def get_view_serializer(self):
        return self._convert_serializer(True)

    def get_default_response_serializer(self):
        from drf_yasg.utils import no_body
        body_override = self._get_request_body_override()
        if body_override and body_override is not no_body:
            return body_override

        return self._convert_serializer(False)

    def _convert_serializer(self, is_write):
        serializer = super().get_view_serializer()
        if not serializer:
            return serializer

        new_meta = getattr(serializer.__class__, 'Meta', CustomSwaggerAutoSchema.BlankMeta)

        class CustomSerializer(serializer.__class__):
            class Meta(new_meta):
                ref_name = ('write' if is_write else 'read') + serializer.__class__.__name__

            def get_fields(self):
                new_fields = OrderedDict()
                if is_write:
                    for fieldName, field in super().get_fields().items():
                        if not field.read_only:
                            new_fields[fieldName] = field
                else:
                    for fieldName, field in super().get_fields().items():
                        if not field.write_only:
                            new_fields[fieldName] = field
                return new_fields

        return CustomSerializer(data=serializer.data)
