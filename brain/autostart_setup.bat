@echo off
echo Configurando NexusSync Bridge para iniciar automaticamente com o Windows...

REM Adiciona ao agendador de tarefas do Windows para iniciar no login
schtasks /create /tn "NexusSyncBridge" /tr "wscript.exe C:\Users\Luiz\brain\start_hidden.vbs" /sc onlogon /ru "%USERNAME%" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] NexusSync Bridge configurado para iniciar automaticamente!
    echo      Ele rodará em background toda vez que o Windows iniciar.
    echo.
    echo      Para iniciar agora: wscript.exe C:\Users\Luiz\brain\start_hidden.vbs
) else (
    echo.
    echo [AVISO] Falha ao criar tarefa agendada. Execute como Administrador.
)

pause
