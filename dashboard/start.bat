@echo off
title Nexus Dashboard — Claude + Gemini
color 0B

echo.
echo  ================================================
echo   NEXUS DASHBOARD v1.0
echo   Claude (esq)  ^|^|  Gemini (dir)
echo   Cerebro Unico — Single Brain
echo  ================================================
echo.

REM Verifica Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+
    pause & exit /b 1
)

REM Instala dependencias no venv local
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [INFO] Criando ambiente virtual...
    python -m venv "%~dp0.venv"
    echo [INFO] Instalando dependencias...
    "%~dp0.venv\Scripts\pip.exe" install -r "%~dp0requirements.txt" -q
    echo [OK] Dependencias instaladas.
    echo.
)

REM Verifica se NexusSync ja esta rodando
curl -s --max-time 1 http://localhost:7700/ping >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Iniciando NexusSync Bridge na porta 7700...
    start "NexusSync" /min python "C:\Users\Luiz\brain\sync_server.py"
    timeout /t 2 /nobreak >nul
    echo [OK] NexusSync iniciado.
) else (
    echo [OK] NexusSync ja esta ativo na porta 7700.
)

REM Inicia Dashboard
echo [INFO] Iniciando Nexus Dashboard na porta 8080...
echo.
echo  Acesse no browser: http://localhost:8080
echo.
echo  Ctrl+C para encerrar o dashboard.
echo.

REM Abre o browser automaticamente apos 2s
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080"

REM Inicia o servidor (com venv)
"%~dp0.venv\Scripts\python.exe" "%~dp0server.py"

echo.
echo  Dashboard encerrado.
pause
