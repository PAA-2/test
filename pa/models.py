from django.conf import settings
from django.db import models


class Plan(models.Model):
    nom = models.CharField(max_length=255)
    excel_path = models.CharField(max_length=500)
    excel_sheet = models.CharField(max_length=255)
    header_row_index = models.IntegerField()

    def __str__(self) -> str:
        return self.nom


class Action(models.Model):
    act_id = models.CharField(max_length=9, unique=True)
    titre = models.CharField(max_length=255)
    statut = models.CharField(max_length=50)
    priorite = models.CharField(max_length=50)
    budget_dzd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    responsables = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="actions", blank=True)
    p = models.BooleanField(default=False)
    d = models.BooleanField(default=False)
    c = models.BooleanField(default=False)
    a = models.BooleanField(default=False)
    j = models.IntegerField(null=True, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="actions")
    excel_fichier = models.CharField(max_length=255)
    excel_feuille = models.CharField(max_length=255)
    excel_row_index = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.act_id} - {self.titre}"


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
