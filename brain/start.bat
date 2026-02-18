@echo off
title NexusSync Bridge — Claude ^<-^> Gemini
color 0A

echo.
echo  ============================================
echo   🧠 NexusSync Bridge — Cerebro Unico
echo   Claude Code ^<--^> Gemini CLI
echo  ============================================
echo.

REM Verifica se Python existe
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale o Python 3.8+
    pause
    exit /b 1
)

echo  Iniciando servidor na porta 7700...
echo  Pressione Ctrl+C para encerrar.
echo.

python C:\Users\Luiz\brain\sync_server.py

pause
