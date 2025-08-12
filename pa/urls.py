from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PlanViewSet, ActionViewSet, ExcelPreview, ExcelRefresh
from .views_export import ExportExcelView, ExportPdfView
from .views_stats import DashboardCounters, ProgressChart, ComparePlansChart
from .views_ops import HealthView
from .views_notify import LateNotifyView, SummaryNotifyView, CustomNotifyView
from .views_reports import CustomReportView
from .views_assistant import (
    SuggestClosuresView,
    PrioritizeView,
    SummarizeView,
    AssistantScoresView,
)
from .views_sync import SyncStatusView, SyncConfigView, SyncRunView, SyncJobsView
from .views_custom_fields import CustomFieldViewSet, CustomFieldSchemaView
from .views_quality import (
    QualityRunView,
    QualityIssuesListView,
    QualityIssueResolveView,
    QualityIssueIgnoreView,
    QualityRulesView,
    QualityRuleDetailView,
)
from .views_admin import (
    TemplatesListCreateView,
    TemplateDetailView,
    TemplatePreviewView,
    AutomationsListCreateView,
    AutomationDetailView,
    AutomationRunNowView,
    MenuItemsListCreateView,
    MenuItemDetailView,
    EffectiveMenuView,
)

router = DefaultRouter()
router.register(r"plans", PlanViewSet)
router.register(r"actions", ActionViewSet, basename="action")
router.register(r"admin/custom-fields", CustomFieldViewSet, basename="custom-field")

urlpatterns = [
    *router.urls,
    path("excel/preview", ExcelPreview.as_view()),
    path("excel/refresh", ExcelRefresh.as_view()),
    path("dashboard/counters", DashboardCounters.as_view()),
    path("charts/progress", ProgressChart.as_view()),
    path("charts/compare-plans", ComparePlansChart.as_view()),
    path("export/excel", ExportExcelView.as_view()),
    path("export/pdf", ExportPdfView.as_view()),
    path("notify/late", LateNotifyView.as_view()),
    path("notify/summary", SummaryNotifyView.as_view()),
    path("notify/custom", CustomNotifyView.as_view()),
    path("reports/custom", CustomReportView.as_view()),
    path("assistant/suggest-closures", SuggestClosuresView.as_view()),
    path("assistant/prioritize", PrioritizeView.as_view()),
    path("assistant/summarize", SummarizeView.as_view()),
    path("assistant/scores", AssistantScoresView.as_view()),
    path("admin/custom-fields/schema", CustomFieldSchemaView.as_view()),
    path("sync/status", SyncStatusView.as_view()),
    path("sync/config", SyncConfigView.as_view()),
    path("sync/run", SyncRunView.as_view()),
    path("sync/jobs", SyncJobsView.as_view()),
    path("quality/run", QualityRunView.as_view()),
    path("quality/issues", QualityIssuesListView.as_view()),
    path("quality/issues/<int:pk>/resolve", QualityIssueResolveView.as_view()),
    path("quality/issues/<int:pk>/ignore", QualityIssueIgnoreView.as_view()),
    path("quality/rules", QualityRulesView.as_view()),
    path("quality/rules/<int:pk>", QualityRuleDetailView.as_view()),
    path("admin/templates", TemplatesListCreateView.as_view()),
    path("admin/templates/<int:pk>", TemplateDetailView.as_view()),
    path("admin/templates/<int:pk>/preview", TemplatePreviewView.as_view()),
    path("admin/automations", AutomationsListCreateView.as_view()),
    path("admin/automations/<int:pk>", AutomationDetailView.as_view()),
    path("admin/automations/<int:pk>/run", AutomationRunNowView.as_view()),
    path("admin/menus", MenuItemsListCreateView.as_view()),
    path("admin/menus/<int:pk>", MenuItemDetailView.as_view()),
    path("menu", EffectiveMenuView.as_view()),
    path("health", HealthView.as_view()),
]
