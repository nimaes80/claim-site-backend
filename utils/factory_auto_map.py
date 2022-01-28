from factory import Faker, fuzzy, django, LazyAttribute
from django.db import models
from functools import wraps
from django.utils import timezone
from random import choice


class Adaptor:
    def choice_field(self, field):
        return fuzzy.FuzzyChoice(dict(field.choices).keys())

    def text_field(self, field):
        return Faker('text', max_nb_chars=1023)

    def char_field(self, field):
        if field.choices:
            return self.choice_field(field)

        return Faker('text', max_nb_chars=field.max_length)

    def boolean_field(self, field):
        return fuzzy.FuzzyChoice([True, False])

    def integer_field(self, field):
        if field.choices:
            return self.choice_field(field)

        return Faker('pyint')

    def float_field(self, field):
        if field.choices:
            return self.choice_field(field)

        return Faker('pyfloat')

    def email_field(self, field):
        return Faker('email')

    def datetime_field(self, field):
        return Faker('date_time', tzinfo=timezone.get_current_timezone())

    def date_field(self, field):
        return Faker('date', tzinfo=timezone.get_current_timezone())

    def image_field(self, field):
        return django.ImageField()

    def file_field(self, field):
        return django.FileField()

    def slug_field(self, field):
        return Faker('slug')

    def foreign_key_field(self, field):
        model = field.remote_field.model
        if field.null:
            return LazyAttribute(lambda a: choice([
                model.objects.order_by('?').first(),
                None
            ]))
        return LazyAttribute(lambda a: model.objects.order_by('?').first())


adaptor = Adaptor()

fields_map = {
    models.CharField: adaptor.char_field,
    models.IntegerField: adaptor.integer_field,
    models.FloatField: adaptor.float_field,
    models.BooleanField: adaptor.boolean_field,
    models.DateTimeField: adaptor.datetime_field,
    models.DateField: adaptor.date_field,
    models.EmailField: adaptor.email_field,
    models.ImageField: adaptor.image_field,
    models.FileField: adaptor.image_field,
    models.ForeignKey: adaptor.foreign_key_field,
    models.TextField: adaptor.text_field,
    models.SlugField: adaptor.slug_field
}


def factory_auto_map(needed_fields='__all__', exclude=[]):
    def inner(factory_class):
        def collect_adapted_data():
            model = factory_class._meta.model
            model_fields = []
            data = {}
            if needed_fields == '__all__':
                model_fields = model._meta.get_fields()
            else:
                for f in needed_fields:
                    model_fields.append(model._meta.get_field(f))

            for f in model_fields:
                if f.name in exclude:
                    continue

                adapt_function = fields_map.get(type(f), None)
                if adapt_function:
                    data[f.name] = adapt_function(f)

            return data

        @wraps(factory_class)
        def wrapper(*args, **kwargs):
            data = collect_adapted_data()
            data.update(kwargs)  # appreciate income values over auto generated values
            return factory_class(*args, **data)

        def build(*args, **kwargs):
            data = collect_adapted_data()
            data.update(kwargs)
            return factory_class.build(*args, **data)

        def create_batch(*args, **kwargs):
            data = collect_adapted_data()
            data.update(kwargs)
            return factory_class.create_batch(*args, **data)

        wrapper.build = build
        wrapper.create_batch = create_batch

        return wrapper
    return inner
