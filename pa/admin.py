from django.contrib import admin

from .models import (
    NotificationTemplate,
    CustomField,
    CustomFieldOption,
    SyncConfig,
    SyncJob,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")


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
