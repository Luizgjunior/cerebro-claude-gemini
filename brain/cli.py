"""
NexusSync CLI — Interface para Claude e Gemini usarem o Brain Server

Uso:
  python cli.py read                          → Lê estado completo
  python cli.py update <agent> <key> <value>  → Atualiza estado
  python cli.py send <from> <message>         → Envia mensagem para o outro agente
  python cli.py messages <agent>              → Ver mensagens pendentes
  python cli.py ack <agent>                   → Marcar mensagens como lidas
  python cli.py log                           → Ver log recente
  python cli.py ping                          → Verificar se servidor está ativo

Exemplos (Gemini):
  python cli.py read
  python cli.py update gemini context "Implementei o endpoint POST /leads"
  python cli.py send gemini "Terminei a Sprint 1. Claude, pode revisar o código?"
  python cli.py messages gemini

Exemplos (Claude):
  python cli.py update claude context "Revisei o código. Aprovado."
  python cli.py send claude "Gemini, iniciar Sprint 2 quando puder"
"""

import io
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Força UTF-8 no terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SERVER = "http://localhost:7700"
BRAIN_FILE = r"C:\Users\Luiz\brain\brain.json"


def req(method, endpoint, data=None):
    url = SERVER + endpoint
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if body else {}
    req_obj = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req_obj, timeout=3) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError:
        return None


def server_online():
    result = req("GET", "/ping")
    return result is not None


def read_local_brain():
    """Fallback: lê brain.json diretamente se servidor offline."""
    import os
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def print_state(state):
    print("\n" + "="*55)
    print("🧠 NEXUSSYNC BRAIN — Estado Atual")
    print("="*55)
    print(f"  Status      : {state.get('status', 'N/A')}")
    print(f"  Atualizado  : {state.get('last_update', 'N/A')}")
    print(f"  Último agente: {state.get('last_agent', 'N/A')}")
    print(f"  Projeto     : {state.get('project', 'N/A')}")
    print(f"\n  Contexto:")
    ctx = state.get("context", "")
    for line in (ctx.split("\n") if ctx else ["Sem contexto"]):
        print(f"    {line}")
    goals = state.get("goals", [])
    if goals:
        print(f"\n  Objetivos ({len(goals)}):")
        for g in goals[-5:]:
            print(f"    • {g}")
    decisions = state.get("decisions", [])
    if decisions:
        print(f"\n  Decisões ({len(decisions)}):")
        for d in decisions[-3:]:
            print(f"    • {d}")
    msgs_g = state.get("messages", {}).get("to_gemini", [])
    msgs_c = state.get("messages", {}).get("to_claude", [])
    if msgs_g:
        print(f"\n  📬 Mensagens para Gemini: {len(msgs_g)}")
    if msgs_c:
        print(f"  📬 Mensagens para Claude: {len(msgs_c)}")
    print("="*55 + "\n")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0].lower()

    # ── ping ──────────────────────────────────────────
    if cmd == "ping":
        if server_online():
            print("✅ NexusSync Bridge online — http://localhost:7700")
        else:
            print("❌ Servidor offline. Execute: start.bat")
        return

    # ── read ──────────────────────────────────────────
    if cmd == "read":
        if server_online():
            state = req("GET", "/state")
        else:
            print("⚠️  Servidor offline — lendo brain.json local...")
            state = read_local_brain()
        if state:
            print_state(state)
        else:
            print("❌ Nenhum estado encontrado.")
        return

    # ── log ───────────────────────────────────────────
    if cmd == "log":
        result = req("GET", "/log")
        if result:
            print("\n📋 Log de Sincronização (últimas entradas):")
            for line in result.get("log", []):
                print(" ", line.strip())
        else:
            print("❌ Servidor offline.")
        return

    # ── update <agent> <key> <value> ──────────────────
    if cmd == "update" and len(args) >= 4:
        agent = args[1]
        key = args[2]
        value = " ".join(args[3:])
        result = req("POST", "/update", {"agent": agent, "key": key, "value": value})
        if result:
            print(f"✅ [{agent}] Atualizado: {key} = {value[:60]}")
        else:
            print("❌ Servidor offline — grave manualmente no CORE_MEMORY.md")
        return

    # ── send <from> <message> ─────────────────────────
    if cmd == "send" and len(args) >= 3:
        from_agent = args[1]
        to_agent = "claude" if from_agent == "gemini" else "gemini"
        content = " ".join(args[2:])
        result = req("POST", "/message", {"from": from_agent, "to": to_agent, "content": content})
        if result:
            print(f"✅ Mensagem enviada de [{from_agent}] → [{to_agent}]")
            print(f"   Conteúdo: {content[:80]}")
        else:
            print("❌ Servidor offline.")
        return

    # ── messages <agent> ──────────────────────────────
    if cmd == "messages" and len(args) >= 2:
        agent = args[1]
        result = req("GET", f"/messages/{agent}")
        if result:
            msgs = result.get("messages", [])
            if msgs:
                print(f"\n📬 Mensagens para [{agent}] ({len(msgs)}):")
                for m in msgs:
                    print(f"  [{m.get('ts','')}] de {m.get('from','?')}: {m.get('content','')}")
                print(f"\n  → Após ler: python cli.py ack {agent}")
            else:
                print(f"✅ Sem mensagens pendentes para [{agent}]")
        else:
            print("❌ Servidor offline.")
        return

    # ── ack <agent> ───────────────────────────────────
    if cmd == "ack" and len(args) >= 2:
        agent = args[1]
        result = req("POST", f"/ack/{agent}")
        if result:
            print(f"✅ {result.get('cleared', 0)} mensagem(ns) marcadas como lidas para [{agent}]")
        else:
            print("❌ Servidor offline.")
        return

    print("Comando não reconhecido. Use: python cli.py --help")


if __name__ == "__main__":
    main()
