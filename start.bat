@echo off
setlocal
title PAA — Dev Launcher

REM Dossiers
set ROOT=%~dp0
set BACKEND=%ROOT%
set FRONTEND=%ROOT%frontend

REM 1) Python venv + deps
if not exist "%BACKEND%.venv\Scripts\activate.bat" (
  echo [PAA] Creation du venv Python...
  py -3 -m venv "%BACKEND%.venv"
)
call "%BACKEND%.venv\Scripts\activate.bat"
python -V

echo [PAA] Installation dependances backend...
if exist "%BACKEND%requirements.txt" (
  pip install --upgrade pip
  pip install -r "%BACKEND%requirements.txt"
) else (
  pip install --upgrade pip
  pip install django djangorestframework djangorestframework-simplejwt django-filter pandas openpyxl reportlab django-cors-headers
)

REM 2) Migrations + runserver
cd /d "%BACKEND%"
echo [PAA] Django migrate...
python manage.py migrate

echo [PAA] Demarrage du backend sur http://localhost:8000 ...
start "PAA Backend" cmd /k "cd /d %BACKEND% && python manage.py runserver 0.0.0.0:8000"

REM 3) Frontend (Vite)
if not exist "%FRONTEND%" (
  echo [PAA] Dossier frontend introuvable: %FRONTEND%
  goto :end
)
cd /d "%FRONTEND%"
if not exist "node_modules" (
  echo [PAA] Installation dependances frontend (npm install)...
  call npm install
)
if not exist ".env.local" (
  echo VITE_API_URL=http://localhost:8000/api> .env.local
)

echo [PAA] Demarrage du frontend sur http://localhost:5173 ...
start "PAA Frontend" cmd /k "cd /d %FRONTEND% && npm run dev"

echo.
echo [PAA] Tout est lance. Backend : http://localhost:8000  /  Frontend : http://localhost:5173
echo [PAA] Fermez cette fenetre ou utilisez les deux consoles ouvertes pour stopper.
:end
endlocal
