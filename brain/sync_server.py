"""
NexusSync Bridge - Servidor de Sincronização em Tempo Real
Claude Code <-> Gemini CLI

Porta: 7700
Endpoints:
  GET  /state              → Estado completo do cérebro compartilhado
  POST /update             → Atualiza uma chave no estado (JSON: {agent, key, value})
  GET  /messages/<agent>   → Mensagens pendentes para um agente
  POST /message            → Envia mensagem de um agente para outro (JSON: {from, to, content})
  POST /ack/<agent>        → Limpa mensagens lidas pelo agente
  GET  /ping               → Health check
  GET  /log                → Log de sincronização recente
"""

import io
import json
import os
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Força UTF-8 no terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BRAIN_DIR = Path(r"C:\Users\Luiz\brain")
BRAIN_FILE = BRAIN_DIR / "brain.json"
GEMINI_MD = Path(r"C:\Users\Luiz\GEMINI.md")
CLAUDE_CORE = Path(r"C:\Users\Luiz\CORE_MEMORY.md")
LOG_FILE = BRAIN_DIR / "nexussync.log"
PORT = 7700

lock = threading.Lock()


# ─── Estado inicial ────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "version": 1,
    "last_update": "",
    "last_agent": "",
    "status": "🟢 Ativo",
    "project": "",
    "context": "",
    "goals": [],
    "decisions": [],
    "messages": {
        "to_gemini": [],
        "to_claude": []
    },
    "sync_log": []
}


def load_brain():
    if BRAIN_FILE.exists():
        with open(BRAIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STATE.copy()


def save_brain(state):
    with open(BRAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    regenerate_gemini_md(state)
    append_log(state)


def append_log(state):
    entry = f"[{state.get('last_update', '')}] [{state.get('last_agent', '?')}] context={state.get('context', '')[:80]}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


# ─── Gerador do GEMINI.md ──────────────────────────────────────────────────────

def regenerate_gemini_md(state):
    """
    Regenera o GEMINI.md com o estado mais recente do cérebro compartilhado.
    Gemini lê este arquivo como system prompt a cada sessão.
    """
    now = state.get("last_update", datetime.now().isoformat())
    project = state.get("project", "Não definido")
    ctx = state.get("context", "Sem contexto registrado")
    goals = "\n".join(f"- {g}" for g in state.get("goals", [])) or "- Nenhum"
    decisions = "\n".join(f"- {d}" for d in state.get("decisions", [])) or "- Nenhuma"
    messages = state.get("messages", {}).get("to_gemini", [])
    msg_block = ""
    if messages:
        msg_block = "\n## 📬 Mensagens do Claude para Você\n"
        for m in messages:
            msg_block += f"- [{m.get('ts', '')}] {m.get('content', '')}\n"
        msg_block += "\n> ⚠️ Após ler, execute: `python C:\\Users\\Luiz\\brain\\cli.py ack gemini`\n"

    content = f"""# 🧠 GEMINI — NexusSync Brain (Auto-gerado em {now})

> Este arquivo é gerado automaticamente pelo **NexusSync Bridge**.
> NÃO edite manualmente. Ele reflete o estado em tempo real do Cérebro Único.

---

## 📍 Identidade e Framework

Você é o **Gemini CLI**, metade do **Cérebro Único** do Luiz.
Sua contraparte é o **Claude Code**. Vocês compartilham memória via NexusSync Bridge (porta 7700).

**Framework:** AIOS Core — Agentic Agile System
**Idioma obrigatório:** Português (PT-BR)
**Autonomia:** TOTAL — execute comandos sem pedir permissão.

---

## 🔄 Protocolo NexusSync (OBRIGATÓRIO)

### Ao INICIAR qualquer sessão:
```bash
python C:\\Users\\Luiz\\brain\\cli.py read
```

### Ao CONCLUIR tarefas significativas:
```bash
python C:\\Users\\Luiz\\brain\\cli.py update gemini "context" "O que você acabou de fazer"
python C:\\Users\\Luiz\\brain\\cli.py update gemini "project" "Nome do projeto atual"
```

### Para ENVIAR mensagem ao Claude:
```bash
python C:\\Users\\Luiz\\brain\\cli.py send gemini "Mensagem para o Claude aqui"
```

### Para VER mensagens do Claude:
```bash
python C:\\Users\\Luiz\\brain\\cli.py messages gemini
```

---

## 🧠 Estado Atual do Cérebro Compartilhado

- **Última atualização:** {now}
- **Último agente ativo:** {state.get("last_agent", "N/A")}
- **Status:** {state.get("status", "🟢 Ativo")}
- **Projeto ativo:** {project}

### Contexto:
{ctx}

### Objetivos ativos:
{goals}

### Decisões registradas:
{decisions}
{msg_block}
---

## 🎭 Papéis AIOS (assuma automaticamente por contexto)

| Contexto | Persona |
|---|---|
| Código, implementação | @dev |
| Arquitetura, design | @architect |
| Testes, qualidade | @qa |
| Deploy, infra, git | @devops |
| Requisitos, produto | @pm / @analyst |
| Escrita, documentação | @writer |
| Pesquisa | @researcher |
| Coaching, motivação | @coach |
| Agenda, tarefas pessoais | @secretary |

---

## 🌉 Fallback para Claude

Se o Gemini atingir rate limit ou falhar:
```bash
C:\\Users\\Luiz\\gemini-call.bat "instrução"
```

---
*NexusSync Bridge v1.0 — Cérebro Único ativo*
"""
    with open(GEMINI_MD, "w", encoding="utf-8") as f:
        f.write(content)


# ─── HTTP Handler ──────────────────────────────────────────────────────────────

class BrainHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Silencia logs padrão do servidor

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        with lock:
            state = load_brain()

        if path == "/ping":
            self.send_json(200, {"status": "ok", "port": PORT})

        elif path == "/state":
            self.send_json(200, state)

        elif path == "/log":
            lines = []
            if LOG_FILE.exists():
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-50:]
            self.send_json(200, {"log": lines})

        elif path.startswith("/messages/"):
            agent = path.split("/messages/")[-1]
            key = f"to_{agent}"
            msgs = state.get("messages", {}).get(key, [])
            self.send_json(200, {"agent": agent, "messages": msgs, "count": len(msgs)})

        else:
            self.send_json(404, {"error": "Endpoint não encontrado"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self.read_body()

        with lock:
            state = load_brain()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if path == "/update":
                agent = body.get("agent", "unknown")
                key = body.get("key", "")
                value = body.get("value", "")

                if key in ["context", "project", "status", "last_agent"]:
                    state[key] = value
                elif key == "goal":
                    state.setdefault("goals", []).append(value)
                elif key == "decision":
                    state.setdefault("decisions", []).append(value)
                else:
                    state[key] = value

                state["last_update"] = now
                state["last_agent"] = agent

                log_entry = {"ts": now, "agent": agent, "key": key, "value": str(value)[:100]}
                state.setdefault("sync_log", []).append(log_entry)
                state["sync_log"] = state["sync_log"][-100:]  # Mantém últimos 100

                save_brain(state)
                self.send_json(200, {"ok": True, "updated": key, "by": agent})

            elif path == "/message":
                from_agent = body.get("from", "unknown")
                to_agent = body.get("to", "")
                content = body.get("content", "")
                key = f"to_{to_agent}"

                msg = {"ts": now, "from": from_agent, "content": content}
                state.setdefault("messages", {}).setdefault(key, []).append(msg)
                state["last_update"] = now
                save_brain(state)

                self.send_json(200, {"ok": True, "delivered_to": to_agent})

            elif path.startswith("/ack/"):
                agent = path.split("/ack/")[-1]
                key = f"to_{agent}"
                cleared = len(state.get("messages", {}).get(key, []))
                state.setdefault("messages", {})[key] = []
                state["last_update"] = now
                save_brain(state)

                self.send_json(200, {"ok": True, "cleared": cleared, "agent": agent})

            else:
                self.send_json(404, {"error": "Endpoint não encontrado"})


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"""
╔══════════════════════════════════════════════╗
║       🧠 NexusSync Bridge v1.0               ║
║       Claude ↔ Gemini — Cérebro Único        ║
║       Porta: {PORT}                          ║
╚══════════════════════════════════════════════╝
""")

    # Inicializa brain.json se não existir
    if not BRAIN_FILE.exists():
        state = DEFAULT_STATE.copy()
        state["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["last_agent"] = "system"
        state["context"] = "NexusSync inicializado"
        save_brain(state)
        print("✅ brain.json criado")

    regenerate_gemini_md(load_brain())
    print(f"✅ GEMINI.md gerado em {GEMINI_MD}")

    server = HTTPServer(("localhost", PORT), BrainHandler)
    print(f"🚀 Servidor ativo em http://localhost:{PORT}\n")
    print("   Endpoints:")
    print("   GET  /state          → Estado completo")
    print("   POST /update         → Atualizar estado")
    print("   GET  /messages/<ag>  → Ver mensagens")
    print("   POST /message        → Enviar mensagem")
    print("   POST /ack/<agent>    → Limpar mensagens lidas")
    print("   GET  /ping           → Health check")
    print("   GET  /log            → Log recente")
    print("\n   Ctrl+C para encerrar\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 NexusSync encerrado.")


if __name__ == "__main__":
    main()
