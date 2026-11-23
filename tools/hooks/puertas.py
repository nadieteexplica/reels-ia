"""Hook PreToolUse de Claude Code (.claude/settings.json): las puertas de las reglas duras que no dependen de la memoria.

1. **Render final y Release sólo con QA aprobado.** Bloquea crear o cambiar un trabajo de render FINAL
   (jobs/render2d/*.json sin "prerelease": true ni tag "-borrador"; jobs/render-final/*) y lanzar o relanzar workflows
   que producen el video final o lo publican en un Release (render-2d final, release, render, render-gpu, armar,
   armar-intro), si studio/episodios/<ep>/qa/qa.json no está aprobado o las fuentes cambiaron (huella).
   Los borradores pasan sin QA (se renderizan para hacer el QA). Actions repite el chequeo (qa_video.py verificar).
2. **Metricool sólo con el OK de Tomás para ESE post.** Bloquea crear/cambiar un post programado sin
   studio/ok/<ep>-<red>.ok por cada red. El OK se gasta al usarlo (se renombra a .usado). Mandar a borrador
   (draft: true) siempre pasa. Las herramientas de vidIQ que publican o suben se bloquean siempre (se publica sólo
   por Metricool).
3. **Nadie más que Tomás crea OKs ni Claude escribe qa.json / auditor_final.json a mano** fuera de las herramientas.

Falla CERRADO: si algo se rompe al revisar una acción sensible, se bloquea. Código 2 + mensaje = bloqueado.
"""
import json, re, subprocess, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RENDER_DIRS = ("jobs/render2d", "jobs/render-final")
WF_FINALES = ("render-2d", "release", "render.yml", "render-gpu", "armar", "armar-intro")
PUBLICAR = re.compile(r"(createScheduledPost|updateScheduledPost|createScheduledPostForReview|sendScheduledPostForReview)$")
VIDIQ_PUBLICA = re.compile(r"vidiq_(instagram_publish_reel|social_post_publish|social_post_draft_create|social_post_draft_update"
                           r"|video_upload|update_video|update_video_thumbnail|upload_image|reply_to_comment)$")
REDES = ("youtube", "instagram", "tiktok")
SOLO_LECTURA = re.compile(r"^\s*(ls|cat|head|tail|wc|git (status|log|diff|show|ls-files)|grep|find)\b")
SENSIBLE = re.compile(r"studio/ok|ok\.sh|qa\.json|auditor_final|jobs/render|gh (workflow|run|api)|ScheduledPost|vidiq_")


def bloquear(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def qa_ok(ep):
    q = RAIZ / "studio/episodios" / ep / "qa/qa.json"
    if not q.exists():
        return f"no hay QA del episodio {ep} (falta {q.relative_to(RAIZ)}). Corre la skill qa-video primero."
    d = json.load(open(q))
    if not d.get("aprobado"):
        return f"el QA de {ep} no está aprobado. Arregla los bloqueantes y vuelve a pasarlo."
    r = subprocess.run([sys.executable, str(RAIZ / "tools/qa_video.py"), "huella", ep], capture_output=True, text=True)
    if r.returncode != 0 or r.stdout.strip() != d.get("huella_fuentes"):
        return f"las fuentes de {ep} cambiaron después del QA (guion, voz, sonido, escena o kit): vuelve a pasar el QA."
    return None


def trabajo(texto):
    try:
        return json.loads(texto)
    except Exception:
        return {"episodio": (re.search(r'"episodio"\s*:\s*"([^"]+)"', texto or "") or [None, None])[1]}


def es_borrador(j):
    return bool(j.get("prerelease")) or str(j.get("tag", "")).endswith("-borrador")


def revisar_archivo(tool, inp):
    ruta = str(inp.get("file_path", ""))
    if "studio/ok/" in ruta and not ruta.endswith("README.md"):
        bloquear("Los OK los crea sólo Tomás con tools/ok.sh en su terminal. Pídeselo.")
    if re.search(r"/qa/(qa|auditor_final)\.json$", ruta) and tool != "Read":
        if ruta.endswith("qa.json"):
            bloquear("qa.json lo escribe sólo tools/qa_video.py cerrar <ep>.")
        # auditor_final.json: sólo con la respuesta TAL CUAL del auditor (se guarda con tools/guardar_veredicto.py)
        bloquear("auditor_final.json se guarda con tools/guardar_veredicto.py (la respuesta del auditor tal cual), no a mano.")
    if any(d in ruta for d in RENDER_DIRS):
        contenido = inp.get("content")
        if contenido is None:  # Edit: el contenido resultante
            actual = Path(ruta).read_text() if Path(ruta).exists() else ""
            contenido = actual.replace(inp.get("old_string", ""), inp.get("new_string", ""))
        j = trabajo(contenido)
        if es_borrador(j):
            return
        if not j.get("episodio"):
            bloquear("El trabajo de render no dice \"episodio\": no se puede revisar su QA.")
        err = qa_ok(j["episodio"])
        if err:
            bloquear("Render final bloqueado: " + err)


def revisar_bash(cmd):
    if SOLO_LECTURA.match(cmd) and not re.search(r"[>|;&]|`|\$\(", cmd):
        return
    if re.search(r"studio/ok|ok\.sh", cmd) and not re.match(r"^\s*git (add|commit)\b", cmd):
        bloquear("Los OK los crea sólo Tomás con tools/ok.sh en su terminal. Pídeselo.")
    if re.search(r"qa\.json|auditor_final\.json", cmd):
        limpio = re.fullmatch(r"\s*(\S*python3?\S*\s+)?tools/(qa_video|guardar_veredicto)\.py\s+[\w\-./ ]+", cmd)
        if not (limpio or re.match(r"^\s*git (add|commit)\b", cmd)):
            bloquear("qa.json y auditor_final.json sólo los escriben tools/qa_video.py y tools/guardar_veredicto.py.")
    if re.search(r"jobs/render(2d|-final)", cmd) and not re.match(r"^\s*git (add|commit|push|pull)\b", cmd):
        bloquear("Los trabajos de render se crean con Write (así el hook revisa el QA), no con la terminal.")
    if re.search(r"gh\s+run\s+rerun|gh\s+api\b.*dispatches|gh\s+workflow\s+(run|enable)\s+\d+", cmd):
        bloquear("Relanzar workflows por ID o por la API no pasa por la puerta de QA: usa gh workflow run <nombre>.yml -f trabajo=...")
    m = re.search(r"gh\s+workflow\s+run\s+(\S+)(.*)", cmd)
    if m and any(w in m.group(1) for w in WF_FINALES):
        args = m.group(2)
        ep = None
        t = re.search(r"trabajo=(\S+)", args)
        if t and (RAIZ / t.group(1)).exists():
            j = trabajo((RAIZ / t.group(1)).read_text())
            if es_borrador(j) and "release" not in m.group(1):
                return
            ep = j.get("episodio")
        e = re.search(r"episodio=(\S+)", args)
        ep = ep or (e.group(1) if e else None)
        if not ep:
            bloquear("No sé de qué episodio es ese render/release: pasa -f trabajo=jobs/... (con \"episodio\") o -f episodio=<ep>.")
        err = qa_ok(ep)
        if err:
            bloquear("Render final / release bloqueado: " + err)


def revisar_publicacion(tool, inp):
    if VIDIQ_PUBLICA.search(tool):
        bloquear("Se publica sólo por Metricool y con el OK de Tomás por post: las herramientas de vidIQ que suben o publican no se usan.")
    if not PUBLICAR.search(tool):
        return
    info = inp.get("info", inp)
    if isinstance(info, str):
        try:
            info = json.loads(info)
        except Exception:
            info = {}
    if isinstance(info, dict) and str(info.get("draft", "")).lower() == "true":
        return  # mandar a borrador siempre se puede (despublicar rápido)
    texto = json.dumps(inp, ensure_ascii=False)
    eps = set(re.findall(r"/releases/download/(ep\d+[a-z]?)/", texto))
    redes = [str(x.get("network", "")).lower() for x in (info.get("providers", []) if isinstance(info, dict) else []) if isinstance(x, dict)]
    redes = [r for r in REDES if r in redes]
    if not eps or not redes:
        bloquear("El post tiene que llevar el video del Release epNN de GitHub y sus redes en providers: sin eso no se puede revisar el OK de Tomás.")
    oks = [RAIZ / "studio/ok" / f"{e}-{r}.ok" for e in sorted(eps) for r in redes]
    faltan = [p.stem for p in oks if not p.exists()]
    if faltan:
        bloquear("Falta el OK de Tomás para: " + ", ".join(faltan) +
                 f". Pídele que corra en su terminal: tools/ok.sh {sorted(eps)[0]} " + " ".join(redes))
    # el OK sirve para UN post: se gasta
    for p in oks:
        p.rename(p.with_name(p.stem + f".usado-{time.strftime('%Y%m%d-%H%M%S')}"))


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool, inp = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
    try:
        if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            revisar_archivo(tool, inp)
        elif tool == "Bash":
            revisar_bash(inp.get("command", ""))
        revisar_publicacion(tool, inp)
    except SystemExit:
        raise
    except Exception as e:  # falla cerrado sólo en lo sensible
        if SENSIBLE.search(tool + json.dumps(inp, ensure_ascii=False)):
            bloquear(f"La puerta no pudo revisar esta acción ({type(e).__name__}: {e}); por seguridad se bloquea.")
    sys.exit(0)


if __name__ == "__main__":
    main()
