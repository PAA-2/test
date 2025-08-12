# TROUBLESHOOTING

## Sommaire
- [Auth 401/403](#auth-401403)
- [CORS](#cors)
- [Excel introuvable](#excel-introuvable)
- [Erreurs pandas/openpyxl](#erreurs-pandasopenpyxl)
- [Outlook indisponible](#outlook-indisponible)
- [Exports PDF](#exports-pdf)
- [Nginx 502/504](#nginx-502504)
- [PostgreSQL](#postgresql)
- [Rate limit 429](#rate-limit-429)
- [Build Frontend/Vite](#build-frontendvite)
- [E2E Playwright](#e2e-playwright)

## Auth 401/403
Token expiré ou rôle insuffisant. Reconnectez-vous (`/login`).

## CORS
Vérifier `CORS_ALLOWED_ORIGINS` côté backend et l’URL du frontend.

## Excel introuvable
Chemin invalide ou `EXCEL_ROOT` absent. Utiliser chemins relatifs depuis `./excel`.

## Erreurs pandas/openpyxl
Types invalides (dates, nombres). Nettoyer les cellules ou appliquer une coercition dans Excel.

## Outlook indisponible
`pywin32` manquant ou machine non-Windows. L’API renvoie 503.

## Exports PDF
Police manquante : installer fonts ou vérifier reportlab. 

## Nginx 502/504
Timeout backend. Augmenter `proxy_read_timeout` ou vérifier migrations.

## PostgreSQL
Variables `DATABASE_URL` incorrectes ou service non démarré. Utiliser `docker compose logs db`.

## Rate limit 429
Trop de requêtes : attendre ou augmenter les seuils (`DEFAULT_THROTTLE_RATES`).

## Build Frontend/Vite
`VITE_API_URL` manquant. Vérifier `.env.local` ou `--env-file` docker.

## E2E Playwright
Installer les dépendances (`npm run e2e:install`), définir `E2E_BASE_URL`, s’assurer des ports disponibles.
