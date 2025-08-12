# PAA — Lancement local (Windows)

## Prerequis
- Python 3.11+  (commande `py -3 --version`)
- Node 18+      (commande `node -v`)

## 1-clic
- Double-cliquez `start.bat`
- Backend: http://localhost:8000  |  Frontend: http://localhost:5173

## Docker (dev)
- Placez vos fichiers Excel dans `./excel/`
- `docker compose --env-file docker/.env.docker up -d --build`
- API: http://localhost:8000  |  Frontend: http://localhost:5173
- Logs: `docker compose logs -f backend` (ou `frontend`, `db`)

## Variables d'environnement
- Frontend: `frontend/.env.local` => `VITE_API_URL=http://localhost:8000/api`
- Backend (si besoin CORS): ajoutez dans `settings.py`:
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", *MIDDLEWARE]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]

## Commandes utiles
- Backend: `\.venv\Scripts\activate && python manage.py runserver`
- Frontend: `cd frontend && npm run dev`

### Migration des chemins Excel
Copiez vos fichiers existants dans `./excel/` et utilisez des `excel_path` relatifs (ex: `F-ELK-494 Plan HSE.xlsx`). Le backend les préfixe avec `EXCEL_ROOT`.

## Depannage
- Si l'API renvoie 401: connectez-vous puis re-essayez (S4 gère le refresh token).
- Si CORS: vérifiez `django-cors-headers` et `CORS_ALLOWED_ORIGINS`.
- Si les exports PDF: assurez-vous que `reportlab` est bien installe.
- Si notifications Outlook: installez `pywin32` sur Windows avec Outlook.
