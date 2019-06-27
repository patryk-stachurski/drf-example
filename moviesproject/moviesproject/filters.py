from django.core.exceptions import ValidationError

from django_filters.rest_framework import FilterSet as DjangoFilterSet

from django_filters.filters import __all__ as filters_all
from django_filters.filters import *


__all__ = filters_all
__all__ += [
    'FilterSet',
    'NumberInFilter',
]


class FilterSet(DjangoFilterSet):
    @property
    def errors(self):
        errors = self.form.errors

        # Implements validation of request query params
        for name, field in self.form.fields.items():
            if name not in errors:
                param_value = self.request.query_params.get(name, None)

                try:
                    v = field.to_python(param_value)
                    field.validate(v)
                except ValidationError as exception:
                    errors[name] = self.form.error_class([exception])
                except:
                    continue

        return errors


class NumberInFilter(BaseInFilter, NumberFilter):
    pass
