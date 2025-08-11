from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PlanViewSet, ActionViewSet, ExcelPreview, ExcelRefresh

router = DefaultRouter()
router.register(r"plans", PlanViewSet)
router.register(r"actions", ActionViewSet, basename="action")

urlpatterns = [
    *router.urls,
    path("excel/preview", ExcelPreview.as_view()),
    path("excel/refresh", ExcelRefresh.as_view()),
]
