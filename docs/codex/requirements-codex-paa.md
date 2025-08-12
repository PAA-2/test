# Requirements Codex PAA

## Sommaire
- [1. Contexte](#1-contexte)
- [2. Architecture & Dossiers](#2-architecture--dossiers)
- [3. Endpoints essentiels](#3-endpoints-essentiels)
- [4. Règles métier](#4-règles-métier)
- [5. Modules](#5-modules)
- [6. Critères globaux](#6-critères-globaux)
- [7. Modèles de prompts](#7-modèles-de-prompts)
- [8. Checklists](#8-checklists)

## 1. Contexte
Application intranet pour suivre des plans d’action à partir de fichiers Excel, qui restent la source de vérité. Chaque action possède un identifiant ACT‑XXXX synchronisé entre Excel et la base. Les modifications passent toujours par la ligne Excel correspondante avant ré‑ingestion. Le backend Django REST Framework communique avec une base PostgreSQL portable et manipule les fichiers via pandas/openpyxl. Le frontend React, Vite et Tailwind fournit l’interface authentifiée (JWT) pour quatre rôles : SuperAdmin, PiloteProcessus, Pilote et Utilisateur. Les exports PDF utilisent reportlab et des notifications Outlook locales sont possibles. L’objectif est de consolider, valider et clôturer les actions tout en garantissant la traçabilité et le respect des rôles.

## 2. Architecture & Dossiers
- backend/ — API Django+DRF
- frontend/ — UI React+Vite+Tailwind
- excel/ — plans sources
- docs/ — documentation & Codex
- docker/ — compose & scripts
- start.bat — lanceur Windows
- requirements.txt & pyproject.toml — dépendances
- .github/workflows/ci.yml — CI
- README.md, RUNBOOK.md, TROUBLESHOOTING.md

## 3. Endpoints essentiels
- POST /auth/login; POST /auth/refresh; POST /auth/logout; GET /users/me; CRUD /users
- CRUD /plans; POST /plans/{id}/rescan; GET /excel/preview?plan
- GET/POST /actions; GET/PUT/DELETE /actions/{act_id}; POST /actions/{act_id}/validate|close|reject|assign; POST /actions/bulk-import|bulk-update
- POST /sync/run; GET /sync/status; PUT /sync/config; POST /excel/refresh
- GET /dashboard/counters; GET /charts/progress; GET /charts/compare-plans
- GET /export/excel|pdf; POST /reports/custom; GET /reports/kpis
- POST /notify/late|summary|custom
- CRUD /admin/modules|settings|custom-fields|templates|automations|menus
- GET /logs; GET /logs/{id}; GET /logs/stats
- POST /assistant/suggest-closures|prioritize|summarize; GET /assistant/scores
- POST /quality/run; GET /quality/issues
- GET /health

## 4. Règles métier
- Excel = source de vérité, consolidé lecture seule
- ACT-ID unique ACT-XXXX commun aux occurrences
- Écritures ciblent `excel_row_index` puis ré-ingestion
- Multi-occurrences selon stratégie (toutes/plan/active)
- PDCA : validation coche C et A
- Champ J = delais - aujourd’hui
- Responsables séparés par "," ou ";"
- Filtres identiques liste/exports/rapports
- Rôles limitent la portée des plans
- Traçabilité Excel : fichier, feuille, row_index
- Sync périodique vérifie changements Excel↔DB
- Exports conservent colonnes et ordre de la liste

## 5. Modules
- Bloc 1 : Utilisateurs, rôles, paramètres, plans, mappage, ACT-ID, traçabilité, audit, sécurité, backups
- Bloc 2 : CRUD actions/plans, multi-responsables, workflow, validation/rejet, filtres, consolidé, historique, import
- Bloc 3 : Planificateur sync, détection changements, conflits, dry-run, ciblage, alertes, journal, perf, cohérence, réindexation
- Bloc 4 : Export Excel/PDF, rapports custom, diffusion, favoris, watermark, bordereaux, archives, comparatifs, qualité données
- Bloc 5 : Layout global, thèmes, formulaires, tableaux filtrables, vues rôles, bulles, graphiques, modales/toasts, accessibilité, i18n
- Bloc 6 : Champs perso, validations, modèles, automations, form/list builder, notif rules, calendrier, menus, paramètres export
- Bloc 7 : Générateur test, Outlook, watcher, verrouillage, résilience I/O, hashing, compression, impression, sauvegarde/restauration
- Bloc 8 : Index DB, cache, batch writer, profiling, monitoring, rate limit, limites upload, nettoyage archives, tests unitaires/intégration
- Bloc 9 : Assistante locale, résumés, priorisation, scores, recommandations, préremplissage, aide contextuelle, rappels, rapports mensuels, journal
- Bloc 10 : Gouvernance, conformité, traçabilité forte, continuité, risques, conformité locale, anonymisation, audit renforcé, revues périodiques, clôture cycle

## 6. Critères globaux
- Authentification JWT + rate limit
- Index DB, cache lecture, pagination stricte
- Filtres cohérents entre liste et exports
- Rôles appliqués à tous les endpoints
- Ordering whiteliste, page_size ≤100
- Logs d’audit et traçabilité Excel
- Exports/rapports fidèles et compressibles
- Docker dev compose et prod-lite
- Tests unitaires/intégration/E2E
- Variables env (DB, EXCEL_ROOT, CORS)
- Résilience I/O et retries
- Monitoring via /api/health

## 7. Modèles de prompts
- Backend Sx — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Frontend Sx — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Charts — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Exports — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Reports — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Notify — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Assistant — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Quality — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …
- Sync — Objectif: … / Fichiers: … / API: … / Tests: … / PR: …

## 8. Checklists
**Avant**
- Mettre à jour branches et dépendances
- Définir env vars (DB, EXCEL_ROOT, CORS)
- Vérifier accès Excel et droits
- Appliquer `python manage.py migrate`
- Préparer secrets JWT/Outlook

**Pendant**
- `pre-commit run`
- `npm run lint` puis `npm run build`
- `python manage.py test`
- Messages de commit clairs
- Si CI indispo, conserver hash commit

**Après**
- Ouvrir PR et vérifier CI
- Tester `/api/health` et parcours clé
- Nettoyer branches fusionnées
- Tagger version / mettre à jour changelog
- Sauvegarder configs et docs

