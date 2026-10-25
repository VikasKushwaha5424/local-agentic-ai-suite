@echo off
title Enterprise HR Policy Agent (Port 8050)
echo ======================================================================
echo  STARTING ENTERPRISE HR POLICY AGENT WEB PORTAL
echo  Port: 8050 (100% Local Ollama)
echo ======================================================================
echo.

curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Starting local Ollama service...
    start /b ollama serve >nul 2>&1
    timeout /t 2 /nobreak >nul
)

python web.py
pause
