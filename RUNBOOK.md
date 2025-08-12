# RUNBOOK

## Sommaire
- [Environnements](#environnements)
- [Secrets](#secrets)
- [Démarrage](#démarrage)
- [Migrations & données](#migrations--données)
- [Synchronisation](#synchronisation)
- [Qualité des données](#qualité-des-données)
- [Exports & rapports](#exports--rapports)
- [Notifications Outlook](#notifications-outlook)
- [Sécurité & performances](#sécurité--performances)
- [Opérations courantes](#opérations-courantes)
- [Checklists](#checklists)

## Environnements
- **Local** : `start.bat` ou `python manage.py runserver` + `npm run dev`
- **Docker dev** : `docker compose --env-file docker/.env.docker up -d --build`
- **Docker prod** : `docker compose -f docker-compose.prod.yml --env-file docker/.env.prod up -d --build`

## Secrets
Définir les variables dans les fichiers `.env.docker` ou `.env.prod`.
Principales clés : `DATABASE_URL`, `DJANGO_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`, `EXCEL_ROOT`, `OUTLOOK_ENABLED`.

## Démarrage
1. Lancer services (local ou docker).
2. Vérifier la santé : `curl http://localhost:8000/api/health`.

## Migrations & données
- `python manage.py migrate --noinput`
- `python manage.py seed_demo` pour jeux de données de test.

## Synchronisation
- Configurer : `PUT /api/sync/config`.
- Exécuter : `POST /api/sync/run` (`dry_run` pour prévisualiser).
- Suivre : `GET /api/sync/jobs`.

## Qualité des données
- Lancer contrôles : `POST /api/quality/run`.
- Résoudre/ignorer : `POST /api/quality/issues/{id}/resolve|ignore`.
- Seuils d’alertes via `QUALITY_ALERT_THRESHOLD`.

## Exports & rapports
- Actions : `GET /api/export/excel|pdf`.
- Rapports custom : `POST /api/reports/custom` (logo, footer, sections).
- Fichiers téléchargés côté client.

## Notifications Outlook
- Requiert Windows + Outlook + `pywin32`.
- Activer avec `OUTLOOK_ENABLED=1`.
- Endpoints : `POST /api/notify/late|summary|custom` (`dry_run` pour brouillon).

## Sécurité & performances
- Throttling DRF : `120/min` par utilisateur.
- Cache charts : 60 s par utilisateur et paramètres.
- Index DB sur champs principaux (statut, priorite, delais, dates, plan).
- Logs structurés avec `request_id`.

## Opérations courantes
- Rotation des logs : via logrotate ou purge manuelle.
- Sauvegarde DB : dump PostgreSQL (`pg_dump`).
- Restauration : `psql` ou remplacement volume.
- Mise à jour images Docker : rebuild + `docker compose pull`.
- Rollback : relancer l’ancienne image/commit.

## Checklists
### Avant mise en prod
- Tests unitaires et E2E passés
- Variables `.env.prod` à jour
- Images Docker construites

### Après déploiement
- Vérifier `/api/health`
- Lancer `seed_demo` si nécessaire
- Examiner logs au démarrage

### Incident
- Consulter logs (`docker compose logs`)
- Vérifier DB et services
- Utiliser `dry_run` pour reproduire sans impacts
