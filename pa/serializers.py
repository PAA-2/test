from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Action,
    Plan,
    CustomField,
    CustomFieldOption,
    DataQualityRule,
    DataQualityIssue,
    Template,
    Automation,
    MenuItem,
)
from .custom_fields import (
    load_definitions_for_role,
    validate_custom_payload,
    filter_custom_for_role,
)

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "nom",
            "excel_path",
            "excel_sheet",
            "header_row_index",
            "actif",
        ]


class ActionSerializer(serializers.ModelSerializer):
    responsables = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    act_id = serializers.CharField(read_only=True)
    custom = serializers.JSONField(required=False, default=dict)

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
            "date_creation",
            "delais",
            "date_realisation",
            "commentaire",
            "plan",
            "excel_fichier",
            "excel_feuille",
            "excel_row_index",
            "custom",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        defs = self.context.get("custom_field_defs") or load_definitions_for_role(user)
        custom_payload = attrs.get("custom", {}) or {}
        attrs["custom"] = validate_custom_payload(custom_payload, defs)
        return super().validate(attrs)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        defs = self.context.get("custom_field_defs")
        data["custom"] = filter_custom_for_role(instance.custom or {}, user, defs)
        return data


class CustomFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldOption
        fields = ["id", "value", "label", "order"]


class CustomFieldSerializer(serializers.ModelSerializer):
    options = CustomFieldOptionSerializer(many=True, required=False)

    class Meta:
        model = CustomField
        fields = [
            "id",
            "name",
            "key",
            "type",
            "required",
            "min",
            "max",
            "regex",
            "help_text",
            "role_visibility",
            "active",
            "options",
        ]

    def create(self, validated_data):
        options = validated_data.pop("options", [])
        field = super().create(validated_data)
        for opt in options:
            CustomFieldOption.objects.create(field=field, **opt)
        return field

    def update(self, instance, validated_data):
        options = validated_data.pop("options", None)
        field = super().update(instance, validated_data)
        if options is not None:
            instance.options.all().delete()
            for opt in options:
                CustomFieldOption.objects.create(field=instance, **opt)
        return field


class DataQualityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataQualityRule
        fields = [
            "id",
            "key",
            "name",
            "description",
            "severity",
            "enabled",
            "params",
            "scope",
            "created_at",
            "updated_at",
        ]


class DataQualityIssueSerializer(serializers.ModelSerializer):
    resolved_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DataQualityIssue
        fields = [
            "id",
            "rule_key",
            "severity",
            "entity_type",
            "act_id",
            "entity_id",
            "plan",
            "message",
            "details",
            "detected_at",
            "status",
            "resolved_by",
            "resolved_at",
        ]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "kind",
            "subject",
            "body_html",
            "body_text",
            "variables",
            "is_default",
            "active",
        ]

    def validate(self, attrs):
        kind = attrs.get("kind") or (self.instance.kind if self.instance else None)
        if kind == "email" and not attrs.get("subject") and not (self.instance and self.instance.subject):
            raise serializers.ValidationError({"subject": "required for email"})
        return attrs


class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = [
            "id",
            "name",
            "enabled",
            "trigger",
            "cron",
            "filters",
            "condition",
            "action",
            "action_params",
            "last_run_at",
            "last_status",
            "last_message",
        ]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "key",
            "label",
            "icon",
            "path",
            "visible_for_roles",
            "order",
            "active",
        ]

    def validate_order(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("order must be integer")
        return value
