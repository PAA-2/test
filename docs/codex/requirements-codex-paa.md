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
PAA est une application intranet de gestion de plans d’action où les fichiers Excel restent la source de vérité. Les actions possèdent un identifiant ACT‑XXXX unique et des informations PDCA. Le backend Django + DRF communique avec une DB PostgreSQL portable et manipule les Excel via pandas/openpyxl. Le frontend React + Vite + Tailwind gère authentification JWT et rôles (SuperAdmin, PiloteProcessus, Pilote, Utilisateur). Exports PDF avec reportlab et notifications locales Outlook sont possibles. Les opérations lisent et réécrivent toujours les lignes Excel correspondantes avant ré‑ingestion.

## 2. Architecture & Dossiers
- backend/ : Django + DRF
- frontend/ : React + Vite
- excel/ : sources Excel
- docker/ : compose & scripts
- docs/ : documentation
- start.bat : lanceur Windows
- requirements.txt / pyproject.toml
- README.md / RUNBOOK.md / TROUBLESHOOTING.md
- .github/workflows/ci.yml

## 3. Endpoints essentiels
- POST /auth/login — login
- POST /auth/refresh — refresh token
- GET /users/me — profil
- GET/POST/PUT/DELETE /plans — plans
- POST /plans/{id}/rescan — relire Excel
- GET /excel/preview — aperçu 10 lignes
- GET/POST/PUT/DELETE /actions — actions
- POST /actions/{id}/validate|close|reject|assign
- POST /sync/run — sync Excel↔DB
- GET /sync/status — état sync
- GET /dashboard/counters — KPIs
- GET /charts/progress — création/clôture mensuelle
- GET /charts/compare-plans — comparatif plans
- GET /export/excel|pdf — exports filtrés
- POST /reports/custom — rapport PDF
- POST /notify/late|summary|custom — notifications Outlook
- CRUD /admin/custom-fields — champs perso
- POST /quality/run — contrôles qualité
- POST /assistant/suggest-closures|prioritize|summarize
- GET /health — healthcheck

## 4. Règles métier
- Excel = source de vérité
- ACT‑ID unique ACT‑0001…
- Multi‑occurrences gérées par stratégie
- Toute écriture cible `excel_row_index`
- PDCA : validation coche C et A
- Champ J = `delais - aujourd’hui`
- Responsables séparés par `,` ou `;`
- Filtres identiques liste/exports
- Rôles limitent portée des plans
- Export/rapport utilisent même périmètre
- Throttle 120/min par user
- Cache charts 60 s

## 5. Modules
1–10 : Utilisateurs, rôles, paramètres, plans, ACT‑ID, traçabilité, audit, sécurité, backups.
11–20 : CRUD actions/plans, multi‑responsables, workflow, filtres, consolidé, historique.
21–30 : Planificateur sync, conflits, dry‑run, journal, perf.
31–40 : Export Excel/PDF, rapports, diffusion, archives, comparatifs, qualité données.
41–50 : Layout, thèmes, formulaires, tableaux filtrables, graphiques, modales, i18n.
51–60 : Champs perso, validations, modèles, automations, form/list builder, notif rules.
61–70 : Générateur test, Outlook, watcher, verrouillage, résilience I/O, hashing, compression.
71–80 : Index DB, cache, batch writer, profiling, monitoring, rate limit, cleanup, tests.
81–90 : Assistante locale, recommandations, préremplissage, rappels, journal.
91–100 : Gouvernance, conformité, anonymisation, audits, continuité.

## 6. Critères globaux
- Respect des rôles et filtres
- Écritures Excel avant DB
- ACT‑ID unique et traçabilité
- PDCA cohérent
- Exports identiques à la liste
- Endpoints sécurisés JWT
- Throttling actif
- Cache charts
- Logs structurés
- Tests unitaires et E2E
- Docker prêt prod/dev
- Documentation à jour

## 7. Modèles de prompts
**Backend Sx**
- Objectif : …
- Fichiers : …
- API : …
- Tests : …
- PR : …

**Frontend Sx**
- Objectif : …
- Fichiers : …
- API : …
- Tests : …
- PR : …

**Charts** idem.

**Exports** idem.

**Reports** idem.

**Notify** idem.

## 8. Checklists
- **Avant** : env vars, dépendances, branches à jour
- **Pendant** : `pre-commit run`, `python manage.py test`, `npm run build`
- **Après** : commit, push, PR ou SHA si PR échoue
