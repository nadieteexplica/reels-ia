"""Arma los materiales que mira el revisor (imágenes y tablas). Todo se regenera desde los archivos de origen:
si se pierde la carpeta materiales/, se vuelve a correr y queda igual.

video:   contacto (1 cuadro/s), gancho (cuadro 0 + primeros 2 s), loop (fin → inicio), tira de 6–12 cuadros por plano
         (4 por segundo: con 6 cuadros el revisor del Ep. 2 no veía parpadeos y decía "congelado"), medidas de movimiento
         por plano (chequeo_planos.metricas), chequeo automático por plano (ojos tapados, quemado, quieto, fondo liso),
         eventos de los detectores (antes | después ampliados), tabla de subtítulos y audio.
kling:   8 cuadros por clip + su cuadro de partida.
cuadros: cada cuadro de estilo / de partida en grande + la ficha del personaje.
"""
import json, os, re, subprocess
import numpy as np
from PIL import Image

import comun
import detectores as D
import chequeo_planos as CH


# ---------------- video ----------------
def cuadros_por_plano(dur):
    """4 cuadros por segundo, entre 6 y 12."""
    return int(max(6, min(12, round(dur * 4))))


def video(mdir, mp4, planos=None, subs_log=None, words=None, kling_planos=None, meta=None, graficos=None):
    os.makedirs(mdir, exist_ok=True)
    info = comun.info_video(mp4)
    dur = info["dur"]
    G = comun.leer_cuadros(mp4, fps=D.FPS_D, w=D.DW, h=D.DH, gris=True)
    if not planos:
        cs = D.cortes(G)
        lim = [0.0] + cs + [dur]
        planos = [{"plano": i + 1, "a": lim[i], "b": lim[i + 1]} for i in range(len(lim) - 1) if lim[i + 1] - lim[i] > 0.15]
    kl = {int(k["plano"]): k for k in (kling_planos or [])}
    for p in planos:
        p["origen"] = "kling" if p["plano"] in kl else "render"

    # --- detectores ---
    subs = comun.leer(subs_log, []) if subs_log else []
    mask = D.mascara_subs(subs, len(G))
    eventos = D.vacios(G) + D.apariciones(G, [p["a"] for p in planos[1:]], mask, top=40) + D.luz(G, planos) + D.sin_cambio(planos)
    for e in eventos:
        t = e.get("t", e.get("t0"))
        e["plano"] = e.get("plano") or next((p["plano"] for p in planos if p["a"] <= t < p["b"]), None)
    eventos.sort(key=lambda e: e.get("t", e.get("t0", 0)))
    for i, e in enumerate(eventos):
        e["id"] = f"E{i + 1}"
    comun.guardar(os.path.join(mdir, "eventos.json"), eventos)
    _imagenes_eventos(mdir, mp4, eventos)

    # --- chequeo automático por plano + medidas de movimiento (van en planos.json para el revisor) ---
    nums = [int(round(i / D.FPS_D * 30)) + 1 for i in range(len(G))]
    ojos = CH.leer_ojos(meta) if meta else {}
    cajas = CH.leer_cajas(graficos if graficos and os.path.exists(graficos) else None, subs_log if subs_log and os.path.exists(subs_log) else None)
    chq = CH.chequear(planos, G, nums, ojos, cajas, vacias=False)      # la pantalla vacía ya la marca D.vacios arriba
    for p in planos:
        p.update(chq["planos"].get(p["plano"], {}))

    # --- contacto 1 cuadro por segundo ---
    ts = [min(s + 0.5, dur - 0.05) for s in range(int(dur))]
    fs = comun.extraer(mp4, ts, os.path.join(mdir, "tmp", "c%s.jpg"), 180, 320)
    comun.grilla(fs, [f"{int(t)}s" for t in ts], 12, os.path.join(mdir, "contacto.jpg"), (180, 320))

    # --- gancho: cuadro 0 grande + 6 cuadros de los primeros 2 s ---
    f0 = comun.extraer(mp4, [0.0], os.path.join(mdir, "tmp", "g0_%s.jpg"), 540, 960)[0]
    Image.open(f0).save(os.path.join(mdir, "cuadro0.jpg"), quality=90)
    ts = [0.0, 0.33, 0.67, 1.0, 1.4, 1.9]
    fs = comun.extraer(mp4, ts, os.path.join(mdir, "tmp", "g%s.jpg"), 360, 640)
    comun.grilla(fs, [f"{t:.2f}s" for t in ts], 3, os.path.join(mdir, "gancho.jpg"))

    # --- loop: último segundo → primer segundo ---
    ts = [dur - 0.9, dur - 0.5, dur - 0.1, 0.0, 0.3, 0.6]
    fs = comun.extraer(mp4, ts, os.path.join(mdir, "tmp", "l%s.jpg"), 360, 640)
    comun.grilla(fs, ["fin -0.9s", "fin -0.5s", "fin -0.1s", "inicio 0.0s", "0.3s", "0.6s"], 3, os.path.join(mdir, "loop.jpg"))

    # --- tira de 6–12 cuadros por plano (4 por segundo) ---
    os.makedirs(os.path.join(mdir, "planos"), exist_ok=True)
    todos, mapa = [], []
    for p in planos:
        a, b = p["a"] + 0.04, p["b"] - 0.04
        n = cuadros_por_plano(p["b"] - p["a"])
        for k in range(n):
            todos.append(a + (b - a) * k / (n - 1))
            mapa.append(p["plano"])
    fs = comun.extraer(mp4, todos, os.path.join(mdir, "tmp", "p%s.jpg"), 270, 480)
    for p in planos:
        idx = [i for i, m in enumerate(mapa) if m == p["plano"]]
        rot = [f"P{p['plano']} {todos[i]:.2f}s" for i in idx]
        p["tira"] = f"planos/P{p['plano']:02d}.jpg"
        comun.grilla([fs[i] for i in idx], rot, 3 if len(idx) <= 6 else 4, os.path.join(mdir, p["tira"]), (270, 480))
    comun.guardar(os.path.join(mdir, "planos.json"), planos)

    # --- subtítulos contra words.json ---
    sub = tabla_subtitulos(subs, comun.leer(words, []) if words else [], os.path.join(mdir, "subtitulos.md")) if subs else None

    # --- audio ---
    aud = audio(mp4, comun.leer(words, []) if words else [])
    comun.guardar(os.path.join(mdir, "audio.json"), aud)
    subprocess.run(["rm", "-rf", os.path.join(mdir, "tmp")])
    return {"info": info, "planos": planos, "eventos": eventos, "subtitulos": sub, "audio": aud, "chequeo": chq}


def _imagenes_eventos(mdir, mp4, eventos):
    """Para cada evento: antes | después, ampliado en la zona marcada (o el cuadro entero)."""
    os.makedirs(os.path.join(mdir, "eventos"), exist_ok=True)
    pares = []
    for e in eventos:
        if e["tipo"] == "aparece_o_desaparece":
            pares.append((e, e["t"] - 2 / D.FPS_D, e["t"] + 1 / D.FPS_D))
        elif e["tipo"] == "pantalla_vacia":
            pares.append((e, max(0, e["t0"] - 0.1), (e["t0"] + e["t1"]) / 2))
        elif e["tipo"] == "cambio_de_luz":
            pares.append((e, e["t0"] + 0.1, e["t1"] - 0.1))
    if not pares:
        return
    ts = [x for _e, a, b in pares for x in (a, b)]
    fs = comun.extraer(mp4, ts, os.path.join(mdir, "tmp", "e%s.png"), 1080, 1920)
    for i, (e, a, b) in enumerate(pares):
        ims = [Image.open(fs[2 * i]).convert("RGB"), Image.open(fs[2 * i + 1]).convert("RGB")]
        if "caja" in e:
            x0, y0, x1, y1 = e["caja"]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            s = max(x1 - x0, y1 - y0) * 1.8 + 120
            s = min(s, 1080)
            box = (int(max(0, min(1080 - s, cx - s / 2))), int(max(0, min(1920 - s, cy - s / 2))))
            box = (box[0], box[1], int(box[0] + s), int(box[1] + s))
            ims = [im.crop(box).resize((480, 480)) for im in ims]
        else:
            ims = [im.resize((360, 640)) for im in ims]
        w, h = ims[0].size
        lienzo = Image.new("RGB", (2 * w + 8, h), (255, 0, 255))
        lienzo.paste(comun.rotulo(ims[0], f"{e['id']} antes {a:.2f}s"), (0, 0))
        lienzo.paste(comun.rotulo(ims[1], f"{e['id']} después {b:.2f}s"), (w + 8, 0))
        e["imagen"] = f"eventos/{e['id']}.jpg"
        lienzo.save(os.path.join(mdir, e["imagen"]), quality=88)
    comun.guardar(os.path.join(mdir, "eventos.json"), eventos)


def tabla_subtitulos(subs, words, salida, fps=30):
    """Una fila por palabra: cuándo se dice, cuándo está en pantalla, si está en pantalla mientras se dice y si la caja está en la zona."""
    por_palabra = {}
    if subs and len(subs[0]) < 7:      # registros viejos sin índice de palabra: se asigna la palabra igual más cercana en tiempo
        clave = lambda x: re.sub(r"[^\wÁÉÍÓÚÜÑáéíóúüñ]", "", x).upper()
        W = [clave(w["w"]) for w in words]
        nuevos = []
        for f, tok, x0, y0, x1, y1 in subs:
            t = (f - 1) / fps
            cand = [i for i, w in enumerate(W) if w == clave(tok)]
            wi = min(cand, key=lambda i: abs(words[i]["s"] - t)) if cand else -1
            nuevos.append((f, tok, x0, y0, x1, y1, wi))
        subs = nuevos
    for f, tok, x0, y0, x1, y1, wi in subs:
        r = por_palabra.setdefault(wi, {"tok": tok, "f0": f, "f1": f, "caja": [x0, y0, x1, y1], "fuera": 0})
        r["f0"], r["f1"] = min(r["f0"], f), max(r["f1"], f)
        r["caja"] = [min(r["caja"][0], x0), min(r["caja"][1], y0), max(r["caja"][2], x1), max(r["caja"][3], y1)]
        if x0 < 115 or x1 > 893 or y0 < 995 or y1 > 1255:
            r["fuera"] += 1
    filas, faltan, desfase, fuera = [], [], [], []
    for i, w in enumerate(words):
        r = por_palabra.get(i)
        if not r:
            faltan.append(i)
            filas.append(f"| {i} | {w['w']} | {w['s']:.2f}–{w['e']:.2f} | — | NO APARECE | — |")
            continue
        t0, t1 = (r["f0"] - 1) / fps, (r["f1"]) / fps
        ok = t0 <= w["s"] + 0.05 and t1 >= min(w["e"], w["s"] + 0.15) - 0.05
        if not ok:
            desfase.append(i)
        if r["fuera"]:
            fuera.append(i)
        c = ",".join(str(int(v)) for v in r["caja"])
        filas.append(f"| {i} | {w['w']} | {w['s']:.2f}–{w['e']:.2f} | {t0:.2f}–{t1:.2f} | {'ok' if ok else 'DESFASE'} | {c}{' FUERA' if r['fuera'] else ''} |")
    extra = sorted(set(por_palabra) - set(range(len(words))))
    with open(salida, "w") as f:
        f.write("| # | palabra | se dice (s) | en pantalla (s) | sincronía | caja x0,y0,x1,y1 |\n|---|---|---|---|---|---|\n")
        f.write("\n".join(filas) + "\n")
    tiempos = {i: [round(words[i]["s"], 2), round(words[i]["e"], 2), words[i]["w"]] for i in faltan + desfase}
    return {"palabras": len(words), "en_pantalla": len(por_palabra), "faltan": faltan, "desfase": desfase, "fuera_de_zona": fuera,
            "sobran": extra, "tiempos": tiempos}


def audio(mp4, words):
    """LUFS, true peak y diferencia voz/música aproximada (habla vs. pausas de más de 0,35 s, que tienen solo música y efectos)."""
    e = comun.sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
    TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
    out = {"lufs": I, "true_peak": TP}
    if words:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True)
        a = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768

        def rms(t0, t1):
            s = a[int(t0 * 16000):int(t1 * 16000)]
            return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9) if len(s) > 160 else None

        habla = [rms(w["s"], w["e"]) for w in words if w["e"] - w["s"] > 0.12]
        pausas = [rms(words[i]["e"] + 0.05, words[i + 1]["s"] - 0.05) for i in range(len(words) - 1) if words[i + 1]["s"] - words[i]["e"] > 0.35]
        habla = [x for x in habla if x is not None]
        pausas = [x for x in pausas if x is not None]
        if habla and pausas:
            out["voz_db"] = round(float(np.median(habla)), 1)
            out["pausas_db"] = round(float(np.median(pausas)), 1)
            out["voz_menos_pausas_db"] = round(out["voz_db"] - out["pausas_db"], 1)
            out["nota"] = "pausas = música + efectos sin voz; con ducking la música sube en las pausas, así que esto es un mínimo"
    return out


# ---------------- kling ----------------
def kling(mdir, clips, pedidos):
    """clips: lista de mp4. pedidos: dict nombre → {inicio (jpg), prompt}."""
    os.makedirs(mdir, exist_ok=True)
    out = []
    for c in clips:
        nombre = os.path.splitext(os.path.basename(c))[0]
        info = comun.info_video(c)
        ts = [info["dur"] * k / 7 * 0.98 + 0.02 for k in range(8)]
        fs = comun.extraer(c, ts, os.path.join(mdir, "tmp", nombre + "_%s.jpg"), 360, 640)
        img = os.path.join(mdir, f"{nombre}.jpg")
        comun.grilla(fs, [f"{nombre} {t:.1f}s" for t in ts], 4, img, (360, 640))
        det = _detalle_movimiento(c, info, mdir, nombre)
        ped = pedidos.get(nombre, {})
        ini = ped.get("inicio")
        if ini and os.path.exists(ini):
            Image.open(ini).convert("RGB").resize((360, 640)).save(os.path.join(mdir, f"{nombre}_inicio.jpg"), quality=88)
        out.append({"clip": nombre, "cuadros": f"{nombre}.jpg", "detalle": det, "inicio": f"{nombre}_inicio.jpg" if ini else None,
                    "prompt": ped.get("prompt", ""), "dur": round(info["dur"], 2), "res": f"{info['w']}x{info['h']}"})
    subprocess.run(["rm", "-rf", os.path.join(mdir, "tmp")])
    comun.guardar(os.path.join(mdir, "clips.json"), out)
    return out


def zona_movimiento(path, dur, w=180, h=320):
    """Caja (x0, y0, x1, y1, en píxeles del video) donde más cambia la imagen: ahí están las manos y los objetos que se mueven."""
    W, H = comun.info_video(path)["w"], comun.info_video(path)["h"]
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=10,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    n = a.size // (w * h)
    if n < 3:
        return None
    G = a[: n * w * h].reshape(n, h, w).astype(np.float32)
    m = np.abs(np.diff(G, axis=0)).mean(axis=0)
    thr = max(6.0, float(np.percentile(m, 92)))
    ys, xs = np.where(m > thr)
    if len(xs) < 20:
        return None
    x0, x1 = np.percentile(xs, [3, 97])
    y0, y1 = np.percentile(ys, [3, 97])
    lado = max(x1 - x0, y1 - y0) * 1.25 + 20
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lado = min(lado, w)
    x0 = max(0, min(w - lado, cx - lado / 2))
    y0 = max(0, min(h - lado, cy - lado / 2))
    k = W / w
    return [int(x0 * k), int(y0 * k), int((x0 + lado) * k), int((y0 + lado) * k)]


def _detalle_movimiento(c, info, mdir, nombre):
    """4 cuadros a resolución completa recortados donde hay movimiento (manos, objetos), para ver los dedos."""
    caja = zona_movimiento(c, info["dur"])
    if not caja:
        return None
    ts = [info["dur"] * f for f in (0.08, 0.36, 0.64, 0.92)]
    fs = comun.extraer(c, ts, os.path.join(mdir, "tmp", nombre + "_d%s.png"), info["w"], info["h"])
    lienzo = Image.new("RGB", (1080, 1080), (20, 20, 20))
    for i, (f, t) in enumerate(zip(fs, ts)):
        if not f:
            continue
        im = Image.open(f).convert("RGB").crop(tuple(caja)).resize((540, 540))
        comun.rotulo(im, f"{nombre} {t:.1f}s (zoom)")
        lienzo.paste(im, ((i % 2) * 540, (i // 2) * 540))
    lienzo.save(os.path.join(mdir, f"{nombre}_detalle.jpg"), quality=90)
    return f"{nombre}_detalle.jpg"


# ---------------- cuadros ----------------
def cuadros(mdir, imagenes, ficha=None):
    os.makedirs(mdir, exist_ok=True)
    out = []
    for f in imagenes:
        im = Image.open(f).convert("RGB")
        a = np.asarray(im.convert("L"))
        hsv = np.asarray(im.convert("HSV"))
        nombre = os.path.splitext(os.path.basename(f))[0]
        im.resize((720, 1280)).save(os.path.join(mdir, f"{nombre}.jpg"), quality=90)
        out.append({"cuadro": nombre, "archivo": f"{nombre}.jpg", "res": f"{im.width}x{im.height}",
                    "quemados_pct": round(float((a > 250).mean() * 100), 2), "brillo": round(float(a.mean()), 1),
                    "saturacion": round(float(hsv[..., 1].mean()), 1)})
    if ficha and os.path.exists(ficha):
        Image.open(ficha).convert("RGB").save(os.path.join(mdir, "ficha_personaje.jpg"), quality=90)
    comun.guardar(os.path.join(mdir, "cuadros.json"), out)
    return out
