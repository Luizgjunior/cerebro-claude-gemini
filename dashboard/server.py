"""
Nexus Dashboard Server v1.0
FastAPI + WebSocket — porta 8080

Endpoints:
  GET  /                    → Serve index.html
  GET  /api/state           → Proxy NexusSync estado
  GET  /api/ping            → Health check
  WS   /ws/claude           → Chat com Claude Code CLI
  WS   /ws/gemini           → Chat com Gemini CLI
"""

import asyncio
import json
import os
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

# ── Constantes ─────────────────────────────────────────────────────────────────

NODE_GEMINI  = r"C:\Users\Luiz\AppData\Roaming\npm\node_modules\@google\gemini-cli\dist\index.js"
NODE_CLAUDE  = r"C:\Users\Luiz\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
NEXUS_URL    = "http://localhost:7700"
WORK_DIR     = r"C:\Users\Luiz"
INDEX_HTML   = Path(__file__).parent / "index.html"

# Linhas de ruído do Node.js para filtrar
NODE_NOISE = ["DEP0040", "punycode", "ExperimentalWarning", "trace-deprecation",
              "DeprecationWarning", "node:"]

def is_noise(text: str) -> bool:
    return any(n in text for n in NODE_NOISE)

# Env para subprocessos — remove CLAUDECODE para evitar conflito de sessão aninhada
def clean_env() -> dict:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["FORCE_COLOR"] = "0"
    env["NO_COLOR"] = "1"
    env["NODE_NO_WARNINGS"] = "1"
    return env


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Nexus Dashboard")


# ── HTTP ───────────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_index():
    return FileResponse(str(INDEX_HTML))


@app.get("/api/state")
async def get_nexus_state():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{NEXUS_URL}/state", timeout=3.0)
            return r.json()
        except Exception:
            return JSONResponse({"error": "NexusSync offline", "status": "offline"}, status_code=503)


@app.get("/api/ping")
async def ping():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{NEXUS_URL}/ping", timeout=2.0)
            return {"nexus": r.json(), "dashboard": "ok"}
        except Exception:
            return {"nexus": "offline", "dashboard": "ok"}


# ── Streaming Helpers ──────────────────────────────────────────────────────────

async def stream_gemini(prompt: str, ws: WebSocket, conv_id: str):
    """Executa Gemini CLI e faz streaming por chunks."""
    cmd = ["node", NODE_GEMINI, "--yolo", "--output-format", "text", "--prompt", prompt]
    await _stream_subprocess(cmd, ws, conv_id, "gemini")


async def stream_claude(prompt: str, ws: WebSocket, conv_id: str):
    """
    Executa Claude CLI com --output-format stream-json para streaming real.
    Cada linha do stdout é um JSON: {"type":"assistant","message":{"content":[{"type":"text","text":"..."}]}}
    """
    cmd = [
        "node", NODE_CLAUDE,
        "-p",
        "--output-format", "stream-json",
        "--dangerously-skip-permissions",
        prompt,
    ]
    await _stream_subprocess(cmd, ws, conv_id, "claude", parse_stream_json=True)


async def _stream_subprocess(cmd: list, ws: WebSocket, conv_id: str, agent: str,
                              parse_stream_json: bool = False):
    """
    Executa subprocess assincrono e envia tokens via WebSocket.

    parse_stream_json=True → interpreta cada linha como JSON (formato Claude stream-json)
    parse_stream_json=False → envia texto bruto linha por linha (Gemini text)
    """
    proc = None
    try:
        await ws.send_json({"type": "status", "content": "Aguardando resposta...",
                            "conversation_id": conv_id})

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORK_DIR,
            env=clean_env(),
        )

        # Lê stdout linha por linha
        async for line_bytes in proc.stdout:
            line = line_bytes.decode("utf-8", errors="replace")

            if is_noise(line):
                continue

            stripped = line.strip()
            if not stripped:
                continue

            if parse_stream_json:
                # Formato stream-json do Claude: extrai texto dos eventos
                text = _extract_claude_token(stripped)
                if text:
                    await ws.send_json({"type": "token", "content": text,
                                        "conversation_id": conv_id})
            else:
                # Gemini text puro — envia a linha inteira
                await ws.send_json({"type": "token", "content": line,
                                    "conversation_id": conv_id})

        await proc.wait()

        # Verifica erros reais no stderr
        if proc.returncode not in (0, None):
            stderr_raw = await proc.stderr.read()
            stderr_text = stderr_raw.decode("utf-8", errors="replace")
            real_errors = [l for l in stderr_text.splitlines()
                           if l.strip() and not is_noise(l)]
            if real_errors:
                await ws.send_json({"type": "error",
                                    "content": "\n".join(real_errors[:5]),
                                    "conversation_id": conv_id})

        await ws.send_json({"type": "done", "content": "", "conversation_id": conv_id})

    except asyncio.CancelledError:
        if proc and proc.returncode is None:
            proc.terminate()
        raise
    except Exception as exc:
        await ws.send_json({"type": "error", "content": str(exc),
                            "conversation_id": conv_id})
        await ws.send_json({"type": "done", "content": "",
                            "conversation_id": conv_id})


def _extract_claude_token(line: str) -> str:
    """
    Extrai texto de uma linha stream-json do Claude CLI.
    Formatos conhecidos:
      {"type":"assistant","message":{"content":[{"type":"text","text":"Olá"}],...}}
      {"type":"text","text":"token"}
      {"type":"content_block_delta","delta":{"type":"text_delta","text":"token"}}
    """
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        # Linha não é JSON válido (ex: texto puro no final) — retorna direto
        return line if line.strip() else ""

    t = obj.get("type", "")

    # Evento de texto direto
    if t == "text":
        return obj.get("text", "")

    # Evento de bloco de conteúdo (streaming de tokens)
    if t == "content_block_delta":
        delta = obj.get("delta", {})
        if delta.get("type") == "text_delta":
            return delta.get("text", "")

    # Mensagem completa do assistente (fallback)
    if t == "assistant":
        message = obj.get("message", {})
        content = message.get("content", [])
        texts = [c.get("text", "") for c in content if c.get("type") == "text"]
        return "".join(texts)

    # Resultado final com campo "result"
    if t == "result":
        return obj.get("result", "")

    return ""


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws/{agent}")
async def ws_agent(websocket: WebSocket, agent: str):
    if agent not in ("claude", "gemini"):
        await websocket.close(code=4004)
        return

    await websocket.accept()
    active_tasks: set[asyncio.Task] = set()

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") != "prompt":
                continue

            prompt = data.get("content", "").strip()
            conv_id = data.get("conversation_id", str(uuid.uuid4()))

            if not prompt:
                continue

            # Lança streaming como task assíncrona (não bloqueia o loop)
            if agent == "gemini":
                coro = stream_gemini(prompt, websocket, conv_id)
            else:
                coro = stream_claude(prompt, websocket, conv_id)

            task = asyncio.create_task(coro)
            active_tasks.add(task)
            task.add_done_callback(active_tasks.discard)

    except WebSocketDisconnect:
        for task in active_tasks:
            task.cancel()
    except Exception:
        for task in active_tasks:
            task.cancel()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("""
+--------------------------------------------------+
|  Nexus Dashboard v1.0                            |
|  Claude (esq) <-> Gemini (dir)                   |
|  Acesse: http://localhost:8080                   |
+--------------------------------------------------+
""")
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8080,
        reload=False,
        log_level="warning",
    )
