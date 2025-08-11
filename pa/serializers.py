from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Action, Plan

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["id", "nom", "excel_path", "excel_sheet", "header_row_index"]


class ActionSerializer(serializers.ModelSerializer):
    responsables = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    act_id = serializers.CharField(read_only=True)

    class Meta:
        model = Action
        fields = [
            "id",
            "act_id",
            "titre",
            "statut",
            "priorite",
            "budget_dzd",
            "responsables",
            "p",
            "d",
            "c",
            "a",
            "j",
            "date_debut",
            "date_fin",
            "commentaire",
            "plan",
            "excel_fichier",
            "excel_feuille",
            "excel_row_index",
        ]
