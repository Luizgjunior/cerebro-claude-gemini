@echo off
rem Script para o Claude chamar o Gemini CLI em modo nao-interativo
rem Uso: gemini-call.bat "instrucao aqui"
rem Nota: usa Python para evitar problemas de quoting do Windows
python C:\Users\Luiz\brain\run_gemini_test.py %*
