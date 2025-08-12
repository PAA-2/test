# PAA

![CI](https://github.com/${REPO_OWNER}/${REPO_NAME}/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-ghcr.io%2F${REPO_OWNER}%2F${REPO_NAME}-blue)
![License](https://img.shields.io/badge/license-TBD-lightgrey)

PAA est une application de gestion de plans d'action multi‑sources Excel. Les fichiers Excel sont la **source de vérité** et toutes les écritures passent par eux.

## Sommaire
- [Stack](#stack)
- [Arborescence](#arborescence)
- [Quickstart](#quickstart)
  - [Local](#local)
  - [Docker](#docker)
  - [Docker prod-lite](#docker-prod-lite)
- [Configuration](#configuration)
- [Authentification & rôles](#authentification--rôles)
- [API map](#api-map)
- [Workflow type](#workflow-type)
- [Tests & CI](#tests--ci)
- [Licence](#licence)

## Stack
- Backend : Django + DRF
- Frontend : React 18 + Vite + Tailwind
- Excel : pandas + openpyxl
- PDF : reportlab
- Auth : JWT
- Outlook local : pywin32

## Arborescence
```
backend/   # API Django
frontend/  # React + Vite
excel/     # fichiers Excel source
docker/    # scripts et configs docker
```

## Quickstart

### Local
1. Windows : double‑cliquez `start.bat`.
2. Ou manuellement :
   ```bash
   python manage.py runserver 0.0.0.0:8000
   npm --prefix frontend run dev
   ```
   API : http://localhost:8000/api – Frontend : http://localhost:5173

### Docker
```bash
docker compose --env-file docker/.env.docker up -d --build
```
Placez vos Excel dans `./excel`.

### Docker prod-lite
```bash
docker compose -f docker-compose.prod.yml --env-file docker/.env.prod up -d --build
```
Servez le frontend via Nginx et le backend via Gunicorn. Les fichiers statiques sont collectés dans `staticfiles/`.

## Configuration
Variables principales :
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `EXCEL_ROOT`
- `OUTLOOK_ENABLED`

## Authentification & rôles
| Rôle | Portée |
| --- | --- |
| SuperAdmin | tout accès |
| PiloteProcessus | tous les plans |
| Pilote | plans autorisés |
| Utilisateur | lecture seule |

## API map
| Endpoint | Méthode | Description |
| --- | --- | --- |
| `/auth/login` | POST | login JWT |
| `/plans` | GET/POST/PUT/DELETE | gestion des plans |
| `/actions` | GET/POST/PUT/DELETE | gestion des actions |
| `/actions/{id}/validate` | POST | valider une action |
| `/actions/{id}/close` | POST | clôturer une action |
| `/actions/{id}/reject` | POST | rejeter une action |
| `/sync/run` | POST | lancer la synchronisation Excel↔DB |
| `/dashboard/counters` | GET | KPIs globales |
| `/charts/progress` | GET | évolution mensuelle |
| `/charts/compare-plans` | GET | comparatif par plan |
| `/export/excel` | GET | export Excel filtré |
| `/export/pdf` | GET | export PDF filtré |
| `/reports/custom` | POST | rapport PDF custom |
| `/notify/late` | POST | notification actions en retard |
| `/admin/custom-fields` | CRUD | champs personnalisés |
| `/quality/run` | POST | contrôles qualité des données |
| `/assistant/suggest-closures` | POST | suggestions de clôture |
| `/health` | GET | healthcheck |

## Workflow type
1. Créer un plan via l'UI ou `POST /plans`.
2. Rescanner le plan (`POST /plans/{id}/rescan`).
3. Prévisualiser (`GET /excel/preview?plan=ID`).
4. Créer puis valider ou clôturer une action.
5. Exporter (`GET /export/*`) ou générer un rapport (`POST /reports/custom`).

## Tests & CI
- `python manage.py test`
- `npm --prefix frontend run e2e`
- CI GitHub Actions : lint, tests, build, E2E, Docker images.

## Licence
Licence à définir. Contributions et crédits bienvenus.
