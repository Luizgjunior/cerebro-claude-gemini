' Inicia o NexusSync Bridge em background (sem janela visível)
' Execute este arquivo para manter o servidor rodando em background
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c python C:\Users\Luiz\brain\sync_server.py > C:\Users\Luiz\brain\server.log 2>&1", 0, False
WScript.Echo "NexusSync Bridge iniciado em background (porta 7700)"
