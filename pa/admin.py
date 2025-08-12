from django.contrib import admin

from .models import (
    NotificationTemplate,
    CustomField,
    CustomFieldOption,
    SyncConfig,
    SyncJob,
    DataQualityRule,
    DataQualityIssue,
    Template,
    Automation,
    MenuItem,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_default", "active")


class CustomFieldOptionInline(admin.TabularInline):
    model = CustomFieldOption
    extra = 1


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldOptionInline]
    list_display = ("name", "key", "type", "active")


@admin.register(SyncConfig)
class SyncConfigAdmin(admin.ModelAdmin):
    list_display = ("enabled", "cron", "strategy", "last_run", "last_status")


@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ("created", "plan", "status", "dry_run")


@admin.register(DataQualityRule)
class DataQualityRuleAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "severity", "enabled")
    search_fields = ("key", "name")


@admin.register(DataQualityIssue)
class DataQualityIssueAdmin(admin.ModelAdmin):
    list_display = (
        "rule_key",
        "severity",
        "entity_type",
        "act_id",
        "plan",
        "status",
        "detected_at",
    )
    list_filter = ("severity", "status", "rule_key")
    search_fields = ("act_id", "message", "plan__nom")


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "action", "enabled", "last_status")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "order", "active")
