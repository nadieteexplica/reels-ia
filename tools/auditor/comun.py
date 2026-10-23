"""Utilidades del auditor: rutas, planos, cuadros y salida JSON. Sin dependencias raras (numpy, PIL, ffmpeg)."""
import ast, json, os, re, subprocess, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EPIS = os.path.join(RAIZ, "studio", "episodios")
FPS = 30
W, H = 1080, 1920

# Proceso v2 (21-oct-2026, después del Ep. 2): el video se audita como ANIMATIC (baja resolución, antes del render final)
# y el render final sólo pasa un chequeo de bloqueantes. Las carpetas viejas 6-video / 7-paquete quedan como historia.
ETAPAS = {
    "1": "guion", "2": "voz", "3": "storyboard", "4": "cuadros", "5": "kling", "6": "animatic", "7": "final", "8": "paquete",
    "P": "proceso",
}
NOMBRE = {v: k for k, v in ETAPAS.items()}
ALIAS = {"video": "animatic", "plan": "storyboard"}


def etapa_id(e):
    """'6', 'animatic' o '6-animatic' → '6-animatic' ('video' = animatic)."""
    e = ALIAS.get(str(e), str(e))
    if e in ETAPAS:
        return f"{e}-{ETAPAS[e]}"
    if e in NOMBRE:
        return f"{NOMBRE[e]}-{e}"
    if re.match(r"^[1-8P]-\w+$", e):
        return e
    sys.exit(f"etapa desconocida: {e}")


def ep_dir(ep):
    d = ep if os.path.isdir(ep) else os.path.join(EPIS, ep)
    if not os.path.isdir(d):
        sys.exit(f"no existe el episodio: {ep}")
    return os.path.abspath(d)


def ronda_dir(ep, etapa, ronda=None, crear=False):
    raiz = os.environ.get("AUDITORIA_BASE") or os.path.join(ep_dir(ep), "auditoria")   # AUDITORIA_BASE: otra carpeta (calibración)
    base = os.path.join(raiz, etapa_id(etapa))
    if ronda is None:
        rs = sorted(int(x[1:]) for x in os.listdir(base) if re.match(r"^r\d+$", x)) if os.path.isdir(base) else []
        ronda = (rs[-1] + (1 if crear else 0)) if rs else 1
    d = os.path.join(base, f"r{ronda}")
    if crear:
        os.makedirs(os.path.join(d, "materiales"), exist_ok=True)
    return d, ronda


def topes():
    """Topes del proceso v2 (presupuesto.json → proceso_v2). Los cambia Tomás ahí; el código los lee de ahí."""
    d = leer(os.path.join(os.path.dirname(os.path.abspath(__file__)), "presupuesto.json"), {}) or {}
    base = {"horas_por_video": 4, "rondas_por_puerta": 2, "planos_por_revisor": 10, "escenas_max": 6, "escenas_a_medida_max": 3,
            "cambio_max_s": 2.0, "palabras": [70, 128], "duracion_s": [25.0, 45.5], "promedio_min": 8.0, "nota_min_revisor": 7,
            "realismo_min": 8}
    base.update(d.get("proceso_v2", {}))
    return base


# ---------- estilo del episodio (decisión de Tomás, 22-oct-2026) ----------
# Cada episodio declara su estilo en studio/episodios/<ep>/estilo.json y el auditor juzga contra ESE estilo:
#   animado  → el look de los Ep. 1–4 (luz suave de estudio, colores saturados, fondo vivo, personajes estilizados).
#   realista → que parezca una película con efectos, no un dibujo animado; suma el criterio "realismo".
# Las reglas de cada uno están en tools/auditor/prompts/estilos.md (los revisores las leen).
ESTILOS = ("animado", "realista")
# Episodios hechos antes de que existiera estilo.json: sin el archivo se auditan como animados y conservan la ficha del
# protagonista viejo como respaldo. Cualquier episodio nuevo TIENE que declarar su estilo.
LEGADO = {"ep01-congelamiento-cerebral", "ep02-pajaros-picante", "ep03-edificio-que-camino", "ep04-cortina-ducha",
          "rhein01-mosasaurio"}


def es_legado(ep_d):
    return os.path.basename(os.path.normpath(ep_d)) in LEGADO


def estilo(ep_d):
    """Lee studio/episodios/<ep>/estilo.json → {"estilo", "declarado", "referencias", "errores"}.

    Formato: {"estilo": "realista", "referencias": ["referencias/*.jpg"], "nota": "para qué"}
    - estilo: "animado" o "realista" (obligatorio).
    - referencias (opcional, sirve sobre todo en realista): fotos reales del tema, rutas relativas a la carpeta del episodio
      (se aceptan comodines). Los revisores las comparan con los cuadros. Máximo 4 se usan. No se suben al repo público
      (.gitignore): son de otros, sólo para comparar.
    Sin archivo: "animado" (declarado = False). Para un episodio nuevo eso es una falla en preparar."""
    p = os.path.join(ep_d, "estilo.json")
    out = {"estilo": "animado", "declarado": False, "referencias": [], "nota": "", "errores": [], "avisos": []}
    if not os.path.exists(p):
        return out
    try:
        d = leer(p) or {}
    except ValueError as e:
        out["errores"].append(f"estilo.json no es JSON válido: {e}")
        return out
    e = str(d.get("estilo", "")).strip().lower()
    if e not in ESTILOS:
        out["errores"].append(f"estilo.json: 'estilo' debe ser {' o '.join(ESTILOS)} (dice '{d.get('estilo')}')")
        return out
    out.update(estilo=e, declarado=True, nota=str(d.get("nota", "")))
    import glob as _g
    refs = d.get("referencias") or []
    if isinstance(refs, str):
        refs = [refs]
    if not isinstance(refs, list):
        out["errores"].append("estilo.json: 'referencias' tiene que ser una lista de rutas (por ejemplo [\"referencias/*.jpg\"])")
        refs = []
    for patron in refs:
        hits = sorted(_g.glob(os.path.join(ep_d, str(patron))))
        if not hits:     # todavía no se bajan las fotos: no frena (se usan recién en las puertas 4, 6 y 7)
            out["avisos"].append(f"estilo.json: la referencia '{patron}' no encontró archivos en la carpeta del episodio")
        out["referencias"] += [h for h in hits if h.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    out["referencias"] = out["referencias"][:4]
    return out


def ficha(ep_d):
    """Ficha de personajes del episodio (studio/episodios/<ep>/ficha.jpg). Desde el 19-oct-2026 cada idea define su estilo y sus
    personajes (decisión de Tomás), así que un episodio nuevo sólo se compara con SU ficha. El protagonista viejo
    (studio/personaje/ficha.jpg) queda como respaldo sólo para los episodios de LEGADO."""
    rutas = [os.path.join(ep_d, "ficha.jpg")]
    if es_legado(ep_d):
        rutas.append(os.path.join(RAIZ, "studio", "personaje", "ficha.jpg"))
    for p in rutas:
        if os.path.exists(p):
            return p
    return None


def guardar(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def leer(path, defecto=None):
    if not os.path.exists(path):
        return defecto
    with open(path) as f:
        return json.load(f)


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------- planos ----------
def planos_desde_build(path):
    """Lee el diccionario T = {plano: (inicio, fin)} de un build_epNN.py (sirve para versiones viejas del repo)."""
    src = open(path).read()
    m = re.search(r"^T\s*=\s*(\{.*?\n\})", src, re.S | re.M)
    if not m:
        sys.exit(f"no encontré T = {{...}} en {path}")
    T = ast.literal_eval(m.group(1))
    return normalizar(T)


def normalizar(T):
    out = [{"plano": int(k), "a": float(v[0]), "b": float(v[1])} for k, v in T.items()]
    out.sort(key=lambda p: p["a"])
    return out


def cargar_planos(path):
    """Acepta *_planos.json del render ({"T": {...}}), una lista [{plano,a,b}] o un build_epNN.py."""
    if path.endswith(".py"):
        return planos_desde_build(path)
    d = leer(path)
    if isinstance(d, dict) and "T" in d:
        return normalizar(d["T"])
    if isinstance(d, list):
        return sorted(({"plano": int(p["plano"]), "a": float(p["a"]), "b": float(p["b"])} for p in d), key=lambda p: p["a"])
    sys.exit(f"formato de planos desconocido: {path}")


def info_video(path):
    p = json.loads(sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path]).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    return {"dur": float(p["format"]["duration"]), "w": v["width"], "h": v["height"],
            "fps": eval(v["r_frame_rate"]), "codec": v["codec_name"], "pix": v["pix_fmt"],
            "mb": int(p["format"]["size"]) / 1e6}


def leer_cuadros(path, fps=15, w=144, h=256, gris=False):
    """Todos los cuadros del video a baja resolución, como array numpy (N, h, w, 3)."""
    import numpy as np
    fmt = "gray" if gris else "rgb24"
    ch = 1 if gris else 3
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}:flags=area",
                        "-f", "rawvideo", "-pix_fmt", fmt, "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    n = a.size // (w * h * ch)
    return a[: n * w * h * ch].reshape(n, h, w, ch) if ch == 3 else a[: n * w * h].reshape(n, h, w)


def extraer(path, tiempos, salida_fmt, w=360, h=640):
    """Extrae cuadros en los tiempos dados (s) en una sola pasada. Devuelve la lista de archivos en el mismo orden."""
    info = info_video(path)
    fps = info["fps"]
    idx = sorted({min(int(round(t * fps)), int(info["dur"] * fps) - 1) for t in tiempos})
    pos = {n: i for i, n in enumerate(idx)}
    sel = "+".join(f"eq(n\\,{n})" for n in idx)
    tmp = salida_fmt.replace("%s", "_tmp_%05d")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"select='{sel}',scale={w}:{h}", "-vsync", "0", "-q:v", "3", tmp])
    archivos = {}
    for n in idx:
        src = tmp % (pos[n] + 1)
        dst = salida_fmt.replace("%s", f"{n:05d}")
        if os.path.exists(src):
            os.replace(src, dst)
            archivos[n] = dst
    return [archivos.get(min(int(round(t * fps)), int(info["dur"] * fps) - 1)) for t in tiempos]


def rotulo(img, texto, color=(255, 255, 255)):
    """Escribe un rótulo chico arriba a la izquierda (fondo negro)."""
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", max(14, img.width // 18))
    except OSError:
        fnt = ImageFont.load_default()
    x0, y0, x1, y1 = d.textbbox((6, 4), texto, font=fnt)
    d.rectangle((x0 - 4, y0 - 3, x1 + 4, y1 + 3), fill=(0, 0, 0))
    d.text((6, 4), texto, font=fnt, fill=color)
    return img


def grilla(archivos, rotulos, cols, salida, celda=(360, 640)):
    from PIL import Image
    filas = -(-len(archivos) // cols)
    lienzo = Image.new("RGB", (cols * celda[0], filas * celda[1]), (20, 20, 20))
    for i, (f, r) in enumerate(zip(archivos, rotulos)):
        if not f or not os.path.exists(f):
            continue
        im = Image.open(f).convert("RGB").resize(celda)
        rotulo(im, r)
        lienzo.paste(im, ((i % cols) * celda[0], (i // cols) * celda[1]))
    lienzo.save(salida, quality=88)
    return salida
