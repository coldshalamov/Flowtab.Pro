@echo off
echo 🚀 Starting Flowtab.Pro Development Environment...

REM --- BACKEND SETUP CHECK ---
if not exist "apps\api\venv" (
    echo [INFO] First time setup detected. Creating Python virtual environment...
    cd apps\api
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Is Python installed and in your PATH?
        pause
        exit /b
    )
    
    echo [INFO] Installing dependencies...
    call venv\Scripts\activate
    pip install -r requirements.txt
    
    echo [INFO] Setting up database...
    if not exist .env copy .env.example .env
    
    REM Run migrations from root to avoid import errors
    cd ..\..
    set PYTHONPATH=%CD%
    apps\api\venv\Scripts\python -m alembic -c apps/api/alembic.ini upgrade head
    apps\api\venv\Scripts\python apps/api/seed.py
    
    echo [SUCCESS] Backend setup complete!
)

REM --- STARTUP ---

REM Start Backend (API)
echo 📦 Launching Backend API (Port 8000)...
REM We run from ROOT so that 'apps.api' imports work
start "Flowtab API" powershell -NoExit -Command "$env:PYTHONPATH='.'; .\apps\api\venv\Scripts\activate; uvicorn apps.api.main:app --reload"

REM Start Frontend (Web)
echo 🎨 Launching Frontend Web App (Port 3000)...
REM Check if node_modules exists, install if not
if not exist "apps\web\node_modules" (
    echo [INFO] Installing Frontend dependencies...
    cd apps\web
    call npm install
    cd ..\..
)

start "Flowtab Web" powershell -NoExit -Command "cd apps/web; npm run dev"

echo.
echo ✅ Services starting!
echo    - Frontend: http://localhost:3000
echo    - Backend:  http://localhost:8000/docs
echo.
pause
