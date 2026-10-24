"""Auditor de "Nadie te explica" (proceso v2, 21-oct-2026): prepara cada revisión, dice qué encargos faltan y cierra el veredicto.

  python3 tools/auditor/auditar.py preparar <ep> <etapa> [opciones]   → chequeos + materiales + encargos (ronda nueva)
  python3 tools/auditor/auditar.py estado   <ep> <etapa> [--ronda N]  → encargos listos / faltantes (los faltantes se relanzan)
  python3 tools/auditor/auditar.py cerrar   <ep> <etapa> [--ronda N]  → veredicto.md + veredicto.json (sale 0 si APROBADO)
  python3 tools/auditor/auditar.py lanzar   <ep> <etapa> [--ronda N]  → imprime el texto exacto para lanzar cada subagente faltante

Etapas: 1 guion · 2 voz · 3 storyboard · 4 cuadros · 5 kling · 6 animatic · 7 final · 8 paquete · P proceso.
Reglas v2 (docs/AUDITOR.md): sin ronda si falla lo automático, máx. 2 rondas (la 2.ª verifica), 1 revisor por cada 10 planos + 1 global,
bloqueantes sólo de la lista cerrada (B1–B14), aprueba con promedio ≥ 8 y ningún criterio bajo 7, y se muestran sólo las
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
REALISMO_MIN = float(TOPES["realismo_min"])   # en un episodio realista el realismo pide ≥ 8 por sí solo (estilos.md)


COMPRENSION_MIN = float(TOPES.get("comprension_min", 8))   # Ep. 6: si no se entiende corrido y sin sonido, no sale


def nota_min(c):
    return REALISMO_MIN if c == "realismo" else COMPRENSION_MIN if c == "comprension" else NOTA_MIN
BLOQUEANTES = {   # lista cerrada: un "bloqueante" sin uno de estos tipos se trata como sugerencia
    "B1": "piezas que se atraviesan o flotan a la vista (dedos, objetos, cuerpos, hojas, frutos)",
    "B2": "algo aparece, desaparece o cambia de forma/color de golpe sin querer; utilería técnica a la vista",
    "B3": "pantalla vacía o plano muerto más de 0,2 s",
    "B4": "personaje distinto a su ficha o deformado",
    "B5": "cara u ojos tapados por un gráfico o subtítulo; subtítulo ilegible, fuera de zona o desfasado",
    "B6": "dato falso, sin respaldo, o fuente que no dice eso",
    "B7": "interior del cuerpo confuso (más de un foco, cortes, cráneo, órganos inventados)",
    "B8": "lista negra (retos peligrosos, tragedias recientes, política, religión, salud como indicación, marcas o personajes ajenos)",
    "B9": "estilo rechazado o imagen rota (quemado, lavado, low-poly, rayos X o neón 2D); en un episodio realista, un plano o "
          "personaje que es claramente dibujo animado (realismo ≤ 5; las capas de explicación encima no cuentan)",
    "B10": "faltas de ortografía o tildes en pantalla o en los textos",
    "B11": "algo clave cortado por el borde o bajo la interfaz de la app (y > 1250) mientras la voz lo nombra",
    # Ep. 6 (vergüenza máxima, 24-oct-2026): cada plano pasaba solo y el video no se entendía
    "B12": "un tramo de ≥ 1 s donde no se reconoce qué se está viendo (desenfocado, oscuro, sujeto cortado o tapado, un detalle "
           "sin contexto) o que alguien sin sonido no entiende",
    "B13": "lo que la voz dice que pasa no se ve: la acción del gancho, la mecánica que se explica o el remate no aparecen en la imagen",
    "B14": "sin plano de situación en los primeros 3 s (quién, dónde y la acción del gancho) o un personaje del relato que nunca "
           "aparece reconocible; escenas pegadas sin un espacio que las una",
}
CRITERIOS = {
    "1-guion": ["precision", "gancho", "claridad", "compartible"],
    "2-voz": ["pronunciacion", "ritmo"],
    "3-storyboard": ["foco", "ritmo", "viabilidad", "gancho_visual"],
    "4-cuadros": ["belleza", "personaje", "manos", "anatomia"],
    "5-kling": ["manos", "objeto", "personaje", "estabilidad"],
    "6-animatic": ["gancho", "claridad", "ritmo", "belleza", "animacion", "subtitulos", "audio", "precision", "comprension"],
    "7-final": [],                 # sólo bloqueantes
    "8-paquete": ["textos", "cumplimiento"],
    "P-proceso": [],
}
# Estilo realista (estilo.json, decisión de Tomás 22-oct-2026): estas etapas suman el criterio "realismo" (estilos.md).
REALISMO_EN = ("4-cuadros", "6-animatic")
CON_ESTILO = ("3-storyboard", "4-cuadros", "5-kling", "6-animatic", "7-final", "8-paquete")   # etapas que dependen del look
CON_FICHA = ("4-cuadros", "5-kling", "6-animatic", "7-final")                                  # etapas que comparan personajes


def criterios(et, estilo="animado"):
    base = list(CRITERIOS.get(et, []))
    if estilo == "realista" and et in REALISMO_EN:
        base.append("realismo")
    return base


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
    # realista: los delatores de la maqueta también se verifican (todos, no sólo los 5 primeros) → ids D1, D2…
    for i, d in enumerate(v.get("delatores", []) or [], 1):
        out.append({"id": f"D{i}", "bloqueante": False, "tipo": None, "plano": d.get("plano") or d.get("cuadro"),
                    "segundo": d.get("segundo"), "que": f"[delator · {d.get('zona', '')}] {d.get('que', '')}",
                    "arreglo": d.get("arreglo"), "de": d.get("de")})
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
    est = comun.estilo(ep_d)     # animado o realista (estilo.json): el auditor juzga contra el estilo que eligió el episodio
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
        lista = materiales.cuadros(md, imgs, ficha, recortes=(est["estilo"] == "realista"))
        res = checks.cuadros(lista, est["estilo"])
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
        if est["estilo"] == "realista" and est["referencias"]:      # fotos reales para comparar el realismo
            extra += [R(os.path.join(md, x)) for x in materiales.referencias(md, est["referencias"])]
        recs = [R(os.path.join(md, n)) for c in lista for n in c.get("recortes", [])]     # realista: franjas a resolución completa
        encs.append(encargo("cuadros", "4-cuadros.md", ", ".join(c["cuadro"] for c in lista),
                            [R(os.path.join(md, c["archivo"])) for c in lista] + recs + extra + [R(os.path.join(md, "cuadros.json"))],
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
        f5 = a.ficha or comun.ficha(ep_d)
        if f5:
            mats.append(R(f5))
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
        ficha = a.ficha or comun.ficha(ep_d)
        if ficha:
            import shutil
            shutil.copy(ficha, os.path.join(md, "ficha.jpg"))
            comunes.append(R(os.path.join(md, "ficha.jpg")))
        if est["estilo"] == "realista" and est["referencias"]:
            comunes += [R(os.path.join(md, x)) for x in materiales.referencias(md, est["referencias"])]
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
            # Ep. 6 (vergüenza máxima): un espectador que ve el video ENTERO corrido, sin guion, y dice qué entendió; recién
            # después lee el guion y marca lo que la voz dice y no se ve. Va en todas las rondas (el video entero cambia).
            sec = comun.leer(os.path.join(md, "secuencia.json"), {}) or {}
            encs.append(encargo("espectador", "6-espectador.md", "el video completo corrido, como lo ve la gente (sin guion primero)",
                                [R(os.path.join(md, h)) for h in sec.get("hojas", [])] + [R(os.path.join(md, "cuadro0.jpg"))],
                                ctx_base, {"despues": [R(os.path.join(ep_d, "guion.md")), R(os.path.join(md, "subtitulos.md"))],
                                           "criterios_propios": ["comprension", "gancho", "claridad"]}))
        else:
            encs.append(encargo("final", "7-final.md", "render final: sólo bloqueantes",
                                glob_mats + [R(os.path.join(md, p["tira"])) for p in P] + evs + [R(os.path.join(md, "planos.json"))], ctx))
    elif et == "8-paquete":
        res = checks.paquete(ep_d, a.url)
        # Ep. 6 (vergüenza máxima): se le mandó a Tomás un video que la puerta 6 NO aprobó. Sin 6 y 7 APROBADO no hay paquete.
        vs = {}
        for et_q in ("6-animatic", "7-final"):
            rq, _n = comun.ronda_dir(a.ep, et_q)
            vs[et_q] = (rq, comun.leer(os.path.join(rq, "veredicto.json"), {}) or {})
        for et_q, (rq, vv) in vs.items():
            vq = vv.get("veredicto")
            # la 6 vale si aprobó, o si sólo le quedaron bloqueantes puntuales que la 7 ya verificó en el render final
            ok6 = et_q == "6-animatic" and vv.get("solo_bloqueantes") and vs["7-final"][1].get("veredicto") == "APROBADO"
            if vq != "APROBADO" and not ok6:
                res["fallas"].append({"que": f"la puerta {et_q} no está APROBADA (último veredicto: {vq or 'sin revisión'}): el video no se "
                                             "empaqueta ni se le manda a Tomás; se rehace o se descarta (docs/AUDITOR.md)",
                                      "evidencia": rel(rq, comun.RAIZ), "bloqueante": True})
        encs.append(encargo("paquete", "8-paquete.md", "textos de publicación",
                            [R(os.path.join(ep_d, "entrega", "caption.md")), R(os.path.join(ep_d, "guion.md"))],
                            ctx_base + ["docs/MANUAL_PRODUCCION.md"]))
    elif et == "P-proceso":
        import proceso
        res = proceso.auditar(a.ep, proceso.ts(a.desde), proceso.ts(a.hasta))
    if et in CON_ESTILO:
        res.setdefault("datos", {})["estilo"] = est["estilo"]
        for x in est["errores"]:
            res["fallas"].append({"que": x, "evidencia": "estilo.json", "bloqueante": True})
        if et in ("4-cuadros", "6-animatic", "7-final"):
            res["avisos"] += [{"que": x, "evidencia": "estilo.json"} for x in est["avisos"]]
        if not est["declarado"] and not est["errores"] and not comun.es_legado(ep_d):
            res["fallas"].append({"que": "el episodio no declara su estilo: crear estilo.json en la carpeta del episodio con "
                                         "{\"estilo\": \"animado\"} o {\"estilo\": \"realista\"} (docs/AUDITOR.md, 'Estilo del episodio')",
                                  "evidencia": "", "bloqueante": True})
        if est["estilo"] == "realista" and not est["referencias"] and et in ("4-cuadros", "6-animatic"):
            res["avisos"].append({"que": "estilo realista sin referencias (fotos reales en estilo.json → referencias): el revisor "
                                         "juzga el realismo sin poder comparar", "evidencia": ""})
        for e in encs:     # lista nueva por encargo (en el animatic varios encargos comparten la misma lista de contexto)
            e["estilo"] = est["estilo"]
            e["contexto"] = [c for c in e["contexto"] if c != "tools/auditor/prompts/estilos.md"] + ["tools/auditor/prompts/estilos.md"]
    if et in CON_FICHA and not comun.es_legado(ep_d) and not (a.ficha or comun.ficha(ep_d)) and not a.sin_personajes:
        res["fallas"].append({"que": "falta ficha.jpg en la carpeta del episodio (los personajes de ESTE episodio; el protagonista "
                                     "viejo ya no sirve de respaldo) o pasar --sin-personajes si el video no tiene personajes",
                              "evidencia": "", "bloqueante": True})
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
          f"{len(encs)} encargos{(' · estilo ' + est['estilo']) if et in CON_ESTILO else ''} → {rel(rd, comun.RAIZ)}")
    return rd


def texto_lanzar(rd, e):
    enc = os.path.join(rd, "encargos.json")
    verif = (f"5. Es una RONDA DE VERIFICACIÓN: en tus materiales está anterior_{e['id']}.json con lo que te toca verificar. Para cada id di "
             f"si quedó arreglado (sección 'Ronda de verificación' de comun.md). Problemas nuevos, sólo si son bloqueantes de la lista.\n"
             if e.get("modo") == "verificacion" else "")
    estilo = (f"; y en {comun.RAIZ}/tools/auditor/prompts/estilos.md la sección del estilo de este episodio: "
              f"**{e['estilo'].upper()}** (juzga contra ese estilo, no contra el de otros videos)" if e.get("estilo") else "")
    return (f"Eres el AUDITOR independiente de la cuenta \"Nadie te explica\". No conoces a quien hizo este trabajo ni su opinión: "
            f"juzgas sólo los materiales. Repo: {comun.RAIZ}.\n"
            f"1. Lee {comun.RAIZ}/tools/auditor/prompts/comun.md y {comun.RAIZ}/{e['prompt']}{estilo}.\n"
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
    # el estilo con que se preparó la ronda (queda en cada encargo); si no está (rondas viejas), el del episodio hoy
    estilo = next((e["estilo"] for e in encs if e.get("estilo")), None) or comun.estilo(comun.ep_dir(a.ep))["estilo"]
    notas, problemas, sugerencias, verif, delatores = {}, [], [], [], []
    for e in listos:
        o = comun.leer(os.path.join(rd, e["salida"]))
        for c, v in (o.get("notas") or {}).items():
            if c == "realismo" and "realismo" not in criterios(et, estilo):
                continue      # en un episodio animado (o en otra etapa) el realismo no se pide: no baja ni sube nada
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
                    p["nota_auditor"] = "marcado bloqueante sin un tipo B1–B14: queda como sugerencia"
                p["bloqueante"] = False
                sugerencias.append(p)
        for v in o.get("verificacion", []) or []:
            v["de"] = e["id"]
            verif.append(v)
        for d in o.get("delatores", []) or []:          # realista: TODO lo que delata la maqueta (sin tope de 8)
            d["de"] = e["id"]
            delatores.append(d)
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
    bajos = {c: v["min"] for c, v in notas.items() if v["min"] is not None and v["min"] < nota_min(c)}
    # el realismo de un episodio realista necesita una nota de verdad: "no aplica" no cuenta
    falta_nota = [c for c in criterios(et, estilo) if (c not in notas or (c in ("realismo", "comprension") and not notas[c]["notas"])) and encs]
    auto_fallas = [f for f in ch["fallas"]]
    aprobado = (not auto_fallas and not [p for p in problemas if p.get("bloqueante") or p.get("de") == "checks"] and not bajos and not falta_nota
                and (promedio is None or promedio >= PROMEDIO_MIN))
    # planos que fallan dos veces → se simplifican o se reemplazan (no se sigue parchando)
    dos_veces = sorted({str(x.get("plano")) for x in pendientes if x.get("bloqueante") and x.get("plano") not in (None, "")})
    salida = (not aprobado and ronda >= MAX_RONDAS)
    ver = {"etapa": et, "ronda": ronda, "estilo": estilo, "veredicto": "APROBADO" if aprobado else "NO APROBADO",
           "promedio": promedio, "notas": {c: {"nota": medias[c], "min": v["min"], "por_que": v["por_que"], "de": v["de"]} for c, v in notas.items()},
           "problemas": problemas, "sugerencias": sugerencias, "verificacion": verif, "avisos": ch.get("avisos", []),
           "criterios_sin_nota": falta_nota, "planos_dos_veces": dos_veces, "reemplazo": salida, "delatores": delatores,
           # sólo fallan bloqueantes puntuales (las notas y el promedio llegan): se simplifican esos planos y la puerta 7 decide.
           # Si falla una nota (comprensión, realismo, cualquiera) o el promedio, el video NO sigue ni se le manda a Tomás.
           "solo_bloqueantes": bool(not auto_fallas and not bajos and not falta_nota and (promedio is None or promedio >= PROMEDIO_MIN)),
           "parar_y_preguntar": bool(salida and "realismo" in criterios(et, estilo) and ("realismo" in bajos or "realismo" in falta_nota))}
    comun.guardar(os.path.join(rd, "veredicto.json"), ver)
    L = [f"# {et} · ronda {ronda} · **{ver['veredicto']}**" + (f" · estilo {estilo}" if et in CON_ESTILO else ""), ""]
    if promedio is not None:
        L += [f"Promedio **{promedio}** (mínimo {PROMEDIO_MIN:g}; ningún revisor bajo {NOTA_MIN} en ningún criterio"
              + (f"; realismo: ningún revisor bajo {REALISMO_MIN:g}" if "realismo" in criterios(et, estilo) else "") + ").", ""]
    falla_realismo = "realismo" in criterios(et, estilo) and ("realismo" in bajos or "realismo" in falta_nota)
    if salida and falla_realismo:
        # el kit es de personajes animados y la puerta 7 no mide realismo: seguir sería publicar un video "realista" que no lo es
        L += [f"**{MAX_RONDAS} rondas sin llegar a realismo {REALISMO_MIN:g}: no se abre otra y el video NO sigue.** No se reemplaza "
              f"por plantillas del kit (son animadas). Se para y se le pregunta a Tomás con opciones (otra vía para lo que se ve "
              f"de juguete, por ejemplo Kling o sacar a la persona de cuadro; aceptar el nivel actual; o cambiar el episodio a animado).", ""]
    elif salida and et == "6-animatic" and not ver["solo_bloqueantes"]:
        L += [f"**{MAX_RONDAS} rondas sin aprobar y no llegan las notas (o el promedio): el video NO sigue y NO se le manda a Tomás** "
              f"(Ep. 6, vergüenza máxima: se le mandó uno así). Se le explica por qué en dos líneas y se propone un reemplazo: otra "
              f"idea o rehacer desde el storyboard. Nada de 'mandarlo con opciones'.", ""]
    elif salida:
        L += [f"**{MAX_RONDAS} rondas sin aprobar: no se abre otra.** Lo que sigue fallando son bloqueantes puntuales: esos planos se "
              f"simplifican o se reemplazan por una plantilla del kit y la puerta 7 revisa bloqueantes en todo el render final. Si es "
              f"guion o storyboard, se cambia la idea o se le pregunta a Tomás.", ""]
    if dos_veces:
        L += [f"**Planos que fallaron dos veces → simplificar o reemplazar (no parchar otra vez):** {', '.join(dos_veces)}", ""]
    if notas:
        L += ["| criterio | nota (promedio) | más baja | por qué (la más baja) |", "|---|---|---|---|"]
        for c, v in ver["notas"].items():
            n = v["nota"]
            mn = v["min"]
            L.append(f"| {c} | {'—' if n is None else n} | {'—' if mn is None else ('**' + str(mn) + '**' if mn < nota_min(c) else mn)} | {v['por_que']} |")
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
    if delatores:
        L += ["", "## Delatores del realismo (lista completa: se arreglan TODOS antes de la ronda siguiente)", ""]
        L += [f"- **{d.get('cuadro') or d.get('plano') or '?'}** · {d.get('zona', '')}: {d.get('que', '')}"
              + (f" → {d['arreglo']}" if d.get("arreglo") else "") for d in delatores]
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
