"""Hook PreToolUse de Claude Code (.claude/settings.json): las dos puertas que no dependen de la memoria de nadie.

1. **Render final sólo con QA aprobado.** Bloquea crear o cambiar un trabajo de render final (jobs/render2d/*.json
   o jobs/render-final/*.json) o lanzar esos workflows, si studio/episodios/<ep>/qa/qa.json no dice "aprobado": true
   o si las fuentes del episodio cambiaron después del QA (la huella no calza). qa.json lo escribe sólo
   tools/qa_video.py: escribirlo a mano está bloqueado.
2. **Metricool sólo con el OK de Tomás para ese post.** Bloquea crear o cambiar un post programado si no existe
   studio/ok/<ep>-<red>.ok para cada red del post (lo crea Tomás con tools/ok.sh; a Claude se le bloquea crearlo).
   Mandar un post a borrador (draft: true) sí se permite: es la forma de despublicar rápido.

Salida: código 2 + mensaje en stderr = bloqueado (Claude Code se lo muestra a Claude). Código 0 = pasa.
"""
import json, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RENDER_DIRS = ("jobs/render2d/", "jobs/render-final/")
RENDER_WORKFLOWS = ("render-2d", "render-final")
PUBLICAR = re.compile(r"(createScheduledPost|updateScheduledPost|createScheduledPostForReview|sendScheduledPostForReview"
                      r"|vidiq_instagram_publish_reel|vidiq_social_post_publish)$")
REDES = ("youtube", "instagram", "tiktok")


def bloquear(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def qa_ok(ep):
    q = RAIZ / "studio/episodios" / ep / "qa/qa.json"
    if not q.exists():
        return f"no hay QA del episodio {ep} (falta {q.relative_to(RAIZ)}). Corre la skill qa-video primero."
    d = json.load(open(q))
    if not d.get("aprobado"):
        return f"el QA de {ep} no está aprobado ({q.relative_to(RAIZ)}). Arregla los bloqueantes y vuelve a pasarlo."
    actual = subprocess.run([sys.executable, str(RAIZ / "tools/qa_video.py"), "huella", ep], capture_output=True, text=True).stdout.strip()
    if actual != d.get("huella_fuentes"):
        return f"las fuentes de {ep} cambiaron después del QA (guion, voz, sonido o escena): vuelve a pasar el QA."
    return None


def ep_de_trabajo(texto):
    try:
        return json.loads(texto).get("episodio")
    except Exception:
        m = re.search(r'"episodio"\s*:\s*"([^"]+)"', texto or "")
        return m.group(1) if m else None


def revisar_render(tool, inp):
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        ruta = str(inp.get("file_path", ""))
        if ruta.endswith("/qa/qa.json") or ruta.endswith("qa/qa.json"):
            bloquear("qa.json lo escribe sólo tools/qa_video.py cerrar <ep>; no se edita a mano.")
        if any(d in ruta for d in RENDER_DIRS):
            contenido = inp.get("content") or ""
            if not contenido and Path(ruta).exists():
                contenido = Path(ruta).read_text()
            if tool == "Edit":
                contenido = (Path(ruta).read_text() if Path(ruta).exists() else "") + inp.get("new_string", "")
            ep = ep_de_trabajo(contenido)
            if not ep:
                bloquear("el trabajo de render no dice \"episodio\": no se puede revisar su QA.")
            err = qa_ok(ep)
            if err:
                bloquear("Render final bloqueado: " + err)
    if tool == "Bash":
        cmd = inp.get("command", "")
        if "qa/qa.json" in cmd and "tools/qa_video.py" not in cmd and re.search(r"(>|tee|cp |mv |sed -i|python3? -c)", cmd):
            bloquear("qa.json lo escribe sólo tools/qa_video.py cerrar <ep>.")
        if any(d in cmd for d in RENDER_DIRS) and re.search(r"(>|tee |cp |mv |cat <<|printf|echo )", cmd):
            bloquear("Los trabajos de render final se crean con Write (así el hook revisa el QA), no con la terminal.")
        m = re.search(r"gh workflow run\s+(\S+)(.*)", cmd)
        if m and any(w in m.group(1) for w in RENDER_WORKFLOWS):
            t = re.search(r"trabajo=(\S+)", m.group(2))
            ruta = RAIZ / t.group(1) if t else None
            ep = ep_de_trabajo(ruta.read_text()) if ruta and ruta.exists() else None
            if not ep:
                bloquear("No puedo saber el episodio de ese render: pasa -f trabajo=jobs/... con un JSON que diga \"episodio\".")
            err = qa_ok(ep)
            if err:
                bloquear("Render final bloqueado: " + err)


def revisar_ok(tool, inp):
    # nadie más que Tomás crea OKs
    if tool in ("Write", "Edit", "MultiEdit") and "studio/ok/" in str(inp.get("file_path", "")) and not str(inp.get("file_path", "")).endswith("README.md"):
        bloquear("Los OK los crea sólo Tomás con tools/ok.sh en su terminal. Pídeselo.")
    if tool == "Bash":
        cmd = inp.get("command", "")
        if "tools/ok.sh" in cmd or re.search(r"studio/ok/\S*\.ok", cmd) and re.search(r"(>|tee|cp |mv |touch|printf|echo )", cmd):
            bloquear("Los OK los crea sólo Tomás con tools/ok.sh en su terminal. Pídeselo.")
    if PUBLICAR.search(tool):
        info = inp.get("info", inp)
        if isinstance(info, str):
            try:
                info = json.loads(info)
            except Exception:
                info = {"_texto": info}
        if isinstance(info, dict) and str(info.get("draft", "")).lower() == "true":
            return  # mandar a borrador siempre se puede
        texto = json.dumps(inp, ensure_ascii=False)
        eps = set(re.findall(r"/download/(ep\d+[a-z]?)/", texto)) or set(re.findall(r"\b(ep\d{2,3}[a-z]?)\b", texto))
        redes = []
        if isinstance(info, dict):
            redes = [str(x.get("network", "")).lower() for x in info.get("providers", []) if isinstance(x, dict)]
        redes = [r for r in REDES if r in redes or re.search(rf'\\?"{r}\\?"|{r}data', texto.lower())]
        if "vidiq_" in tool:
            redes = redes or ["instagram"]
        if not eps or not redes:
            bloquear("No puedo saber a qué episodio o red corresponde este post (el video tiene que venir del Release epNN). "
                     "Sin eso no hay forma de revisar el OK de Tomás.")
        faltan = [f"{e}-{r}" for e in sorted(eps) for r in redes if not (RAIZ / "studio/ok" / f"{e}-{r}.ok").exists()]
        if faltan:
            bloquear("Falta el OK de Tomás para: " + ", ".join(faltan) +
                     f". Pídele que corra en su terminal: tools/ok.sh {sorted(eps)[0]} " + " ".join(redes))


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool, inp = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
    revisar_ok(tool, inp)
    revisar_render(tool, inp)
    sys.exit(0)


if __name__ == "__main__":
    main()
