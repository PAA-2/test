import django_filters
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError

from .models import Action


class StrictOrderingFilter(OrderingFilter):
    def remove_invalid_fields(self, queryset, fields, view, request):
        valid_fields = [term[0] for term in self.get_valid_fields(queryset, view, {'request': request})]
        invalid = [f.lstrip('-') for f in fields if f.lstrip('-') not in valid_fields]
        if invalid:
            raise ValidationError({"ordering": f"Invalid fields: {', '.join(invalid)}"})
        return super().remove_invalid_fields(queryset, fields, view, request)


class ActionFilter(django_filters.FilterSet):
    responsable = django_filters.NumberFilter(field_name="responsables__id")

    class Meta:
        model = Action
        fields = {
            "plan": ["exact"],
            "statut": ["exact"],
            "priorite": ["exact"],
            "j": ["lt", "gt", "exact"],
        }
