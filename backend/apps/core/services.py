import math
from django.db import models
from rest_framework import serializers

from .types import PaginatedResult, ServiceResult


class CRUDMixin:
    """Provides basic CRUD operations for a Django model."""

    def get_all(self, queryset=None):
        qs = queryset if queryset is not None else self.model.objects.all()
        return qs

    def get_by_id(self, pk, queryset=None):
        qs = queryset if queryset is not None else self.model.objects.all()
        try:
            return qs.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, **kwargs):
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save(update_fields=list(kwargs.keys()))
        return instance

    def delete(self, instance):
        instance.delete()


class PaginationMixin:
    """Provides queryset pagination."""

    def paginate(self, queryset, page=1, page_size=10):
        total = queryset.count()
        total_pages = math.ceil(total / page_size) if page_size else 1
        offset = (page - 1) * page_size
        items = list(queryset[offset:offset + page_size])
        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class SerializerMixin:
    """Provides serializer helper methods."""

    def serialize(self, instance, serializer_class=None, many=False, context=None):
        klass = serializer_class or self.serializer_class
        return klass(instance, many=many, context=context or {}).data

    def validate_data(self, data, serializer_class=None, instance=None, partial=False, context=None):
        klass = serializer_class or self.serializer_class
        serializer = klass(instance=instance, data=data, partial=partial, context=context or {})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class BaseService(CRUDMixin, PaginationMixin, SerializerMixin):
    """
    Base service class combining CRUD, Pagination, and Serializer mixins.
    All business logic should live in service subclasses, not in views or serializers.
    """

    model = None
    serializer_class = None

    def __init__(self):
        if self.model is None:
            raise ValueError(f'{self.__class__.__name__} must define a model attribute.')

    @classmethod
    def result_ok(cls, data=None):
        return ServiceResult(success=True, data=data)

    @classmethod
    def result_error(cls, error='', errors=None):
        return ServiceResult(success=False, error=error, errors=errors or {})
