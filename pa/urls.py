from rest_framework.routers import DefaultRouter

from .views import PlanViewSet, ActionViewSet

router = DefaultRouter()
router.register(r"plans", PlanViewSet)
router.register(r"actions", ActionViewSet, basename="action")

urlpatterns = router.urls
