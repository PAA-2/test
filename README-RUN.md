# PAA — Lancement local (Windows)

## Prerequis
- Python 3.11+  (commande `py -3 --version`)
- Node 18+      (commande `node -v`)

## 1-clic
- Double-cliquez `start.bat`
- Backend: http://localhost:8000  |  Frontend: http://localhost:5173

## Variables d'environnement
- Frontend: `frontend/.env.local` => `VITE_API_URL=http://localhost:8000/api`
- Backend (si besoin CORS): ajoutez dans `settings.py`:
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", *MIDDLEWARE]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]

## Commandes utiles
- Backend: `\.venv\Scripts\activate && python manage.py runserver`
- Frontend: `cd frontend && npm run dev`

## Depannage
- Si l'API renvoie 401: connectez-vous puis re-essayez (S4 gère le refresh token).
- Si CORS: vérifiez `django-cors-headers` et `CORS_ALLOWED_ORIGINS`.
- Si les exports PDF: assurez-vous que `reportlab` est bien installe.
- Si notifications Outlook: installez `pywin32` sur Windows avec Outlook.
