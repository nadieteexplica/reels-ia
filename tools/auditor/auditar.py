"""Auditor de "Nadie te explica": prepara cada revisión, dice qué encargos faltan y cierra el veredicto.

  python3 tools/auditor/auditar.py preparar <ep> <etapa> [opciones]   → chequeos + materiales + encargos (ronda nueva)
  python3 tools/auditor/auditar.py estado   <ep> <etapa> [--ronda N]  → encargos listos / faltantes (los faltantes se relanzan)
  python3 tools/auditor/auditar.py cerrar   <ep> <etapa> [--ronda N]  → veredicto.md + veredicto.json (sale 0 si APROBADO)
  python3 tools/auditor/auditar.py lanzar   <ep> <etapa> [--ronda N]  → imprime el texto exacto para lanzar cada subagente faltante

Etapas: 1 guion · 2 voz · 3 storyboard · 4 cuadros · 5 kling · 6 video · 7 paquete · P proceso.
Todo queda en studio/episodios/<ep>/auditoria/<etapa>/rN/. Los materiales (imágenes) no se suben al repo: se regeneran con 'preparar'.
Detalle de reglas, checklists y formato: docs/AUDITOR.md.
"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import comun, checks

PROMPTS = os.path.join(comun.RAIZ, "tools", "auditor", "prompts")
MAX_RONDAS = 3
CRITERIOS = {
    "1-guion": ["precision", "gancho", "claridad", "compartible"],
    "2-voz": ["pronunciacion", "ritmo"],
    "3-storyboard": ["foco", "ritmo", "viabilidad", "gancho_visual"],
    "4-cuadros": ["belleza", "personaje", "manos", "anatomia"],
    "5-kling": ["manos", "objeto", "personaje", "estabilidad"],
    "6-video": ["gancho", "claridad", "ritmo", "belleza", "animacion", "subtitulos", "audio", "precision"],
    "7-paquete": ["textos", "cumplimiento"],
    "P-proceso": [],
}
TRAMO = 9   # planos por revisor en la etapa de video (cada revisión corta: si se corta, se relanza sin perder nada)


def rel(p, base):
    return os.path.relpath(p, base)


def encargo(rd, id_, prompt, alcance, materiales, contexto, extra=None):
    e = {"id": id_, "prompt": f"tools/auditor/prompts/{prompt}", "alcance": alcance,
         "materiales": materiales, "contexto": contexto, "salida": f"{id_}.json"}
    if extra:
        e.update(extra)
    return e


def preparar(a):
    et = comun.etapa_id(a.etapa)
    ep_d = comun.ep_dir(a.ep)
    rd, ronda = comun.ronda_dir(a.ep, et, crear=True)
    if ronda > MAX_RONDAS:
        print(f"⚠️  ronda {ronda}: ya pasaron {MAX_RONDAS} rondas. Según AUDITOR.md, se propone un reemplazo (no se sigue corrigiendo).")
    md = os.path.join(rd, "materiales")
    R = lambda p: os.path.relpath(p, comun.RAIZ)
    ctx_base = ["docs/AUDITOR.md"]
    encs = []
    if et == "1-guion":
        res = checks.guion(ep_d)
        encs.append(encargo(rd, "guion", "1-guion.md", "guion completo", [R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md", "docs/IDEAS.md", "docs/PUBLICADOS.md"]))
    elif et == "2-voz":
        words = a.words or os.path.join(ep_d, "words.json")
        ident = os.path.basename(ep_d)
        asr = a.asr or os.path.join(comun.RAIZ, "out", "asr", f"{ident}.json")
        res = checks.voz(ep_d, words, os.path.join(comun.RAIZ, "out", "status.json"), a.job, asr)
        W = comun.leer(words, [])
        mp3 = a.mp3 or os.path.join(comun.RAIZ, "out", "tts", f"{ident}.mp3")
        sil = checks.silencios(mp3) if os.path.exists(mp3) else []
        with open(os.path.join(md, "voz.md"), "w") as f:
            f.write("Tiempos de la alineación de ElevenLabs. Ojo: la alineación suele meter el silencio dentro de la palabra "
                    "(sobre todo en las que terminan en '...'); la pausa que se oye es la columna 'silencio real' "
                    "(ffmpeg silencedetect a −35 dB, mínimo 0,1 s) entre esta palabra y la siguiente.\n\n")
            f.write("| # | palabra | inicio | fin | dura | hueco en la alineación | silencio real después |\n|---|---|---|---|---|---|---|\n")
            for i, w in enumerate(W):
                sig = W[i + 1]["s"] if i + 1 < len(W) else w["e"] + 1
                hueco = sig - w["e"]
                real = sum(max(0, min(b, sig + 0.05) - max(a_, w["s"] + 0.08)) for a_, b in sil if a_ < sig + 0.05 and b > w["s"] + 0.08)
                f.write(f"| {i} | {w['w']} | {w['s']:.2f} | {w['e']:.2f} | {w['e'] - w['s']:.2f} | {hueco:.2f} | {real:.2f} |\n")
        encs.append(encargo(rd, "voz", "2-voz.md", "voz completa", [R(os.path.join(md, "voz.md")), R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "3-storyboard":
        W = comun.leer(os.path.join(ep_d, "words.json"), [])
        res = checks.storyboard(ep_d, W[-1]["e"] if W else None)
        encs.append(encargo(rd, "storyboard", "3-storyboard.md", "storyboard completo",
                            [R(os.path.join(ep_d, "storyboard.md")), R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md", "CONTEXTO.md"]))
    elif et == "4-cuadros":
        import materiales
        imgs = sorted(sum((glob.glob(g) for g in a.imagenes), []))
        if not imgs:
            sys.exit("--imagenes no encontró archivos")
        ficha = a.ficha or os.path.join(comun.RAIZ, "studio", "personaje", "ficha.jpg")
        lista = materiales.cuadros(md, imgs, ficha)
        res = checks.cuadros(lista)
        # pedidos de Kling que parten de estos cuadros: la instrucción se revisa ANTES de gastar unidades
        nombres = {os.path.basename(i) for i in imgs}
        ped = {}
        for p in glob.glob(os.path.join(ep_d, "kling", "pedido*.json")) + (a.pedidos or []):
            for x in comun.leer(p, []):
                if os.path.basename(x.get("inicio", "")) in nombres:
                    ped[x["nombre"]] = x
        if ped:
            pk = checks.pedidos_kling(ped)
            res["fallas"] += pk["fallas"]
            res["avisos"] += pk["avisos"]
            res["datos"]["pedidos_kling"] = sorted(ped)
        extra = [R(os.path.join(md, "ficha_personaje.jpg"))] if os.path.exists(os.path.join(md, "ficha_personaje.jpg")) else []
        for k in range(0, len(lista), 6):
            parte = lista[k:k + 6]
            encs.append(encargo(rd, f"cuadros{k // 6 + 1}", "4-cuadros.md", ", ".join(c["cuadro"] for c in parte),
                                [R(os.path.join(md, c["archivo"])) for c in parte] + extra + [R(os.path.join(md, "cuadros.json"))],
                                ctx_base + ["docs/MANUAL_PRODUCCION.md"], {"notas_de_uso": a.nota or ""}))
    elif et == "5-kling":
        import materiales
        clips = sorted(sum((glob.glob(g) for g in a.clips), []))
        if not clips:
            sys.exit("--clips no encontró archivos")
        pedidos = {}
        for p in glob.glob(os.path.join(ep_d, "kling", "pedido*.json")) + (a.pedidos or []):
            for x in comun.leer(p, []):
                ini = x.get("inicio", "")
                pedidos.setdefault(x["nombre"], {"inicio": os.path.join(ep_d, "kling", ini) if ini else None, "prompt": x.get("prompt", "")})
        lista = materiales.kling(md, clips, pedidos)
        pk = comun.leer(os.path.join(ep_d, "kling", "planos.json"))
        res = checks.kling(lista, pk)
        for k in range(0, len(lista), 3):
            parte = lista[k:k + 3]
            mats = []
            for c in parte:
                mats.append(R(os.path.join(md, c["cuadros"])))
                if c.get("detalle"):
                    mats.append(R(os.path.join(md, c["detalle"])))
                if c["inicio"]:
                    mats.append(R(os.path.join(md, c["inicio"])))
            mats.append(R(os.path.join(md, "clips.json")))
            if os.path.exists(os.path.join(comun.RAIZ, "studio", "personaje", "ficha.jpg")):
                mats.append("studio/personaje/ficha.jpg")
            encs.append(encargo(rd, f"kling{k // 3 + 1}", "5-kling.md", ", ".join(c["clip"] for c in parte), mats,
                                ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "6-video":
        import materiales
        planos = comun.cargar_planos(a.planos) if a.planos else None
        words = a.words or os.path.join(ep_d, "words.json")
        kp = [] if a.kling_planos == "ninguno" else comun.leer(a.kling_planos or os.path.join(ep_d, "kling", "planos.json"), [])
        mat = materiales.video(md, a.video, planos, a.subs, words, kp)
        res = checks.video(a.video, mat, a.subs)
        P = mat["planos"]
        comunes = [R(os.path.join(md, "contacto.jpg"))]
        for k in range(0, len(P), TRAMO):
            parte = P[k:k + TRAMO]
            ids = {p["plano"] for p in parte}
            evs = [e for e in mat["eventos"] if e.get("plano") in ids]
            mats = [R(os.path.join(md, p["tira"])) for p in parte] + [R(os.path.join(md, e["imagen"])) for e in evs if e.get("imagen")]
            encs.append(encargo(rd, f"tramo{k // TRAMO + 1}", "6-video-tramo.md",
                                f"planos {parte[0]['plano']}…{parte[-1]['plano']} ({parte[0]['a']:.2f}–{parte[-1]['b']:.2f} s)",
                                comunes + mats + [R(os.path.join(md, "planos.json")), R(os.path.join(md, "eventos.json"))],
                                ctx_base + ["docs/MANUAL_PRODUCCION.md", R(os.path.join(ep_d, "guion.md"))],
                                {"planos": [p["plano"] for p in parte], "eventos": [e["id"] for e in evs]}))
        glob_mats = comunes + [R(os.path.join(md, x)) for x in ("cuadro0.jpg", "gancho.jpg", "loop.jpg", "audio.json")]
        if os.path.exists(os.path.join(md, "subtitulos.md")):
            glob_mats.append(R(os.path.join(md, "subtitulos.md")))
        encs.append(encargo(rd, "global", "6-video-global.md", "video completo (gancho, ritmo, loop, subtítulos, audio, precisión)",
                            glob_mats + [R(os.path.join(md, "planos.json"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md", R(os.path.join(ep_d, "guion.md"))]))
    elif et == "7-paquete":
        res = checks.paquete(ep_d, a.url)
        encs.append(encargo(rd, "paquete", "7-paquete.md", "textos de publicación",
                            [R(os.path.join(ep_d, "entrega", "caption.md")), R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "P-proceso":
        import proceso
        res = proceso.auditar(a.ep, proceso.ts(a.desde), proceso.ts(a.hasta))
    comun.guardar(os.path.join(rd, "checks.json"), res)
    comun.guardar(os.path.join(rd, "encargos.json"), encs)
    print(f"{et} r{ronda}: {len(res['fallas'])} fallas automáticas, {len(res['avisos'])} avisos, {len(encs)} encargos → {rel(rd, comun.RAIZ)}")
    for x in res["fallas"]:
        print("  ❌", x["que"], ("· " + x["evidencia"]) if x.get("evidencia") else "")
    return rd


def texto_lanzar(rd, e):
    enc = os.path.join(rd, "encargos.json")
    return (f"Eres el AUDITOR independiente de la cuenta \"Nadie te explica\". No conoces a quien hizo este trabajo ni su opinión: "
            f"juzgas sólo los materiales. Repo: {comun.RAIZ}.\n"
            f"1. Lee {comun.RAIZ}/tools/auditor/prompts/comun.md y {comun.RAIZ}/{e['prompt']}.\n"
            f"2. Tu encargo es el de id \"{e['id']}\" en {enc} (alcance, materiales y contexto; las rutas son relativas al repo). "
            f"Los chequeos automáticos de esta ronda están en {os.path.join(rd, 'checks.json')}.\n"
            f"3. Mira TODOS los materiales de tu encargo. No abras otros archivos del repo ni otras carpetas de auditoría.\n"
            f"4. Escribe tu resultado en {os.path.join(rd, e['salida'])} con el formato JSON de comun.md, una sola vez, al final.\n"
            f"Responde con una línea: tu veredicto y el número de problemas.")


def estado(a, imprimir=True):
    et = comun.etapa_id(a.etapa)
    rd, ronda = comun.ronda_dir(a.ep, et, a.ronda)
    encs = comun.leer(os.path.join(rd, "encargos.json"), [])
    listos, faltan = [], []
    for e in encs:
        out = comun.leer(os.path.join(rd, e["salida"]))
        (listos if out and out.get("completo") else faltan).append(e)
    if imprimir:
        print(f"{et} r{ronda}: {len(listos)}/{len(encs)} encargos listos" + (f"; faltan: {', '.join(e['id'] for e in faltan)}" if faltan else ""))
    return rd, ronda, encs, listos, faltan


def lanzar(a):
    rd, _r, _e, _l, faltan = estado(a, imprimir=False)
    for e in faltan:
        print(f"===== {e['id']} =====")
        print(texto_lanzar(rd, e))


def cerrar(a):
    et = comun.etapa_id(a.etapa)
    rd, ronda, encs, listos, faltan = estado(a, imprimir=False)
    if faltan:
        sys.exit(f"faltan encargos: {', '.join(e['id'] for e in faltan)} (relanzarlos con 'lanzar')")
    ch = comun.leer(os.path.join(rd, "checks.json"), {"fallas": [], "avisos": []})
    notas, problemas, vs = {}, [], []
    for e in listos:
        o = comun.leer(os.path.join(rd, e["salida"]))
        vs.append(o.get("veredicto", "NO APROBADO"))
        for c, v in (o.get("notas") or {}).items():
            n = v["nota"] if isinstance(v, dict) else v
            if n is None:          # "no aplica" (p. ej. anatomía en un cuadro sin interior)
                notas.setdefault(c, {"nota": None, "por_que": "no aplica", "de": e["id"]})
                continue
            if c not in notas or notas[c]["nota"] is None or n < notas[c]["nota"]:
                notas[c] = {"nota": n, "por_que": v.get("por_que", "") if isinstance(v, dict) else "", "de": e["id"]}
        for p in o.get("problemas", []):
            p["de"] = e["id"]
            problemas.append(p)
    if et == "5-kling":       # el tramo de cada clip que usa el video tiene que caer dentro de su tramo usable
        usables = {}
        for e in listos:
            for c in comun.leer(os.path.join(rd, e["salida"]), {}).get("clips", []) or []:
                usables[c["clip"]] = c
        pk = comun.leer(os.path.join(comun.ep_dir(a.ep), "kling", "planos.json"), []) or []
        planos_t = {}
        W = comun.leer(os.path.join(comun.ep_dir(a.ep), "words.json"), [])
        for k in pk:
            c = usables.get(os.path.splitext(k["clip"])[0])
            if not c:
                continue
            a0 = float(k.get("desde", 0))
            dur = float(k.get("dur", 2.0)) * float(k.get("velocidad", 1.0))
            u = c.get("usable") or [0, 0]
            if not c.get("sirve") or a0 < u[0] - 0.05 or a0 + dur > u[1] + 0.05:
                ch["fallas"].append({"que": f"el plano {k['plano']} usa {k['clip']} desde {a0:.1f} s y su tramo usable es {u[0]:.1f}–{u[1]:.1f} s"
                                     + ("" if c.get("sirve") else " (el revisor dice que el clip no sirve)"),
                                     "evidencia": c.get("por_que", ""), "bloqueante": True})
    for f in ch["fallas"]:
        problemas.append({"prioridad": 0 if f.get("bloqueante") else 1, "bloqueante": bool(f.get("bloqueante")),
                          "que": "[automático] " + f["que"], "donde": f.get("evidencia", ""), "arreglo": "cumplir la regla", "de": "checks"})
    problemas.sort(key=lambda p: (not p.get("bloqueante"), p.get("prioridad", 9)))
    bajos = {c: v for c, v in notas.items() if v["nota"] is not None and v["nota"] < 8}
    falta_nota = [c for c in CRITERIOS.get(et, []) if c not in notas and encs]
    aprobado = not ch["fallas"] and not any(p.get("bloqueante") for p in problemas) and not bajos and not falta_nota \
        and all(v == "APROBADO" for v in vs)
    ver = {"etapa": et, "ronda": ronda, "veredicto": "APROBADO" if aprobado else "NO APROBADO", "notas": notas,
           "problemas": problemas, "avisos": ch.get("avisos", []), "criterios_sin_nota": falta_nota,
           "reemplazo": (not aprobado and ronda >= MAX_RONDAS)}
    comun.guardar(os.path.join(rd, "veredicto.json"), ver)
    L = [f"# {et} · ronda {ronda} · **{ver['veredicto']}**", ""]
    if ver["reemplazo"]:
        L += [f"**{MAX_RONDAS} rondas sin aprobar: se propone un reemplazo (no se sigue corrigiendo).**", ""]
    if notas:
        L += ["| criterio | nota | por qué |", "|---|---|---|"]
        L += [f"| {c} | {'—' if v['nota'] is None else ('**' + str(v['nota']) + '**' if v['nota'] < 8 else v['nota'])} | {v['por_que']} |" for c, v in notas.items()]
        L.append("")
    if falta_nota:
        L += [f"Criterios sin nota (cuentan como no aprobados): {', '.join(falta_nota)}", ""]
    L += ["## Arreglos (en orden)", ""]
    for i, p in enumerate(problemas, 1):
        donde = " · ".join(str(x) for x in (p.get("plano") and f"plano {p['plano']}", p.get("segundo") and f"{p['segundo']} s", p.get("donde")) if x)
        L.append(f"{i}. {'🛑 ' if p.get('bloqueante') else ''}{p['que']}" + (f" — {donde}" if donde else "") +
                 (f". **Arreglo:** {p['arreglo']}" if p.get("arreglo") else ""))
    if ch.get("avisos"):
        L += ["", "## Avisos automáticos (mirados por el revisor)", ""] + [f"- {x['que']}" + (f" · {x['evidencia']}" if x.get("evidencia") else "") for x in ch["avisos"]]
    open(os.path.join(rd, "veredicto.md"), "w").write("\n".join(L) + "\n")
    # resumen por episodio
    base = os.environ.get("AUDITORIA_BASE") or os.path.join(comun.ep_dir(a.ep), "auditoria")
    filas = []
    for d in sorted(glob.glob(os.path.join(base, "*", "r*", "veredicto.json"))):
        v = comun.leer(d)
        filas.append(f"| {v['etapa']} | r{v['ronda']} | {v['veredicto']} | {sum(1 for p in v['problemas'] if p.get('bloqueante'))} | {len(v['problemas'])} |")
    open(os.path.join(base, "ESTADO.md"), "w").write("| etapa | ronda | veredicto | bloqueantes | arreglos |\n|---|---|---|---|---|\n" + "\n".join(filas) + "\n")
    print(open(os.path.join(rd, "veredicto.md")).read())
    sys.exit(0 if aprobado else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["preparar", "estado", "lanzar", "cerrar"])
    ap.add_argument("ep")
    ap.add_argument("etapa")
    ap.add_argument("--ronda", type=int)
    ap.add_argument("--video")
    ap.add_argument("--planos", help="*_planos.json del render, lista [{plano,a,b}] o build_epNN.py")
    ap.add_argument("--subs", help="subs_log.json del render")
    ap.add_argument("--words")
    ap.add_argument("--kling-planos", help="kling/planos.json del episodio (por defecto) o 'ninguno'")
    ap.add_argument("--clips", nargs="*", default=[])
    ap.add_argument("--pedidos", nargs="*", default=[], help="pedidos de Kling extra (p. ej. versiones viejas sacadas de git)")
    ap.add_argument("--imagenes", nargs="*", default=[])
    ap.add_argument("--ficha")
    ap.add_argument("--nota", help="para qué son los cuadros (estilo de escenario nuevo / partida de Kling para el plano N)")
    ap.add_argument("--asr")
    ap.add_argument("--mp3", help="locución (por defecto out/tts/<ep>.mp3)")
    ap.add_argument("--job")
    ap.add_argument("--url")
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    a = ap.parse_args()
    {"preparar": preparar, "estado": estado, "lanzar": lanzar, "cerrar": cerrar}[a.accion](a)
