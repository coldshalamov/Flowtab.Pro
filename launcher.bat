@echo off
title Flowtab.Pro Launcher
cd /d "D:\GitHub\Flowtab.Pro"
echo Starting Flowtab.Pro on port 3014...
echo.
npm --version >nul 2>&1
if errorlevel 1 (
echo ERROR: npm is not installed or not in PATH.
pause
exit /b 1
)
npm run dev -- --port 3014
pause
