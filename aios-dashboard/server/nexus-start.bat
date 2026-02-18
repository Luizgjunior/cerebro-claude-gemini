@echo off
title Nexus Core
cd C:\Users\Luiz\aios-dashboard\server
start /b node server.js
timeout /t 2 >nul
start http://localhost:3001
echo Nexus Dashboard iniciado com sucesso!
exit
