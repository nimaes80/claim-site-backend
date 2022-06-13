from utils.utils import getattrd
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 10000
    page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'num_of_pages': self.page.paginator.num_pages,
            'count': self.page.paginator.count,
            'data': data,
        })


class ExtraContextMixin:
    def get_serializer_context(self):
        # noinspection PyUnresolvedReferences
        context = super().get_serializer_context()
        context.update(self.extra_context())
        return context

    def extra_context(self):
        return {}


class UserContextMixin(ExtraContextMixin):
    def extra_context(self):
        extra_context = super().extra_context()
        extra_context['user'] = getattr(self.request, 'user', None)
        return extra_context


class LawyerContextMixin(ExtraContextMixin):
    def extra_context(self):
        extra_context = super().extra_context()
        extra_context['lawyer'] = getattrd(self.request, 'user.lawyer', None)
        return extra_context


class CustomOrderingFilter(OrderingFilter):
    def get_schema_fields(self, view):
        import coreapi
        import coreschema
        from django.utils.encoding import force_str
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        valid_fields = getattr(view, 'ordering_fields', None)
        default_fields = getattr(view, 'ordering', None)
        if valid_fields is not None:
            valid_fields = ', '.join(valid_fields)
        if default_fields is not None:
            if isinstance(default_fields, str):
                default_fields = (default_fields,)
            default_fields = ', '.join(default_fields)
        valid_fields = valid_fields or ''
        default_fields = default_fields or ''
        # noinspection PyArgumentList
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.ordering_title),
                    description=f'choices: {valid_fields},\n default: {default_fields}'
                )
            )
        ]
