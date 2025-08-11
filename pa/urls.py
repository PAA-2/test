from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PlanViewSet, ActionViewSet, ExcelPreview, ExcelRefresh
from .views_stats import DashboardCounters, ProgressChart, ComparePlansChart

router = DefaultRouter()
router.register(r"plans", PlanViewSet)
router.register(r"actions", ActionViewSet, basename="action")

urlpatterns = [
    *router.urls,
    path("excel/preview", ExcelPreview.as_view()),
    path("excel/refresh", ExcelRefresh.as_view()),
    path("dashboard/counters", DashboardCounters.as_view()),
    path("charts/progress", ProgressChart.as_view()),
    path("charts/compare-plans", ComparePlansChart.as_view()),
]
