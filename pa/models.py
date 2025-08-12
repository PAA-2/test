from django.conf import settings
from django.db import models


class Plan(models.Model):
    nom = models.CharField(max_length=255)
    excel_path = models.CharField(max_length=500)
    excel_sheet = models.CharField(max_length=255)
    header_row_index = models.IntegerField()
    actif = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["actif"]),
            models.Index(fields=["nom"]),
            models.Index(fields=["excel_path"]),
        ]

    def __str__(self) -> str:
        return self.nom


class Action(models.Model):
    act_id = models.CharField(max_length=9, unique=True, db_index=True)
    titre = models.CharField(max_length=255)
    statut = models.CharField(max_length=50, db_index=True)
    priorite = models.CharField(max_length=50, db_index=True)
    budget_dzd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    responsables = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="actions", blank=True)
    p = models.BooleanField(default=False)
    d = models.BooleanField(default=False)
    c = models.BooleanField(default=False)
    a = models.BooleanField(default=False)
    j = models.IntegerField(null=True, blank=True, db_index=True)
    date_creation = models.DateField(null=True, blank=True, db_index=True)
    delais = models.DateField(null=True, blank=True, db_index=True)
    date_realisation = models.DateField(null=True, blank=True, db_index=True)
    commentaire = models.TextField(blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="actions", db_index=True)
    excel_fichier = models.CharField(max_length=255)
    excel_feuille = models.CharField(max_length=255)
    excel_row_index = models.IntegerField(db_index=True)
    custom = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.act_id} - {self.titre}"

    class Meta:
        indexes = [
            models.Index(fields=["statut"]),
            models.Index(fields=["priorite"]),
            models.Index(fields=["delais"]),
            models.Index(fields=["date_creation"]),
            models.Index(fields=["date_realisation"]),
            models.Index(fields=["plan"]),
            models.Index(fields=["excel_row_index"]),
        ]


class Profile(models.Model):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SuperAdmin", "SuperAdmin"
        PILOTE_PROCESSUS = "PiloteProcessus", "PiloteProcessus"
        PILOTE = "Pilote", "Pilote"
        UTILISATEUR = "Utilisateur", "Utilisateur"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices)
    plans_autorises = models.ManyToManyField(Plan, blank=True)

    def __str__(self) -> str:
        return f"{self.user} ({self.role})"


class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class CustomField(models.Model):
    class Type(models.TextChoices):
        TEXT = "text", "text"
        NUMBER = "number", "number"
        DATE = "date", "date"
        SELECT = "select", "select"
        TAGS = "tags", "tags"
        BOOL = "bool", "bool"

    class Visibility(models.TextChoices):
        ALL = "All", "All"
        SA_PP = "SA_PP", "SA_PP"
        PILOTE = "Pilote", "Pilote"
        UTILISATEUR = "Utilisateur", "Utilisateur"

    name = models.CharField(max_length=100)
    key = models.SlugField(unique=True)
    type = models.CharField(max_length=10, choices=Type.choices)
    required = models.BooleanField(default=False)
    min = models.IntegerField(null=True, blank=True)
    max = models.IntegerField(null=True, blank=True)
    regex = models.CharField(max_length=255, blank=True)
    help_text = models.CharField(max_length=255, blank=True)
    role_visibility = models.CharField(
        max_length=20, choices=Visibility.choices, default=Visibility.ALL
    )
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class CustomFieldOption(models.Model):
    field = models.ForeignKey(
        CustomField, on_delete=models.CASCADE, related_name="options"
    )
    value = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.field.key}:{self.value}"


class SyncConfig(models.Model):
    class Strategy(models.TextChoices):
        PLAN = "plan", "plan"
        ALL = "all", "all"
        ACTIVE = "active", "active"

    enabled = models.BooleanField(default=True)
    cron = models.CharField(max_length=100, default=settings.SYNC_DEFAULT_CRON)
    strategy = models.CharField(
        max_length=10, choices=Strategy.choices, default=Strategy.ALL
    )
    batch_size = models.IntegerField(default=settings.SYNC_BATCH_SIZE)
    retry_on_lock = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"SyncConfig({self.cron})"


class SyncJob(models.Model):
    class Status(models.TextChoices):
        OK = "OK", "OK"
        FAIL = "FAIL", "FAIL"
        PARTIAL = "PARTIAL", "PARTIAL"

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    status = models.CharField(max_length=10, choices=Status.choices, db_index=True)
    stats = models.JSONField(default=dict, blank=True)
    dry_run = models.BooleanField(default=False)
    error = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"SyncJob({self.status})"

class DataQualityRule(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "LOW"
        MED = "MED", "MED"
        HIGH = "HIGH", "HIGH"
        CRITICAL = "CRITICAL", "CRITICAL"

    class Scope(models.TextChoices):
        ACTION = "action", "action"
        PLAN = "plan", "plan"
        EXCEL = "excel", "excel"

    key = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    enabled = models.BooleanField(default=True)
    params = models.JSONField(default=dict, blank=True)
    scope = models.CharField(max_length=10, choices=Scope.choices, default=Scope.ACTION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.key


class DataQualityIssue(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "LOW"
        MED = "MED", "MED"
        HIGH = "HIGH", "HIGH"
        CRITICAL = "CRITICAL", "CRITICAL"

    class Status(models.TextChoices):
        OPEN = "OPEN", "OPEN"
        RESOLVED = "RESOLVED", "RESOLVED"
        IGNORED = "IGNORED", "IGNORED"

    rule_key = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=Severity.choices, db_index=True)
    entity_type = models.CharField(max_length=10)
    act_id = models.CharField(max_length=9, null=True, blank=True)
    entity_id = models.IntegerField(null=True, blank=True)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN, db_index=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            "rule_key",
            "entity_type",
            "act_id",
            "entity_id",
            "message",
        )

    def __str__(self) -> str:
        return f"{self.rule_key}:{self.entity_type}:{self.act_id or self.entity_id}"
