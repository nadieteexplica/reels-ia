"""Auditor de "Nadie te explica" (proceso v2, 21-oct-2026): prepara cada revisión, dice qué encargos faltan y cierra el veredicto.

  python3 tools/auditor/auditar.py preparar <ep> <etapa> [opciones]   → chequeos + materiales + encargos (ronda nueva)
  python3 tools/auditor/auditar.py estado   <ep> <etapa> [--ronda N]  → encargos listos / faltantes (los faltantes se relanzan)
  python3 tools/auditor/auditar.py cerrar   <ep> <etapa> [--ronda N]  → veredicto.md + veredicto.json (sale 0 si APROBADO)
  python3 tools/auditor/auditar.py lanzar   <ep> <etapa> [--ronda N]  → imprime el texto exacto para lanzar cada subagente faltante

Etapas: 1 guion · 2 voz · 3 storyboard · 4 cuadros · 5 kling · 6 animatic · 7 final · 8 paquete · P proceso.
Reglas v2 (docs/AUDITOR.md): sin ronda si falla lo automático, máx. 2 rondas (la 2.ª verifica), 1 revisor por cada 10 planos + 1 global,
bloqueantes sólo de la lista cerrada (B1–B11), aprueba con promedio ≥ 8 y ningún criterio bajo 7, y se muestran sólo las
5 sugerencias más importantes. Todo queda en studio/episodios/<ep>/auditoria/<etapa>/rN/.
"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import comun, checks

PROMPTS = os.path.join(comun.RAIZ, "tools", "auditor", "prompts")
TOPES = comun.topes()                       # presupuesto.json → proceso_v2 (los cambia Tomás ahí)
MAX_RONDAS = int(TOPES["rondas_por_puerta"])
TRAMO = int(TOPES["planos_por_revisor"])    # un revisor no alcanza a mirar 40 tiras + eventos (Ep. 2: tramos de 9)
TOP_SUGERENCIAS = 5
PROMEDIO_MIN, NOTA_MIN = float(TOPES["promedio_min"]), int(TOPES["nota_min_revisor"])
BLOQUEANTES = {   # lista cerrada: un "bloqueante" sin uno de estos tipos se trata como sugerencia
    "B1": "piezas que se atraviesan o flotan a la vista (dedos, objetos, cuerpos, hojas, frutos)",
    "B2": "algo aparece, desaparece o cambia de forma/color de golpe sin querer; utilería técnica a la vista",
    "B3": "pantalla vacía o plano muerto más de 0,2 s",
    "B4": "personaje distinto a su ficha o deformado",
    "B5": "cara u ojos tapados por un gráfico o subtítulo; subtítulo ilegible, fuera de zona o desfasado",
    "B6": "dato falso, sin respaldo, o fuente que no dice eso",
    "B7": "interior del cuerpo confuso (más de un foco, cortes, cráneo, órganos inventados)",
    "B8": "lista negra (retos peligrosos, tragedias recientes, política, religión, salud como indicación, marcas o personajes ajenos)",
    "B9": "estilo rechazado o imagen rota (quemado, lavado, low-poly, rayos X o neón 2D)",
    "B10": "faltas de ortografía o tildes en pantalla o en los textos",
    "B11": "algo clave cortado por el borde o bajo la interfaz de la app (y > 1250) mientras la voz lo nombra",
}
CRITERIOS = {
    "1-guion": ["precision", "gancho", "claridad", "compartible"],
    "2-voz": ["pronunciacion", "ritmo"],
    "3-storyboard": ["foco", "ritmo", "viabilidad", "gancho_visual"],
    "4-cuadros": ["belleza", "personaje", "manos", "anatomia"],
    "5-kling": ["manos", "objeto", "personaje", "estabilidad"],
    "6-animatic": ["gancho", "claridad", "ritmo", "belleza", "animacion", "subtitulos", "audio", "precision"],
    "7-final": [],                 # sólo bloqueantes
    "8-paquete": ["textos", "cumplimiento"],
    "P-proceso": [],
}


def rel(p, base):
    return os.path.relpath(p, base)


def encargo(id_, prompt, alcance, materiales, contexto, extra=None):
    e = {"id": id_, "prompt": f"tools/auditor/prompts/{prompt}", "alcance": alcance,
         "materiales": materiales, "contexto": contexto, "salida": f"{id_}.json"}
    if extra:
        e.update(extra)
    return e


def anterior(ep, et, ronda):
    """Lo que dejó la ronda anterior para verificar: bloqueantes + las sugerencias más importantes."""
    if ronda <= 1:
        return None
    rd, _ = comun.ronda_dir(ep, et, ronda - 1)
    v = comun.leer(os.path.join(rd, "veredicto.json"))
    if not v:
        return None
    # lo automático se vuelve a medir solo en cada ronda: a verificar va lo que dijeron los revisores
    revis = lambda p: p.get("de") not in ("checks", "verificación")
    items = [p for p in v.get("problemas", []) if p.get("bloqueante") and revis(p)] + \
            [p for p in v.get("sugerencias", []) if revis(p)][:TOP_SUGERENCIAS]
    out = []
    for i, p in enumerate(items, 1):
        out.append({"id": f"A{i}", "bloqueante": bool(p.get("bloqueante")), "tipo": p.get("tipo"), "plano": p.get("plano"),
                    "segundo": p.get("segundo"), "que": p.get("que"), "arreglo": p.get("arreglo"), "de": p.get("de")})
    return out


def _planos_de(items):
    out = set()
    for x in items or []:
        try:
            out.add(int(x.get("plano")))
        except (TypeError, ValueError):
            pass
    return out


def asignar(encs, ant):
    """Cada cosa a verificar la verifica UN revisor: el mismo que la marcó (mismo id) o el que tiene ese plano."""
    for x in ant:
        dest = next((e for e in encs if e["id"] == x.get("de")), None)
        if dest is None and x.get("plano") not in (None, ""):
            dest = next((e for e in encs if str(x.get("plano")) in {str(p) for p in e.get("planos", [])}), None)
        dest = dest or encs[0]
        x["asignado"] = dest["id"]
        dest.setdefault("verificar_ids", []).append(x["id"])


def preparar(a):
    et = comun.etapa_id(a.etapa)
    ep_d = comun.ep_dir(a.ep)
    _rd0, ultima = comun.ronda_dir(a.ep, et)
    existe = os.path.isdir(_rd0)
    ultima = ultima if existe else 0
    base_et = os.path.dirname(_rd0)
    if et == "8-paquete" and a.url and existe and (comun.leer(os.path.join(_rd0, "veredicto.json"), {}) or {}).get("veredicto") == "APROBADO":
        # comprobar la URL pública después del OK de Tomás no es una ronda nueva
        res = checks.paquete(ep_d, a.url)
        comun.guardar(os.path.join(base_et, "url.json"), res)
        for x in res["fallas"]:
            print("  ❌", x["que"])
        print(f"paquete: URL {'OK' if not res['fallas'] else 'con fallas'} → {rel(os.path.join(base_et, 'url.json'), comun.RAIZ)}")
        sys.exit(1 if res["fallas"] else 0)
    if et != "P-proceso" and ultima >= MAX_RONDAS and not a.forzar:      # P es un informe: no tiene tope
        sys.exit(f"⛔ {et}: ya hubo {MAX_RONDAS} rondas. No se abre otra (docs/AUDITOR.md): lo que sigue fallando se simplifica o se "
                 f"reemplaza por una plantilla y sigue a la puerta siguiente (en el animatic: la puerta 7 revisa bloqueantes en todo el "
                 f"video); si es guion o storyboard, se cambia la idea o se le pregunta a Tomás. Sólo con --forzar 'motivo'.")
    ronda = ultima + 1
    # se arma en una carpeta provisoria: si el chequeo automático falla, NO se abre ronda ni se lanzan revisores
    rd = os.path.join(base_et, "_pre")
    import shutil
    shutil.rmtree(rd, ignore_errors=True)
    md = os.path.join(rd, "materiales")
    os.makedirs(md, exist_ok=True)
    ant = anterior(a.ep, et, ronda)
    R = lambda p: os.path.relpath(p, comun.RAIZ)
    ctx_base = ["docs/AUDITOR.md"]
    encs = []
    if et == "1-guion":
        res = checks.guion(ep_d)
        mats = [R(os.path.join(ep_d, "guion.md"))]
        if a.fuentes:   # extractos bajados por el workflow fuentes.yml (regla: nada de consultas web en serie)
            import shutil
            shutil.copy(a.fuentes, os.path.join(md, "fuentes.md"))
            mats.append(R(os.path.join(md, "fuentes.md")))
        else:
            res["avisos"].append({"que": "sin extractos de fuentes (workflow fuentes.yml): el revisor tendrá que buscar en la web", "evidencia": ""})
        encs.append(encargo("guion", "1-guion.md", "guion completo", mats,
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
        # v2: la voz es automática; sólo hay revisor si la transcripción encontró diferencias o hay ritmo raro
        dif = res["datos"].get("asr_diferencias") or []
        raros = [x for x in res["avisos"] if "ritmo" in x["que"] or "pausa" in x["que"]]
        if dif or raros:
            encs.append(encargo("voz", "2-voz.md", "voz completa", [R(os.path.join(md, "voz.md")), R(os.path.join(ep_d, "guion.md"))],
                                ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "3-storyboard":
        W = comun.leer(os.path.join(ep_d, "words.json"), [])
        res = checks.storyboard(ep_d, W[-1]["e"] if W else None)
        mats = [R(os.path.join(ep_d, "storyboard.md")), R(os.path.join(ep_d, "guion.md"))]
        if os.path.exists(os.path.join(ep_d, "ficha.jpg")):    # personajes propios del episodio
            mats.append(R(os.path.join(ep_d, "ficha.jpg")))
        encs.append(encargo("storyboard", "3-storyboard.md", "storyboard completo (fichas de plano)", mats,
                            ctx_base + ["docs/MANUAL_PRODUCCION.md", "CONTEXTO.md", "studio/plantilla/KIT.md"]))
    elif et == "4-cuadros":
        import materiales
        imgs = sorted(sum((glob.glob(g) for g in a.imagenes), []))
        if not imgs:
            sys.exit("--imagenes no encontró archivos")
        ficha = a.ficha or comun.ficha(ep_d)
        lista = materiales.cuadros(md, imgs, ficha)
        res = checks.cuadros(lista)
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
        encs.append(encargo("cuadros", "4-cuadros.md", ", ".join(c["cuadro"] for c in lista),
                            [R(os.path.join(md, c["archivo"])) for c in lista] + extra + [R(os.path.join(md, "cuadros.json"))],
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
        mats = []
        for c in lista:
            mats.append(R(os.path.join(md, c["cuadros"])))
            if c.get("detalle"):
                mats.append(R(os.path.join(md, c["detalle"])))
            if c["inicio"]:
                mats.append(R(os.path.join(md, c["inicio"])))
        mats.append(R(os.path.join(md, "clips.json")))
        if comun.ficha(ep_d):
            mats.append(R(comun.ficha(ep_d)))
        encs.append(encargo("kling", "5-kling.md", ", ".join(c["clip"] for c in lista), mats, ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et in ("6-animatic", "7-final"):
        import materiales
        planos = comun.cargar_planos(a.planos) if a.planos else None
        words = a.words or os.path.join(ep_d, "words.json")
        kp = [] if a.kling_planos == "ninguno" else comun.leer(a.kling_planos or os.path.join(ep_d, "kling", "planos.json"), [])
        mat = materiales.video(md, a.video, planos, a.subs, words, kp, meta=a.meta, graficos=a.graficos)
        res = checks.video(a.video, mat, a.subs)
        res["fallas"] += mat["chequeo"]["fallas"]
        res["avisos"] += mat["chequeo"]["avisos"]
        P = mat["planos"]
        comunes = [R(os.path.join(md, "contacto.jpg"))]
        ficha = comun.ficha(ep_d)
        if ficha:
            import shutil
            shutil.copy(ficha, os.path.join(md, "ficha.jpg"))
            comunes.append(R(os.path.join(md, "ficha.jpg")))
        ctx = ctx_base + ["docs/MANUAL_PRODUCCION.md", R(os.path.join(ep_d, "guion.md"))]
        glob_mats = comunes + [R(os.path.join(md, x)) for x in ("cuadro0.jpg", "gancho.jpg", "loop.jpg", "audio.json")]
        if os.path.exists(os.path.join(md, "subtitulos.md")):
            glob_mats.append(R(os.path.join(md, "subtitulos.md")))
        evs = [R(os.path.join(md, e["imagen"])) for e in mat["eventos"] if e.get("imagen")]
        if not a.sin_personajes and not mat["chequeo"].get("ojos_cuadros"):
            res["fallas"].append({"que": "sin datos de ojos: no se puede revisar 'cara tapada' (pasar --meta del render, o "
                                         "--sin-personajes si el video no tiene personajes)", "evidencia": "", "bloqueante": True})
        if et == "6-animatic":
            # un revisor por cada ≤10 planos (no alcanza a mirar 40 tiras con sus eventos) + uno global; en la r2 (verificación)
            # sólo los planos que tenían algo que verificar o que se re-renderizaron
            sel = P
            if ant is not None:
                quiero = _planos_de(ant) | {int(x) for x in (a.cambiados or "").split(",") if x.strip()}
                sel = [p for p in P if p["plano"] in quiero]
            for k in range(0, len(sel), TRAMO):
                parte = sel[k:k + TRAMO]
                ids = {p["plano"] for p in parte}
                ev_p = [e for e in mat["eventos"] if e.get("plano") in ids]
                encs.append(encargo(f"planos{k // TRAMO + 1}", "6-animatic-planos.md",
                                    f"planos {parte[0]['plano']}…{parte[-1]['plano']} ({parte[0]['a']:.2f}–{parte[-1]['b']:.2f} s)",
                                    comunes + [R(os.path.join(md, p["tira"])) for p in parte] +
                                    [R(os.path.join(md, e["imagen"])) for e in ev_p if e.get("imagen")] +
                                    [R(os.path.join(md, "planos.json")), R(os.path.join(md, "eventos.json"))], ctx,
                                    {"planos": [p["plano"] for p in parte], "eventos": [e["id"] for e in ev_p]}))
            encs.append(encargo("global", "6-animatic-global.md", "video completo (gancho, ritmo, loop, subtítulos, audio, precisión)",
                                glob_mats + [R(os.path.join(md, "planos.json"))], ctx))
        else:
            encs.append(encargo("final", "7-final.md", "render final: sólo bloqueantes",
                                glob_mats + [R(os.path.join(md, p["tira"])) for p in P] + evs + [R(os.path.join(md, "planos.json"))], ctx))
    elif et == "8-paquete":
        res = checks.paquete(ep_d, a.url)
        encs.append(encargo("paquete", "8-paquete.md", "textos de publicación",
                            [R(os.path.join(ep_d, "entrega", "caption.md")), R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "P-proceso":
        import proceso
        res = proceso.auditar(a.ep, proceso.ts(a.desde), proceso.ts(a.hasta))
    if a.forzar:
        res["avisos"].insert(0, {"que": f"ronda {ronda} abierta con --forzar: {a.forzar}", "evidencia": ""})
    comun.guardar(os.path.join(rd, "checks.json"), res)
    if res["fallas"] and et != "P-proceso":
        # lo medible se arregla ANTES de gastar revisores y rondas
        print(f"{et}: {len(res['fallas'])} fallas automáticas → NO se abre la ronda {ronda} ni se lanzan revisores. "
              f"Arreglar y volver a correr 'preparar' (queda en {rel(rd, comun.RAIZ)}/checks.json).")
        for x in res["fallas"]:
            print("  " + ("🛑" if x.get("bloqueante") else "❌"), x["que"], ("· " + x["evidencia"]) if x.get("evidencia") else "")
        sys.exit(1)
    final = os.path.join(base_et, f"r{ronda}")
    shutil.rmtree(final, ignore_errors=True)
    os.replace(rd, final)
    viejo, nuevo = R(rd), R(final)
    encs = json.loads(json.dumps(encs).replace(viejo, nuevo))
    rd, md = final, os.path.join(final, "materiales")
    # ronda 2: verificación de la ronda 1 (no es una revisión nueva desde cero); cada cosa la verifica un solo revisor
    if ant is not None and encs:
        asignar(encs, ant)
        comun.guardar(os.path.join(md, "anterior.json"), ant)
        for e in encs:
            mias = [x for x in ant if x.get("asignado") == e["id"]]
            comun.guardar(os.path.join(md, f"anterior_{e['id']}.json"), mias)
            e["materiales"].append(R(os.path.join(md, f"anterior_{e['id']}.json")))
            e["modo"] = "verificacion"
    comun.guardar(os.path.join(rd, "checks.json"), res)
    comun.guardar(os.path.join(rd, "encargos.json"), encs)
    print(f"{et} r{ronda}{' (verificación)' if ant else ''}: 0 fallas automáticas, {len(res['avisos'])} avisos, "
          f"{len(encs)} encargos → {rel(rd, comun.RAIZ)}")
    return rd


def texto_lanzar(rd, e):
    enc = os.path.join(rd, "encargos.json")
    verif = (f"5. Es una RONDA DE VERIFICACIÓN: en tus materiales está anterior_{e['id']}.json con lo que te toca verificar. Para cada id di "
             f"si quedó arreglado (sección 'Ronda de verificación' de comun.md). Problemas nuevos, sólo si son bloqueantes de la lista.\n"
             if e.get("modo") == "verificacion" else "")
    return (f"Eres el AUDITOR independiente de la cuenta \"Nadie te explica\". No conoces a quien hizo este trabajo ni su opinión: "
            f"juzgas sólo los materiales. Repo: {comun.RAIZ}.\n"
            f"1. Lee {comun.RAIZ}/tools/auditor/prompts/comun.md y {comun.RAIZ}/{e['prompt']}.\n"
            f"2. Tu encargo es el de id \"{e['id']}\" en {enc} (alcance, materiales y contexto; las rutas son relativas al repo). "
            f"Los chequeos automáticos de esta ronda están en {os.path.join(rd, 'checks.json')}.\n"
            f"3. Mira TODOS los materiales de tu encargo. No abras otros archivos del repo ni otras carpetas de auditoría.\n"
            f"4. Escribe tu resultado en {os.path.join(rd, e['salida'])} con el formato JSON de comun.md, una sola vez, al final.\n"
            f"{verif}"
            f"Responde con una línea: tu veredicto y el número de bloqueantes.")


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


def _tipo(p):
    t = str(p.get("tipo") or "").upper().strip()
    return t if t in BLOQUEANTES else None


def cerrar(a):
    et = comun.etapa_id(a.etapa)
    rd, ronda, encs, listos, faltan = estado(a, imprimir=False)
    if faltan:
        sys.exit(f"faltan encargos: {', '.join(e['id'] for e in faltan)} (relanzarlos con 'lanzar')")
    ch = comun.leer(os.path.join(rd, "checks.json"), {"fallas": [], "avisos": []})
    ant = comun.leer(os.path.join(rd, "materiales", "anterior.json"))
    notas, problemas, sugerencias, verif = {}, [], [], []
    for e in listos:
        o = comun.leer(os.path.join(rd, e["salida"]))
        for c, v in (o.get("notas") or {}).items():
            n = v["nota"] if isinstance(v, dict) else v
            pq = v.get("por_que", "") if isinstance(v, dict) else ""
            x = notas.setdefault(c, {"notas": [], "por_que": "", "min": None, "de": ""})
            if n is None:
                x["por_que"] = x["por_que"] or "no aplica"
                continue
            x["notas"].append(n)
            if x["min"] is None or n < x["min"]:
                x.update(min=n, por_que=pq, de=e["id"])
        for p in o.get("problemas", []):
            p["de"] = e["id"]
            if p.get("bloqueante") and _tipo(p):
                p["tipo"] = _tipo(p)
                problemas.append(p)
            else:
                if p.get("bloqueante"):
                    p["nota_auditor"] = "marcado bloqueante sin un tipo B1–B11: queda como sugerencia"
                p["bloqueante"] = False
                sugerencias.append(p)
        for v in o.get("verificacion", []) or []:
            v["de"] = e["id"]
            verif.append(v)
    # verificación: lo que sigue sin arreglar vuelve; un bloqueante sin arreglar sigue siendo bloqueante
    pendientes = []
    if ant:
        # cuenta sólo lo que dijo el revisor asignado a cada cosa (otro que la ve en el contacto a 1 cuadro/s no la pisa)
        estado_id = {v.get("id"): bool(v.get("arreglado")) for v in verif if v.get("de") == next(
            (x.get("asignado") for x in ant if x["id"] == v.get("id")), v.get("de"))}
        for x in ant:
            if not estado_id.get(x["id"], False):
                y = dict(x, que=f"[{x['id']} sin arreglar] {x['que']}", de="verificación")
                pendientes.append(y)
                (problemas if x.get("bloqueante") and x.get("tipo") in BLOQUEANTES else sugerencias).append(
                    dict(y, bloqueante=bool(x.get("bloqueante") and x.get("tipo") in BLOQUEANTES)))
    for f in reversed(ch["fallas"]):      # toda falla automática impide aprobar: va con los bloqueantes
        problemas.insert(0, {"prioridad": 0, "bloqueante": bool(f.get("bloqueante")), "tipo": "auto",
                             "que": "[automático] " + f["que"], "donde": f.get("evidencia", ""), "arreglo": "cumplir la regla", "de": "checks"})
    sugerencias.sort(key=lambda p: (p.get("prioridad", 9), str(p.get("plano") or "")))
    medias = {c: (round(sum(v["notas"]) / len(v["notas"]), 1) if v["notas"] else None) for c, v in notas.items()}
    con_nota = [m for m in medias.values() if m is not None]
    promedio = round(sum(con_nota) / len(con_nota), 2) if con_nota else None
    # ningún revisor bajo el mínimo en ningún criterio (el promedio no esconde al revisor que sí miró)
    bajos = {c: v["min"] for c, v in notas.items() if v["min"] is not None and v["min"] < NOTA_MIN}
    falta_nota = [c for c in CRITERIOS.get(et, []) if c not in notas and encs]
    auto_fallas = [f for f in ch["fallas"]]
    aprobado = (not auto_fallas and not [p for p in problemas if p.get("bloqueante") or p.get("de") == "checks"] and not bajos and not falta_nota
                and (promedio is None or promedio >= PROMEDIO_MIN))
    # planos que fallan dos veces → se simplifican o se reemplazan (no se sigue parchando)
    dos_veces = sorted({str(x.get("plano")) for x in pendientes if x.get("bloqueante") and x.get("plano") not in (None, "")})
    salida = (not aprobado and ronda >= MAX_RONDAS)
    ver = {"etapa": et, "ronda": ronda, "veredicto": "APROBADO" if aprobado else "NO APROBADO",
           "promedio": promedio, "notas": {c: {"nota": medias[c], "min": v["min"], "por_que": v["por_que"], "de": v["de"]} for c, v in notas.items()},
           "problemas": problemas, "sugerencias": sugerencias, "verificacion": verif, "avisos": ch.get("avisos", []),
           "criterios_sin_nota": falta_nota, "planos_dos_veces": dos_veces, "reemplazo": salida}
    comun.guardar(os.path.join(rd, "veredicto.json"), ver)
    L = [f"# {et} · ronda {ronda} · **{ver['veredicto']}**", ""]
    if promedio is not None:
        L += [f"Promedio **{promedio}** (mínimo {PROMEDIO_MIN:g}; ningún revisor bajo {NOTA_MIN} en ningún criterio).", ""]
    if salida:
        L += [f"**{MAX_RONDAS} rondas sin aprobar: no se abre otra.** Lo que sigue fallando se simplifica o se reemplaza por una "
              f"plantilla del kit y el video sigue: en el animatic, la puerta 7 revisa bloqueantes en todo el render final (incluidos "
              f"los planos simplificados). Si es guion o storyboard, se cambia la idea o se le pregunta a Tomás.", ""]
    if dos_veces:
        L += [f"**Planos que fallaron dos veces → simplificar o reemplazar (no parchar otra vez):** {', '.join(dos_veces)}", ""]
    if notas:
        L += ["| criterio | nota (promedio) | más baja | por qué (la más baja) |", "|---|---|---|---|"]
        for c, v in ver["notas"].items():
            n = v["nota"]
            mn = v["min"]
            L.append(f"| {c} | {'—' if n is None else n} | {'—' if mn is None else ('**' + str(mn) + '**' if mn < NOTA_MIN else mn)} | {v['por_que']} |")
        L.append("")
    if falta_nota:
        L += [f"Criterios sin nota (cuentan como no aprobados): {', '.join(falta_nota)}", ""]
    donde = lambda p: " · ".join(str(x) for x in (p.get("plano") and f"plano {p['plano']}", p.get("segundo") and f"{p['segundo']} s", p.get("donde")) if x)
    L += ["## Bloqueantes y fallas automáticas (impiden aprobar)", ""] + ([f"{i}. {'🛑' if p.get('bloqueante') else '❌'} {('[' + p['tipo'] + '] ') if p.get('tipo') not in (None, 'auto') else ''}{p['que']}"
                                    + (f" — {donde(p)}" if donde(p) else "") + (f". **Arreglo:** {p['arreglo']}" if p.get("arreglo") else "")
                                    for i, p in enumerate(problemas, 1)] or ["Ninguno."])
    L += ["", f"## Sugerencias (las {TOP_SUGERENCIAS} más importantes; el resto queda en veredicto.json)", ""]
    L += [f"{i}. {p['que']}" + (f" — {donde(p)}" if donde(p) else "") + (f". **Arreglo:** {p['arreglo']}" if p.get("arreglo") else "")
          for i, p in enumerate(sugerencias[:TOP_SUGERENCIAS], 1)] or ["Ninguna."]
    if ant:
        L += ["", "## Verificación de la ronda anterior", "", "| id | qué | arreglado |", "|---|---|---|"]
        L += [f"| {x['id']} | {x['que'][:90]} | {'sí' if estado_id.get(x['id'], False) else '**no**'} |" for x in ant]
    if ch.get("avisos"):
        L += ["", "## Avisos automáticos", ""] + [f"- {x['que']}" + (f" · {x['evidencia']}" if x.get("evidencia") else "") for x in ch["avisos"][:12]]
        if len(ch["avisos"]) > 12:
            L.append(f"- … y {len(ch['avisos']) - 12} más en checks.json")
    open(os.path.join(rd, "veredicto.md"), "w").write("\n".join(L) + "\n")
    # resumen por episodio
    base = os.environ.get("AUDITORIA_BASE") or os.path.join(comun.ep_dir(a.ep), "auditoria")
    filas = []
    for d in sorted(glob.glob(os.path.join(base, "*", "r*", "veredicto.json"))):
        v = comun.leer(d)
        filas.append(f"| {v['etapa']} | r{v['ronda']} | {v['veredicto']} | {sum(1 for p in v['problemas'] if p.get('bloqueante'))} | "
                     f"{len(v['problemas']) + len(v.get('sugerencias', []))} |")
    open(os.path.join(base, "ESTADO.md"), "w").write("| etapa | ronda | veredicto | bloqueantes | observaciones |\n|---|---|---|---|---|\n" + "\n".join(filas) + "\n")
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
    ap.add_argument("--meta", help="carpeta meta/ del render (ojos de cada personaje por cuadro → 'cara tapada')")
    ap.add_argument("--graficos", help="graficos.json del post (cajas de lupas, recuadros, píldoras)")
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
    ap.add_argument("--fuentes", help="extractos de fuentes_<ep>.md (prerelease <epNN>-fuentes, workflow fuentes.yml)")
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--forzar", help="abrir una ronda más allá del máximo (motivo; queda en el veredicto)")
    ap.add_argument("--cambiados", help="r2 del animatic: planos re-renderizados (coma), además de los que tenían algo que verificar")
    ap.add_argument("--sin-personajes", action="store_true", help="video sin personajes: no exige datos de ojos")
    a = ap.parse_args()
    {"preparar": preparar, "estado": estado, "lanzar": lanzar, "cerrar": cerrar}[a.accion](a)
