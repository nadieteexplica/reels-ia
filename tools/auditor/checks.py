"""Chequeos automáticos por etapa (sin IA). Si alguno falla, la etapa es NO APROBADO aunque el revisor la apruebe.
Cada función devuelve {"fallas": [...], "avisos": [...], "datos": {...}}. Una falla es una regla del manual que no se cumple;
un aviso es algo que el revisor tiene que mirar con cuidado.
"""
import difflib, json, os, re, unicodedata

import comun

PROHIBIDO = ["en este video", "sígueme", "siguenos", "síguenos", "dale like", "no vas a creer", "suscríbete", "link en la bio"]
LISTA_NEGRA = ["polític", "elecci", "partido", "religi", "dios", "iglesia", "reto", "challenge", "suicid", "atentado", "terremoto de",
               "tragedia", "muert", "arma", "droga", "dosis", "medicamento", "pulpo"]
SALUD = ["dolor", "cerebro", "sangre", "nervio", "corazón", "pulmón", "riñón", "enfermedad", "síntoma", "médic", "salud"]
NUMEROS = {"uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "trece", "catorce",
           "quince", "veinte", "treinta", "cuarenta", "cincuenta", "cien", "mil", "millón", "millones", "medio", "mitad"}
RES = lambda: {"fallas": [], "avisos": [], "datos": {}}


def _f(r, que, evidencia="", bloqueante=False):
    r["fallas"].append({"que": que, "evidencia": evidencia, "bloqueante": bloqueante})


def _a(r, que, evidencia=""):
    r["avisos"].append({"que": que, "evidencia": evidencia})


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def palabras(texto):
    return [w for w in re.split(r"\s+", texto.strip()) if re.search(r"\w", w)]


def seccion(md, titulo):
    m = re.search(rf"^##+\s*{titulo}[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


def texto_guion(ep_d):
    md = open(os.path.join(ep_d, "guion.md")).read()
    return md, seccion(md, "Guion")


# ---------------- 1. guion ----------------
def guion(ep_d, publicados=None):
    r = RES()
    md, txt = texto_guion(ep_d)
    if not txt:
        _f(r, "guion.md no tiene la sección '## Guion'", bloqueante=True)
        return r
    ws = palabras(txt)
    n = len(ws)
    est = n / 2.97
    r["datos"].update({"palabras": n, "duracion_estimada_s": round(est, 1)})
    if not 190 <= n <= 215:
        _f(r, f"el guion tiene {n} palabras (190–215)")
    if not 62 <= est <= 75:
        _f(r, f"duración estimada {est:.1f} s fuera de 62–75 s (a 2,97 palabras/s)")
    frases = [f.strip() for f in re.split(r"(?<=[.!?:])\s+", txt.replace("\n", " ")) if f.strip()]
    largas = [(len(palabras(f)), f) for f in frases if len(palabras(f)) > 14]
    for k, f in largas:
        (_f if k > 18 else _a)(r, f"frase de {k} palabras (máx. 14)", f)
    pausas = txt.count("...") + txt.count("…")
    r["datos"]["pausas"] = pausas
    if not 2 <= pausas <= 4:
        _a(r, f"{pausas} pausas '...' (el manual pide 2–4)")
    t = norm(txt)
    for p in PROHIBIDO:
        if norm(p) in t:
            _f(r, f"frase prohibida en el guion: '{p}'", bloqueante=True)
    for p in LISTA_NEGRA:
        if re.search(r"\b" + norm(p), t):
            _a(r, f"palabra de la lista negra (revisar tema): '{p}'")
    if any(norm(s) in t for s in SALUD) and "consult" not in t:
        _a(r, "tema de salud sin 'si te pasa seguido, consulta' (revisar si corresponde)")
    # fuentes
    fuentes = seccion(md, "Fuentes")
    urls = re.findall(r"https?://[^\s)>\]]+", fuentes)
    dominios = sorted({re.sub(r"^www\.", "", u.split("/")[2]) for u in urls})
    no_wiki = [d for d in dominios if "wikipedia" not in d]
    r["datos"]["fuentes"] = dominios
    if len(no_wiki) < 2:
        _f(r, f"menos de 2 fuentes independientes con URL (hay {len(no_wiki)}; Wikipedia no cuenta)", bloqueante=True)
    ver = seccion(md, "Verificaci")
    filas = [l for l in ver.splitlines() if l.startswith("|") and not re.match(r"^\|\s*-", l) and "Afirmaci" not in l]
    r["datos"]["afirmaciones_verificadas"] = len(filas)
    if not filas:
        _f(r, "no hay tabla de verificación por afirmación", bloqueante=True)
    for l in filas:
        cel = [c.strip() for c in l.strip("|").split("|")]
        if len(cel) < 2 or not cel[1]:
            _f(r, "afirmación sin fuente en la tabla de verificación", l, bloqueante=True)
    # cifras del guion que no aparecen en la verificación
    vn = norm(ver)
    for w in ws:
        x = norm(w).strip(".,;:!?¡¿…\"'()")
        if (re.search(r"\d", x) or x in NUMEROS) and x not in vn:
            _a(r, f"cifra '{x}' sin fuente al lado en la verificación")
    # puntaje de la idea
    m = re.search(r"puntaje[^\d]{0,20}(\d+(?:[.,]\d+)?)", md, re.I)
    linea = "historias" if re.search(r"l[ií]nea:\s*historias", md, re.I) else "datos"
    minimo = 25 if linea == "historias" else 32
    if not m:
        _f(r, f"guion.md no anota el puntaje de la idea (IDEAS.md §2, mínimo {minimo} en {linea})")
    elif float(m.group(1).replace(",", ".")) < minimo:
        _f(r, f"puntaje {m.group(1)} bajo el mínimo {minimo} de la línea {linea}", bloqueante=True)
    if not re.search(r"(envi|mand|guard)", norm(md)):
        _a(r, "guion.md no dice para qué acción está pensado (enviar o guardar)")
    return r


# ---------------- 2. voz ----------------
def voz(ep_d, words_path, status_path=None, job=None, asr_path=None):
    r = RES()
    words = comun.leer(words_path, [])
    if not words:
        _f(r, f"no existe {words_path}", bloqueante=True)
        return r
    dur = words[-1]["e"]
    r["datos"]["duracion_voz_s"] = round(dur, 2)
    if not 62 <= dur + 0.4 <= 75:
        _f(r, f"la voz dura {dur:.1f} s (+0,4 de cola) fuera de 62–75 s", bloqueante=True)
    largas = [(w["w"], round(w["e"] - w["s"], 2), w["s"]) for w in words[:-1] if w["e"] - w["s"] > 1.2 and "..." not in w["w"]]
    for w, d, s in largas:
        _f(r, f"la palabra '{w}' dura {d} s (máx. 1,2)", f"{s:.2f} s")
    mp3 = os.path.join(comun.RAIZ, "out", "tts", os.path.basename(ep_d) + ".mp3")
    sil = silencios(mp3) if os.path.exists(mp3) else []
    pausas = [("(silencio)", round(b - a_, 2), a_) for a_, b in sil if b - a_ > 1.0 and a_ > 0.2 and b < words[-1]["e"]] if sil else \
        [(words[i]["w"], round(words[i + 1]["s"] - words[i]["e"], 2), words[i]["e"]) for i in range(len(words) - 1)
         if words[i + 1]["s"] - words[i]["e"] > 1.0]
    for w, d, s in pausas:
        _a(r, f"pausa de {d} s después de '{w}'", f"{s:.2f} s")
    _md, txt = texto_guion(ep_d)
    if txt and len(palabras(txt)) != len(words):
        _f(r, f"words.json tiene {len(words)} palabras y el guion {len(palabras(txt))}", bloqueante=True)
    # ritmo por frase
    frase, t0 = [], words[0]["s"]
    for w in words:
        frase.append(w)
        if re.search(r"[.!?]$", w["w"]):
            d = w["e"] - t0
            ps = len(frase) / d if d > 0 else 0
            if len(frase) >= 4 and not 2.2 <= ps <= 3.8:
                _a(r, f"ritmo de {ps:.1f} palabras/s en '{' '.join(x['w'] for x in frase)[:60]}'", f"{t0:.2f} s")
            frase, t0 = [], w["e"]
    r["datos"]["palabras_por_s"] = round(len(words) / dur, 2)
    if status_path and os.path.exists(status_path):
        st = comun.leer(status_path, {})
        if job and isinstance(st.get(job), dict) and "error" in json.dumps(st[job]).lower():
            _f(r, f"out/status.json marca error en {job}", json.dumps(st[job])[:200], bloqueante=True)
        if "creditos_usados" in st:
            quedan = st["creditos_limite"] - st["creditos_usados"]
            r["datos"]["creditos_restantes"] = quedan
            if quedan < 8000:
                _f(r, f"quedan {quedan} créditos de ElevenLabs (avisar a Tomás y bajar a 2 videos)")
    # pronunciación: transcripción automática contra el guion
    if asr_path and os.path.exists(asr_path):
        asr = comun.leer(asr_path)
        a = [norm(x).strip(".,;:!?¡¿…\"'") for x in palabras(asr.get("texto", ""))]
        g = [norm(x).strip(".,;:!?¡¿…\"'") for x in palabras(txt)]
        sm = difflib.SequenceMatcher(None, g, a, autojunk=False)
        dif = [(" ".join(g[i1:i2]), " ".join(a[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        r["datos"]["asr_coincidencia"] = round(sm.ratio(), 3)
        r["datos"]["asr_diferencias"] = dif
        if sm.ratio() < 0.9:
            _f(r, f"la transcripción automática coincide sólo {sm.ratio() * 100:.0f} % con el guion")
        for gg, aa in dif:
            _a(r, f"se escucha '{aa}' donde el guion dice '{gg}'")
    else:
        _f(r, "falta la transcripción automática de la voz (workflow auditor-asr.yml): pronunciación sin verificar")
    return r


def silencios(mp3, db=-35, d=0.1):
    """Silencios reales del audio [(inicio, fin)], con ffmpeg silencedetect."""
    e = comun.sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mp3, "-af", f"silencedetect=noise={db}dB:d={d}", "-f", "null", "-"]).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", e)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", e)]
    return list(zip(ini, fin))


# ---------------- 3. storyboard ----------------
CON_MANOS = ["taza", "cono en su mano", "en la mano", "vasos con", "vaso con", "bombilla", "botella", "agarra", "toma de", "sostiene",
             "manos a la", "mano en la", "manos en la", "se toca", "drinking", "focus", "muerde", "lleva a la boca"]


def storyboard(ep_d, dur_voz=None):
    r = RES()
    p = os.path.join(ep_d, "storyboard.md")
    if not os.path.exists(p):
        _f(r, "no existe storyboard.md", bloqueante=True)
        return r
    md = open(p).read()
    lineas = [l for l in md.splitlines() if l.startswith("|")]
    head = next((l for l in lineas if re.search(r"\|\s*#\s*\|", l)), None)
    if not head:
        _f(r, "storyboard.md sin tabla con columna #", bloqueante=True)
        return r
    cols = [norm(c.strip()) for c in head.strip("|").split("|")]
    filas = []
    for l in lineas:
        cel = [c.strip() for c in l.strip("|").split("|")]
        if cel and re.match(r"^\d+$", cel[0]):
            filas.append(dict(zip(cols, cel)))
    r["datos"]["planos"] = len(filas)
    ci = lambda *ks: next((c for c in cols if any(k in c for k in ks)), None)
    c_t, c_pl, c_acc, c_or = ci("tiempo"), ci("plano"), ci("accion"), ci("origen", "fuente", "sale de")
    tiempos = []
    for f in filas:
        m = re.findall(r"(\d+(?:[.,]\d+)?)", f.get(c_t, ""))
        if len(m) >= 2:
            a, b = float(m[0].replace(",", ".")), float(m[1].replace(",", "."))
            tiempos.append((int(f[cols[0]]), a, b, f))
    for (n1, a1, b1, _), (n2, a2, b2, _) in zip(tiempos, tiempos[1:]):
        if a2 - b1 > 0.1:
            _f(r, f"hueco de {a2 - b1:.2f} s entre el plano {n1} y el {n2}")
    for n, a, b, f in tiempos:
        d = b - a
        acc = norm(f.get(c_acc, ""))
        if d > 2.5 and not re.search(r"(se arma|se transforma|aparece|crece|se llena|cuenta|sube|baja|se enciende|se ilumina)", acc):
            _a(r, f"plano {n} dura {d:.1f} s sin transformación escrita (nunca más de 2 s sin cambio)")
        if d < 0.8:
            _a(r, f"plano {n} dura {d:.2f} s (muy corto para leerse)")
    if tiempos and dur_voz and abs(tiempos[-1][2] - dur_voz) > 1.0:
        _a(r, f"el storyboard termina en {tiempos[-1][2]:.1f} s y la voz en {dur_voz:.1f} s")
    # escala: cambio cada 8–12 s
    if c_pl and tiempos:
        esc_prev, t_prev = None, 0.0
        for n, a, b, f in tiempos:
            e = (f.get(c_pl, "") or "?").split()[0][:1].upper()
            if e != esc_prev:
                if esc_prev and a - t_prev > 12:
                    _f(r, f"{a - t_prev:.0f} s sin cambiar de escala (planos hasta el {n})")
                esc_prev, t_prev = e, a
    # origen de cada plano: render, kling o biblioteca
    if not c_or:
        _f(r, "falta la columna 'Origen' (render / kling / biblioteca) en el storyboard")
        sospechosos = [int(f[cols[0]]) for f in filas if any(k in norm(" ".join(f.values())) for k in CON_MANOS)]
        r["datos"]["planos_con_manos_estimados"] = sospechosos
        if len(sospechosos) > 3:
            _f(r, f"{len(sospechosos)} planos con manos y objetos o manos en la cara ({sospechosos}): máximo 2–3 de Kling, el resto de la biblioteca o sin objeto")
    else:
        kl = [int(f[cols[0]]) for f in filas if "kling" in norm(f.get(c_or, ""))]
        r["datos"]["planos_kling"] = kl
        if len(kl) > 3:
            _f(r, f"{len(kl)} planos de Kling {kl} (máximo 3)", bloqueante=True)
        sin = [int(f[cols[0]]) for f in filas if any(k in norm(" ".join(f.values())) for k in CON_MANOS)
               and not re.search(r"(kling|bibliot)", norm(f.get(c_or, "")))]
        for n in sin:
            _f(r, f"plano {n} tiene manos con objeto o en la cara y sale de render (Blender no hace contacto de dedos)")
    # interior: cabeza de vidrio
    for n, a, b, f in tiempos:
        t = norm(" ".join(f.values()))
        if re.search(r"\bi\b|interior", norm(f.get(c_pl, ""))) or "cabeza" in t:
            if re.search(r"(corte de la cabeza|craneo|crane|parche|ojos de caricatura|cerebro a medias)", t):
                _f(r, f"plano {n}: interior con corte/cráneo (la regla es 'cabeza de vidrio' de perfil, sin cortes)", f.get(c_acc, "")[:80])
    if filas and re.search(r"(fade|fundido|desde negro)", norm(" ".join(filas[0].values()))):
        _f(r, "el plano 1 parte con fundido: el cuadro 0 tiene que ser una imagen fuerte", bloqueante=True)
    esp = len(re.findall(r"(whip|zoom de transici|rebobin|transici[oó]n especial)", norm(md)))
    if esp > 3:
        _a(r, f"{esp} menciones de transiciones especiales (máximo 2)")
    return r


# ---------------- 4. cuadros ----------------
def cuadros(lista):
    r = RES()
    for c in lista:
        w, h = (int(x) for x in c["res"].split("x"))
        if w < 720 or h < 1280:
            _f(r, f"{c['cuadro']}: resolución {c['res']} (mín. 720x1280)")
        if c["quemados_pct"] >= 3:
            _f(r, f"{c['cuadro']}: {c['quemados_pct']} % de píxeles quemados (máx. 3 %)", bloqueante=True)
        if c["brillo"] > 175 and c["saturacion"] < 70:
            _f(r, f"{c['cuadro']}: se ve lavado (brillo {c['brillo']}, saturación {c['saturacion']})")
        if c["brillo"] < 35:
            _a(r, f"{c['cuadro']}: muy oscuro (brillo {c['brillo']})")
    r["datos"]["cuadros"] = len(lista)
    return r


# ---------------- 5. kling ----------------
MALAS_KLING = ("pain", "hurt", "blood", "clench", "scream", "violent", "injur", "dolor", "sangre", "agony", "suffer")


def prompt_kling(r, nombre, prompt):
    """Instrucción de Kling: sin palabras de dolor o violencia (el filtro 'risk control' rechaza el clip) y con las reglas de manos."""
    p = norm(prompt)
    for mala in MALAS_KLING:
        if mala in p:
            _f(r, f"{nombre}: la instrucción usa '{mala}' (Kling rechaza el clip por 'risk control'; usar 'funny brain freeze', etc.)")
    if p and not re.search(r"(never (float|pass)|really touch|wrapped)", p):
        _a(r, f"{nombre}: la instrucción no exige contacto real de la mano ('fingers wrapped around…', 'never floats, never passes through…')")
    if p and "no text" not in p:
        _a(r, f"{nombre}: la instrucción no dice 'no text'")


def pedidos_kling(pedidos):
    r = RES()
    for n, x in pedidos.items():
        prompt_kling(r, n, x.get("prompt", ""))
    r["datos"]["pedidos"] = len(pedidos)
    return r


def kling(clips, planos_kling=None):
    r = RES()
    for c in clips:
        w, h = (int(x) for x in c["res"].split("x"))
        if min(w, h) < 720:
            _f(r, f"{c['clip']}: resolución {c['res']}")
        if not c.get("inicio"):
            _a(r, f"{c['clip']}: no se encontró el cuadro de partida")
        prompt_kling(r, c["clip"], c.get("prompt", ""))
    if planos_kling is not None:
        usados = sorted({k["plano"] for k in planos_kling})
        r["datos"]["planos_kling"] = usados
        if len(usados) > 3:
            _f(r, f"{len(usados)} planos del video salen de Kling {usados} (máximo 3)")
    r["datos"]["clips"] = len(clips)
    return r


# ---------------- 6. video ----------------
def video(mp4, mat, subs_log=None):
    r = RES()
    q = comun.sh(["python3", os.path.join(comun.RAIZ, "tools", "qa.py"), mp4])   # técnico: duración, formato, volumen, negros, congelados
    r["datos"]["qa"] = q.stdout.strip().splitlines()
    for l in q.stdout.splitlines():
        if l.startswith("❌"):
            _f(r, "QA técnico: " + l[2:], bloqueante=True)
    for e in mat["eventos"]:
        if e.get("bloqueante"):
            _f(r, f"{e['id']} {e['que']}", f"{e.get('t0', e.get('t'))}–{e.get('t1', '')} s, plano {e.get('plano')}", bloqueante=True)
    s = mat.get("subtitulos")
    if s is None:
        _f(r, "no hay registro de subtítulos (subs_log.json): no se puede comprobar sincronía ni zona")
    else:
        r["datos"]["subtitulos"] = {k: (len(v) if isinstance(v, list) else v) for k, v in s.items()}
        if s["faltan"]:
            tt = s.get("tiempos", {})
            pal = [tt.get(i, tt.get(str(i), [0, 0, "?"])) for i in s["faltan"]]
            planos_f = {next((p["plano"] for p in mat["planos"] if p["a"] <= w[0] < p["b"]), None) for w in pal}
            txt = " ".join(w[2] for w in pal)
            if len(pal) <= 4 and len(planos_f) == 1:   # p. ej. un nombre científico que va como título 3D (el manual oculta los subtítulos ahí)
                _a(r, f"'{txt}' no sale en subtítulos (plano {planos_f.pop()}): confirmar que está como título grande en pantalla", f"{pal[0][0]} s")
            else:
                _f(r, f"{len(s['faltan'])} palabras de words.json nunca aparecen en pantalla: '{txt[:80]}'", str(s["faltan"][:15]))
        if s["desfase"]:
            _f(r, f"{len(s['desfase'])} palabras no están en pantalla mientras se dicen", str(s["desfase"][:15]))
        if s["fuera_de_zona"]:
            _f(r, f"{len(s['fuera_de_zona'])} palabras con la caja fuera de x 120–888 · y 1000–1250", str(s["fuera_de_zona"][:15]))
    a = mat["audio"]
    r["datos"]["audio"] = a
    if "voz_menos_pausas_db" in a and a["voz_menos_pausas_db"] < 6:
        _a(r, f"la voz está sólo {a['voz_menos_pausas_db']} dB sobre las pausas (música/efectos): revisar mezcla")
    r["datos"]["planos"] = len(mat["planos"])
    return r


# ---------------- 7. paquete ----------------
def paquete(ep_d, url_mp4=None, usa_anatomia=None):
    r = RES()
    p = os.path.join(ep_d, "entrega", "caption.md")
    if not os.path.exists(p):
        _f(r, "no existe entrega/caption.md", bloqueante=True)
        return r
    md = open(p).read()
    ig = seccion(md, "Instagram")
    yt = seccion(md, "YouTube")
    com = seccion(md, "Primer comentario")
    meta = seccion(md, "Datos para Metricool")
    for nom, s in (("Instagram/TikTok", ig), ("YouTube", yt), ("Primer comentario", com), ("Datos para Metricool", meta)):
        if not s:
            _f(r, f"falta la sección '{nom}' en caption.md")
    tags = re.findall(r"#\w+", ig)
    r["datos"]["hashtags"] = tags
    if not 3 <= len(tags) <= 5:
        _f(r, f"{len(tags)} hashtags en Instagram/TikTok (3–5)")
    if "#nadieteexplica" not in [t.lower() for t in tags]:
        _f(r, "falta #nadieteexplica")
    if "?" not in ig:
        _f(r, "el texto de Instagram/TikTok no tiene pregunta abierta")
    m = re.search(r"T[ií]tulo[^:]*:\**\s*(.+)", yt)
    titulo = m.group(1).strip() if m else ""
    r["datos"]["titulo_youtube"] = titulo
    if not titulo:
        _f(r, "falta el título de YouTube", bloqueante=True)
    elif len(titulo) > 60:
        _f(r, f"título de YouTube de {len(titulo)} caracteres (máx. 60)", titulo, bloqueante=True)
    if "fuente" not in norm(yt):
        _f(r, "la descripción de YouTube no lleva las fuentes")
    if len(re.findall(r"https?://", com)) < 2 or "fuente" not in norm(com):
        _f(r, "el primer comentario no tiene 'Fuentes' con al menos 2 enlaces")
    if "?" not in com:
        _a(r, "el primer comentario no termina con pregunta ('¿Qué quieres que te explique…?')")
    mm = norm(meta)
    mk = re.search(r"madeforkids[^\n]*", mm)
    if not mk or not re.search(r"(false|\bno\b)", mk.group(0)) or "pendiente" in mk.group(0):
        _f(r, "madeForKids no está en 'no' (decidido por Tomás el 19-oct)", mk.group(0) if mk else "", bloqueante=True)
    if not re.search(r"tiktok[^\n]*title|tiktok[^\n]*t[ií]tulo", mm):
        _f(r, "falta tiktokData.title (Metricool rechaza TikTok sin título)", bloqueante=True)
    if not re.search(r"isaigenerated[^\n]*true", mm):
        _f(r, "falta isAiGenerated: true en Instagram", bloqueante=True)
    if not re.search(r"isaigc[^\n]*true", mm):
        _f(r, "falta isAigc: true en TikTok", bloqueante=True)
    if usa_anatomia is None:
        sb = os.path.join(ep_d, "storyboard.md")
        usa_anatomia = os.path.exists(sb) and re.search(r"(interior|anatom|cabeza de vidrio)", norm(open(sb).read())) is not None
    if usa_anatomia:
        for nom, s in (("descripción de YouTube", yt), ("primer comentario", com)):
            if "z-anatomy" not in norm(s):
                _f(r, f"usa anatomía de Z-Anatomy y falta el crédito en la {nom} (licencia CC BY-SA)", bloqueante=True)
    if not os.path.exists(os.path.join(ep_d, "entrega", "portada.jpg")) and "videocovermilliseconds" not in mm:
        _a(r, "no hay portada.jpg ni videoCoverMilliseconds")
    if url_mp4:
        h = comun.sh(["curl", "-sSL", "-r", "0-0", "-o", "/dev/null", "-w", "%{http_code}", url_mp4]).stdout.strip()
        r["datos"]["url_mp4_http"] = h
        if h not in ("200", "206"):
            _f(r, f"la URL pública del MP4 responde {h}", url_mp4, bloqueante=True)
    return r
