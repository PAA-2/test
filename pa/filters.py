import django_filters

from .models import Action


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
