from django.contrib import admin

from .models import NotificationTemplate, CustomField, CustomFieldOption


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
