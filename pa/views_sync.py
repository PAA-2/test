from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import SyncConfig, SyncJob, Profile
from .permissions import RolePermission
from .services.sync import plan_sync
from .scheduler import schedule_from_config


class SyncStatusView(APIView):
    permission_classes = [RolePermission]

    def get(self, request):
        config = SyncConfig.objects.first()
        if not config:
            return Response({"enabled": False})
        data = {
            "enabled": config.enabled,
            "cron": config.cron,
            "strategy": config.strategy,
            "batch_size": config.batch_size,
            "last_run": config.last_run,
            "last_status": config.last_status,
        }
        return Response(data)


class SyncConfigView(APIView):
    permission_classes = [RolePermission]

    def put(self, request):
        if request.user.profile.role not in (
            Profile.Role.SUPER_ADMIN,
            Profile.Role.PILOTE_PROCESSUS,
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        config, _ = SyncConfig.objects.get_or_create(id=1)
        for field in [
            "enabled",
            "cron",
            "strategy",
            "batch_size",
            "retry_on_lock",
            "notes",
        ]:
            if field in request.data:
                setattr(config, field, request.data[field])
        config.save()
        schedule_from_config()
        return Response({"enabled": config.enabled, "cron": config.cron})


class SyncRunView(APIView):
    permission_classes = [RolePermission]

    def post(self, request):
        if request.user.profile.role not in (
            Profile.Role.SUPER_ADMIN,
            Profile.Role.PILOTE_PROCESSUS,
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        dry_run = bool(request.data.get("dry_run"))
        plan_id = request.data.get("plan")
        config = SyncConfig.objects.first()
        if not config:
            config = SyncConfig.objects.create()
        try:
            stats = plan_sync(config, dry_run=dry_run, plan_id=plan_id)
            SyncJob.objects.create(
                plan_id=plan_id,
                status=SyncJob.Status.OK,
                stats=stats,
                dry_run=dry_run,
            )
            config.last_run = timezone.now()
            config.last_status = SyncJob.Status.OK
            config.save(update_fields=["last_run", "last_status"])
        except Exception as exc:  # pragma: no cover - unexpected errors
            SyncJob.objects.create(
                plan_id=plan_id,
                status=SyncJob.Status.FAIL,
                stats={},
                dry_run=dry_run,
                error=str(exc),
            )
            config.last_run = timezone.now()
            config.last_status = SyncJob.Status.FAIL
            config.save(update_fields=["last_run", "last_status"])
            return Response({"error": str(exc)}, status=500)
        return Response({"stats": stats})


class SyncJobsView(APIView):
    permission_classes = [RolePermission]

    def get(self, request):
        qs = SyncJob.objects.all().order_by("-created")
        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        plan_param = request.query_params.get("plan")
        if plan_param:
            qs = qs.filter(plan_id=plan_param)
        dry_run = request.query_params.get("dry_run")
        if dry_run is not None:
            qs = qs.filter(dry_run=dry_run.lower() == "true")
        user = request.user
        if user.profile.role == Profile.Role.PILOTE:
            qs = qs.filter(plan__in=user.profile.plans_autorises.all())
        data = [
            {
                "id": job.id,
                "created": job.created,
                "plan": job.plan_id,
                "status": job.status,
                "stats": job.stats,
                "dry_run": job.dry_run,
            }
            for job in qs
        ]
        return Response(data)
