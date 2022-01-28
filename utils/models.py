from django.db import models

from django.utils import timezone
from utils.config import UtilsConfig as Conf
from django.db.models import F
from django.core.validators import MinValueValidator


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class DeletedMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class LikeMixin(models.Model):
    liked_by = models.ManyToManyField("account.User", blank=True)

    class Meta:
        abstract = True

    @property
    def likes(self):
        return self.liked_by.count()


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        abstract = True


class DraftMixin(models.Model):
    is_draft = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def draft(self):
        self.is_draft = True

    def indraft(self):
        self.is_draft = False


class ArchiveMixin(models.Model):
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()


class ModifyMixin(models.Model):
    modified_at = AutoDateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class ApprovalMixin(models.Model):
    approval_status = models.CharField(
        max_length=50, choices=Conf.APPROVAL_STATUS, default=Conf.PENDING
    )
    changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def approve(self):
        self.approval_status = Conf.APPROVED
        self.changed_at = timezone.now()

    def reject(self):
        self.approval_status = Conf.REJECTED
        self.changed_at = timezone.now()


class OrderableMixin(models.Model):
    order = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(1)]
    )

    class Meta:
        abstract = True

    def default_ordering_query(self, operation="", **kwargs):
        """
        This function is for segmentate records and use needed segment
        for filtering in get_ordering_query function, for example we have
        a model that record's ordering seperated by section field( we call them segment ):

        (segment a) section 1: 1, 2, 3, 4, 5 <- five record, related to section 1 with order from 1 to 5
        (segment b) section 2: 1, 2, 3 <- three record, related to section 2 with order from 1 to 3

        when we want perform some operation on a record it will effect on its segment.
        this function will handle this logical segmentation.

        by default whole records return as a segment
        """
        return self.__class__.objects.all()

    def get_ordering_query(self, operation, **kwargs):
        """
        this function filter records that will effect by operation on a segment
        """
        q = self.default_ordering_query(operation, **kwargs)

        if operation == Conf.UPDATE_DECREASE:
            q = q.filter(order__lte=kwargs["from_order"], order__gte=self.order)

        elif operation == Conf.UPDATE_INCREASE:
            q = q.filter(order__gte=kwargs["from_order"], order__lte=self.order)

        elif operation in [Conf.ADD, Conf.DELETE]:
            q = q.filter(order__gte=self.order).exclude(id=self.id)

        if self.id:
            q = q.exclude(id=self.id)
        return q

    def makeup_order(self, operation, **kwargs):
        # input : 1, 2, 3(delete), 4, 5, ...
        # operation: 4, 5, 6,... -> 3, 4, 5, ...
        if operation == Conf.DELETE:
            query = self.get_ordering_query(operation, **kwargs)
            query.update(order=F("order") - 1)
            self.order = None
            self.save()

        # input : 1, 2, 3(add), 3, 4, 5, ...
        # operation: 3, 4, 5,... -> 4, 5, 6, ...
        elif operation == Conf.ADD:
            query = self.get_ordering_query(operation, **kwargs)
            query.update(order=F("order") + 1)

        # input : 1, 2, 3(move to 6), 4, 5, 6, 7...
        # operation: 4, 5, 6 -> 3, 4, 5
        elif operation == Conf.UPDATE_INCREASE:
            from_order = kwargs.get("from_order", None)
            assert bool(
                from_order
            ), "UPDATE_INCREASE operation need from_order argument"

            query = self.get_ordering_query(operation, **kwargs)
            query.update(order=F("order") - 1)

        # input : 1, 2, 3, 4, 5, 6(move to 3), 7...
        # operation: 3, 4, 5 -> 4, 5, 6
        elif operation == Conf.UPDATE_DECREASE:
            from_order = kwargs.get("from_order", None)
            assert bool(
                from_order
            ), "UPDATE_DECREASE operation need from_order argument"

            query = self.get_ordering_query(operation, **kwargs)
            query.update(order=F("order") + 1)

    def update_order(self, to_order):
        """Wrapping function, for hidding complexity"""
        if not self.order:
            self.add_order()

        from_order = self.order
        position = to_order - from_order
        operation = None
        if position > 0:
            operation = Conf.UPDATE_INCREASE
        elif position < 0:
            operation = Conf.UPDATE_DECREASE
        else:
            return

        count = self.default_ordering_query(operation).count()

        if to_order > count:
            to_order = count

        self.order = to_order
        self.save(update_fields=["order"])

        if position > 0:
            self.makeup_order(operation, from_order=from_order)
        if position < 0:
            self.makeup_order(operation, from_order=from_order)

    def delete_order(self):
        """Wrapping function, for hidding complexity"""
        if self.order:
            self.makeup_order(Conf.DELETE)

    def add_order(self):
        """Wrapping function, for hidding complexity"""
        q = self.default_ordering_query(Conf.ADD)
        if self.id:
            q = q.exclude(id=self.id)
        count = q.count()

        if not self.order:
            self.order = count + 1
            self.save(update_fields=["order"])

        elif self.order > count:
            self.order = count + 1
            self.save(update_fields=["order"])

        self.makeup_order(Conf.ADD)
