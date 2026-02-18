"""
NexusSync — Chama o Gemini CLI com um prompt arbitrario.

Uso:
  python run_gemini_test.py "instrucao aqui"

  Sem argumentos: executa o teste padrao do NexusSync.
"""
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

NODE_GEMINI = r"C:\Users\Luiz\AppData\Roaming\npm\node_modules\@google\gemini-cli\dist\index.js"

# Prompt passado como argumento ou prompt de teste padrao
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
else:
    prompt = (
        "Execute em sequencia estes 4 comandos Python usando a ferramenta shell disponivel "
        "e mostre o output de cada um:\n"
        "(1) python C:\\Users\\Luiz\\brain\\cli.py ping\n"
        "(2) python C:\\Users\\Luiz\\brain\\cli.py read\n"
        "(3) python C:\\Users\\Luiz\\brain\\cli.py update gemini context \"Gemini conectado ao NexusSync. Teste OK.\"\n"
        "(4) python C:\\Users\\Luiz\\brain\\cli.py send gemini \"Ola Claude! Gemini aqui. Cerebro Unico sincronizado.\"\n"
        "Confirme que o NexusSync Bridge esta funcionando."
    )

result = subprocess.run(
    ["node", NODE_GEMINI, "--yolo", "--output-format", "text", "--prompt", prompt],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=r"C:\Users\Luiz",
    timeout=120,
)

if result.stdout:
    print(result.stdout)
if result.returncode != 0 and result.stderr:
    # Filtra o aviso de deprecacao do punycode
    errs = [l for l in result.stderr.splitlines() if "DEP0040" not in l and "punycode" not in l and "trace-deprecation" not in l]
    if errs:
        print("STDERR:", "\n".join(errs[:10]))
