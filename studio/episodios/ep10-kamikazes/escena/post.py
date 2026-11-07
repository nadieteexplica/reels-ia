"""Post del Ep. 10 (kamikazes; sobre el del Ep. 9): arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Gradación de época (grado.py: menos color, más contraste, un poco cálida) con grano fino y viñeta; el mapa va limpio.
- Píldoras del storyboard v2: KAMIKAZE · 17 AÑOS con flecha, 26 DE MAYO DE 1945 + FOTO REAL, VOLUNTARIOS, ÚLTIMA CARTA y
  PERDÓN (+ RECREACIÓN), OKINAWA 1945, INVASIÓN · 1 DE NOVIEMBRE, PRESIDENTE TRUMAN, 15 DE AGOSTO DE 1945 / JAPÓN SE RINDE.
- Mapa: islas perdidas (rojo → gris), flechas de EE.UU., barras MARINEROS/EJÉRCITO, flechas de la invasión, la mancha roja
  de Okinawa que se copia a Japón y los dos destellos (Hiroshima, Nagasaki). Contador 0 → 12.700. Blanco al final del 16.
- Loop: desde 53,40 s vuelve la foto del cuadro 0 (cuadros del plano 1).
- Las posiciones salen del meta de cada cuadro (pantalla() de la escena); las caras de la foto van como "ojos".
- Escribe subs_log.json, graficos.json y ep10_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep10 as E
import graficos as G
from grado import grado
E2_ESCENA = {1: "E5", 2: "E5", 3: "E1", 4: "E4", 5: "E1", 6: "E5", 7: "E5", 8: "E5", 9: "E5", 10: "E5", 11: "E3", 12: "E3", 13: "E3",
             14: "E3", 15: "E3", 16: "E3", 17: "E3", 18: "E4", 19: "E4", 20: "E1", 21: "E1", 22: "E4", 23: "E4", 24: "E4", 25: "E4",
             26: "E5", 27: "E1"}      # = planos_ep10.ESCENA (sin importar bpy)

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
words = E.palabras()
FR = {k: E.FR(k) for k in E.T}
END = E.FIN
FONTS = os.path.abspath(os.path.join(HERE, "../../../plantilla/fonts"))
FONT = os.path.join(FONTS, "Inter-Black.otf")
FONT_B = os.path.join(FONTS, "Inter-ExtraBold.otf")
AMARILLO = (255, 210, 63)          # palabra activa (manual §6)
AMBAR = (255, 186, 52)             # píldoras de la historia japonesa
ACERO = (64, 104, 146)             # píldoras de EE.UU.
AZUL = (70, 150, 255)              # flechas y barra de EE.UU.
VERDE = (96, 170, 90)              # el ejército en tierra
GRIS = (150, 156, 166)
ROJO = (225, 45, 40)
CLAVE = {"KAMIKAZE": (240, 80, 64), "KAMIKAZES": (240, 80, 64)}
BOX = (120, 888, 1000, 1250)
META = {}
for p in sorted(glob.glob(os.path.join(src, "meta", "*.json"))):
    d = json.load(open(p))
    META.setdefault(str(d["pieza"]), {"cuadros": {}})["cuadros"].update(d.get("cuadros", {}))


def plano_de(f):
    for k, (a, b) in FR.items():
        if a <= f < b:
            return k
    return max(FR)


def t_de(f):
    return (f - 1) / FPS


def meta(k, f, clave, defecto=None):
    c = META.get(str(k), {}).get("cuadros", {})
    if str(f) in c and clave in c[str(f)]:
        return c[str(f)][clave]
    ks = [int(x) for x, v in c.items() if clave in v]
    if ks:
        return c[str(min(ks, key=lambda x: abs(x - f)))][clave]
    return defecto


def cargar(path):
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


def cuadro(f, a, b):
    im = cargar(os.path.join(src, f"{f:05d}.png"))
    if im is not None or not os.environ.get("MUESTRAS"):
        return im
    cand = [int(os.path.basename(q)[:5]) for q in glob.glob(os.path.join(src, "[0-9]" * 5 + ".png"))]
    cand = [c for c in cand if a <= c < b]
    return cargar(os.path.join(src, f"{min(cand, key=lambda c: abs(c - f)):05d}.png")) if cand else None


def bloom(im, umbral=0.82, fuerza=0.45):
    a = np.asarray(im).astype(np.float32) / 255
    lum = a.max(axis=2)
    mask = np.clip((lum - umbral) / (1 - umbral), 0, 1)[..., None] * a
    g = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return Image.fromarray((np.clip(a + g * fuerza, 0, 1) * 255).astype(np.uint8))


def pop(age, dur=0.3):
    if age <= 0:
        return 0.0
    if age >= dur:
        return 1.0
    x = age / dur
    return 1 + 0.18 * math.sin(math.pi * x) * (1 - x) * 2 - (1 - x) ** 3


# ---------------- gráficos ----------------
def pildora(im, texto, cx, cy, fondo=(250, 250, 248), tinta=(24, 24, 28), s=1.0, tam=58, marca=None, tipo="pildora"):
    if s <= 0.02:
        return
    f = ImageFont.truetype(FONT, int(tam * s))
    tw = f.getlength(texto)
    extra = int(tam * 1.0 * s) if marca else 0
    w, h = tw + 64 * s + extra, tam * 1.45 * s
    x0, y0 = cx - w / 2, cy - h / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 4, y0 + 7, x0 + w + 4, y0 + h + 7), radius=h / 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=h / 2, fill=(*fondo, 245))
    tx = x0 + 32 * s + extra
    d.text((tx, cy - f.size * 0.60), texto, font=f, fill=tinta)
    if marca:
        mx, my, r = x0 + 32 * s + extra * 0.42, cy, tam * 0.34 * s
        if marca == "x":
            for dx in (-1, 1):
                d.line((mx - r, my - r * dx, mx + r, my + r * dx), fill=tinta, width=int(9 * s))
        else:
            d.line((mx - r, my, mx - r * 0.25, my + r * 0.75, mx + r, my - r * 0.8), fill=tinta, width=int(9 * s), joint="curve")
    im.paste(lay, (0, 0), lay)
    G.registrar(tipo, (x0, y0, x0 + w, y0 + h))


def flecha(im, x0, y0, x1, y1, col, ancho=10):
    d = ImageDraw.Draw(im)
    d.line((x0, y0, x1, y1), fill=col, width=ancho)
    a = math.atan2(y1 - y0, x1 - x0)
    L = ancho * 2.6
    for s in (-1, 1):
        d.line((x1, y1, x1 - L * math.cos(a + s * 0.5), y1 - L * math.sin(a + s * 0.5)), fill=col, width=ancho)
    G.registrar("flecha", (min(x0, x1) - 12, min(y0, y1) - 12, max(x0, x1) + 12, max(y0, y1) + 12))




def sale(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def suave(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

# ---------------- subtítulos (palabra por palabra; cifras juntas) ----------------
NUMEROS = [("diecisiete", "17"), ("trece mil", "13.000")]


def limpiar(w):
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡?¿\"":
        w = w.replace(ch, "")
    return w.upper()


TOK = []          # [(texto en pantalla, [índices de palabras], fin de frase)]
i = 0
while i < len(words):
    hecho = False
    for frase, cifra in NUMEROS:
        n = len(frase.split())
        bloque = [limpiar(x["w"]).lower() for x in words[i:i + n]]
        if bloque == [limpiar(x).lower() for x in frase.split()]:
            TOK.append((cifra, list(range(i, i + n)), words[i + n - 1]["w"][-1] in ",.:;!?…"))
            i += n
            hecho = True
            break
    if not hecho:
        TOK.append((limpiar(words[i]["w"]), [i], words[i]["w"][-1] in ",.:;!?…" or words[i]["w"].endswith("...")))
        i += 1

grupos, cur = [], []
for j, (tx, idx, fin) in enumerate(TOK):
    cur.append(j)
    nxt = TOK[j + 1][1][0] if j + 1 < len(TOK) else None
    if len(cur) == 3 or fin or (nxt is not None and words[nxt]["s"] - words[idx[-1]]["e"] > 0.3):
        grupos.append(cur)
        cur = []
if cur:
    grupos.append(cur)
g2 = []
for g in grupos:
    if any(len(TOK[j][0]) >= 11 for j in g) and len(g) > 1:
        # la palabra larga va sola, pero las cortas de al lado quedan juntas (v3.0: "QUE" salía sola 0,1 s, puerta 6)
        cur = []
        for j in g:
            if len(TOK[j][0]) >= 11:
                if cur:
                    g2.append(cur)
                g2.append([j])
                cur = []
            else:
                cur.append(j)
        if cur:
            g2.append(cur)
    else:
        g2.append(g)
grupos = g2
# Ep. 10: grupos a mano (el corte automático dejaba "SON" o "LOS" solos y partía "ESTADOS | UNIDOS")
GRUPOS_MANUAL = """ESTE KAMIKAZE | TIENE 17 AÑOS | LA FOTO ES | DE 1945 | EL DÍA ANTES | DE SU MISIÓN | JAPÓN ESTÁ PERDIENDO | LA GUERRA |
Y MANDA | A SUS PILOTOS | A NO VOLVER | OFICIALMENTE | SON VOLUNTARIOS | PERO DECIRLE QUE NO | A TU ESCUADRÓN | ES CASI IMPOSIBLE |
ANTES DE DESPEGAR | LE ESCRIBEN | A SU FAMILIA | Y LE PIDEN | PERDÓN | LOS ESTADOUNIDENSES | NO SABEN | CÓMO FRENAR | A ALGUIEN QUE |
NO QUIERE VOLVER | LLENAN EL CIELO | DE BALAS | Y DERRIBAN | A LA MAYORÍA | PERO EL QUE PASA | CASI SIEMPRE PEGA | EN OKINAWA MUEREN |
MÁS MARINEROS | QUE SOLDADOS | DEL EJÉRCITO | EN TIERRA | Y A ESTADOS UNIDOS | TODAVÍA LE FALTA | INVADIR JAPÓN | PERO JAPÓN JUNTA |
CASI 13.000 AVIONES | TODOS | PARA CHOCAR | EL PRESIDENTE TRUMAN | TEME REPETIR OKINAWA | AHORA EN JAPÓN | ESE MIEDO | ES UNA |
DE LAS RAZONES | PARA LANZAR | LA BOMBA ATÓMICA | Y EL DÍA QUE | JAPÓN SE RINDE | TODAVÍA DESPEGAN | KAMIKAZES"""
_gm = [g.split() for g in GRUPOS_MANUAL.replace("\n", " ").split("|") if g.strip()]
_j, _gr = 0, []
for _g in _gm:
    _idx = list(range(_j, _j + len(_g)))
    if [TOK[j][0] for j in _idx] != _g:
        raise SystemExit(f"GRUPOS_MANUAL no calza en {_g}: {[TOK[j][0] for j in _idx]}")
    _gr.append(_idx)
    _j += len(_g)
if _j != len(TOK):
    raise SystemExit(f"GRUPOS_MANUAL deja {len(TOK) - _j} palabras fuera")
grupos = _gr
SIN_SUBS = set()
SUB_LOG = []


def s_tok(j):
    return words[TOK[j][1][0]]["s"]


def e_tok(j):
    return words[TOK[j][1][-1]]["e"]


def tam(tok, font):
    return int(font.size * 1.10) if tok in CLAVE else font.size


def gap(font, a, b):
    return font.getlength(" ") + 0.07 * (font.getlength(a) + font.getlength(b))


def ancho(font, toks):
    return sum(ImageFont.truetype(FONT, tam(t, font)).getlength(t) for t in toks) + sum(gap(font, toks[i], toks[i + 1]) for i in range(len(toks) - 1))


def diagramar(g):
    toks = [TOK[j][0] for j in g]
    maxw = (BOX[1] - BOX[0]) / 1.12
    splits = [[toks]]
    if len(toks) > 1:
        c = len(toks) // 2 + len(toks) % 2
        splits.append([toks[:c], toks[c:]])
    for lo in (76, 60):
        for lines in splits:
            for size in range(84, lo - 1, -4):
                f = ImageFont.truetype(FONT, size)
                if all(ancho(f, l) <= maxw for l in lines):
                    return f, lines
    return ImageFont.truetype(FONT, 60), splits[-1]


def subtitulos(img, f):
    if f in SIN_SUBS:
        return
    t = t_de(f)
    g = None
    for gi, gg in enumerate(grupos):
        s, e = s_tok(gg[0]), e_tok(gg[-1])
        nxt = grupos[gi + 1] if gi + 1 < len(grupos) else None
        e_show = min(e + 0.25, s_tok(nxt[0])) if nxt else e + 0.4
        if s - 0.03 <= t < e_show:
            g = gg
            break
    if g is None:
        return
    font, lines = diagramar(g)
    d = ImageDraw.Draw(img, "RGBA")
    lh = font.size * 1.12
    y0 = (BOX[2] + BOX[3]) / 2 - lh * len(lines) / 2
    cx = (BOX[0] + BOX[1]) / 2
    k = 0
    for li, line in enumerate(lines):
        x = cx - ancho(font, line) / 2
        y = y0 + li * lh
        for ti, tok in enumerate(line):
            j = g[k]
            k += 1
            fb = ImageFont.truetype(FONT, tam(tok, font))
            yy = y - (fb.size - font.size) / 2
            activo = s_tok(j) - 0.02 <= t < max(e_tok(j), s_tok(j) + 0.12)
            tw = fb.getlength(tok)
            col = CLAVE.get(tok, (255, 255, 255))
            if activo:
                age = t - s_tok(j)
                sc = 1.0 + 0.12 * max(0.0, 1 - abs(age - 0.06) / 0.06) if age < 0.12 else 1.0
                fnt = ImageFont.truetype(FONT, int(fb.size * sc))
                ox, oy = (fnt.getlength(tok) - tw) / 2, (fnt.size - fb.size) / 2
                d.text((x - ox + 3, yy - oy + 5), tok, font=fnt, fill=(0, 0, 0, 110))
                d.text((x - ox, yy - oy), tok, font=fnt, fill=AMARILLO if tok not in CLAVE else col, stroke_width=6, stroke_fill=(0, 0, 0))
                caja = (x - ox, yy - oy, x - ox + fnt.getlength(tok), yy - oy + fnt.size)
            else:
                d.text((x + 3, yy + 5), tok, font=fb, fill=(0, 0, 0, 110))
                d.text((x, yy), tok, font=fb, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
                caja = (x, yy, x + tw, yy + fb.size)
            for wi in TOK[j][1]:
                SUB_LOG.append((f, limpiar(words[wi]["w"]), *caja, wi))
            x += tw + (gap(font, tok, line[ti + 1]) if ti + 1 < len(line) else 0)


# ---------------- gráficos por plano (v3) ----------------
def edad(f, k, desde=0.0):
    return t_de(f) - E.T[k][0] - desde


def tw(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def T0(k):
    return E.T[k][0]


_LUGAR = {}


def libre(k, clave, texto, pref, tam=58, marca=None):
    """Lugar fijo (por plano) para una píldora que no tape ningún ojo en todo el plano (graficos.lugar_libre)."""
    if (k, clave) not in _LUGAR:
        fnt = ImageFont.truetype(FONT, tam)
        w = fnt.getlength(texto) + 64 + (tam if marca else 0) + 16
        h = tam * 1.45 + 16
        ojos = [o for c in META.get(str(k), {}).get("cuadros", {}).values() for o in c.get("ojos", [])]
        _LUGAR[(k, clave)] = G.lugar_libre(w, h, ojos, preferidos=pref) or pref[0]
    return _LUGAR[(k, clave)]


def pild(im, f, k, clave, texto, t0, pref, fondo=(250, 250, 248), tinta=(24, 24, 28), tam=58, marca=None, hasta=None):
    t = t_de(f)
    if t < t0 or (hasta is not None and t >= hasta):
        return
    cx, cy = libre(k, clave, texto, pref, tam, marca)
    pildora(im, texto, cx, cy, fondo=fondo, tinta=tinta, s=pop(t - t0), tam=tam, marca=marca)


def texto_sombra(d, xy, texto, fnt, col=(255, 255, 255), a=255, ancla="mm"):
    x, y = xy
    d.text((x + 3, y + 5), texto, font=fnt, fill=(0, 0, 0, int(0.45 * a)), anchor=ancla)
    d.text((x, y), texto, font=fnt, fill=(*col, a), stroke_width=5, stroke_fill=(0, 0, 0, int(0.8 * a)), anchor=ancla)


def apunta(im, f, k, clave, texto, t0, punto, fondo=(250, 250, 248), tinta=(24, 24, 28), tam=50, hasta=None, col=(255, 255, 255)):
    """Píldora con flecha fina hacia lo que nombra (posición de la escena en el meta del cuadro)."""
    t = t_de(f)
    if t < t0 or (hasta is not None and t >= hasta):
        return
    px, py = meta(k, f, punto, None) or (540, 700)
    cx = max(330, min(750, px))
    s = pop(t - t0)
    if py > 1290:      # lo que nombra está bajo los subtítulos: la píldora va debajo y la flecha sube (no cruza el texto)
        cy = min(1600, py + 150)
        if cy - py > 100 and s > 0.5:
            flecha(im, cx, cy - 46, px, py + 14, col, ancho=8)
        pildora(im, texto, cx, cy, fondo=fondo, tinta=tinta, s=s, tam=tam)
        return
    cy = max(470, min(800, py - 230))
    if py > 960:       # caería sobre los subtítulos: sin flecha
        pildora(im, texto, cx, cy, fondo=fondo, tinta=tinta, s=s, tam=tam)
        return
    if py - cy > 120 and s > 0.5:
        flecha(im, cx, cy + 46, px, py - 14, col, ancho=8)
    pildora(im, texto, cx, cy, fondo=fondo, tinta=tinta, s=s, tam=tam)


def _lug(k, f, nombre):
    L = meta(k, f, "lugares", {}) or {}
    p = L.get(nombre)
    return tuple(p) if p else None


def _capa_rgba(im):
    return Image.new("RGBA", im.size, (0, 0, 0, 0))


def _componer(im, capa):
    im.paste(capa, (0, 0), capa)


def mancha(im, centro, r, alfa, col=ROJO):
    """Mancha roja difusa sobre el mapa (lo que pasó en Okinawa)."""
    if not centro or alfa <= 0.01 or r < 2:
        return
    lay = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(lay)
    x, y = centro
    d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=int(255 * alfa))
    lay = lay.filter(ImageFilter.GaussianBlur(max(2, r * 0.35)))
    rojo = Image.new("RGB", im.size, col)
    im.paste(rojo, (0, 0), lay.point(lambda v: int(v * 0.75)))


def destello(im, centro, u):
    """Destello blanco de una bomba vista desde el espacio (u: 0 → 1 en 0,7 s)."""
    if not centro or u <= 0 or u >= 1:
        return
    x, y = centro
    a = min(1.0, 1.6 * math.exp(-u * 3.0))
    r = 70 + 380 * sale(u)
    lay = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(lay)
    d.ellipse((x - r, y - r, x + r, y + r), fill=int(255 * a))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.45))
    im.paste(Image.new("RGB", im.size, (255, 250, 235)), (0, 0), lay)
    d2 = ImageDraw.Draw(im)
    rr = 14 + 40 * (1 - u)
    d2.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 250))


def punto_isla(im, xy, col, r=13):
    if not xy:
        return
    d = ImageDraw.Draw(im)
    x, y = xy
    d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=(10, 10, 12))
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def flecha_parcial(im, p0, p1, u, col=AZUL, ancho=12):
    if not p0 or not p1 or u <= 0.02:
        return
    x0, y0 = p0
    x1 = x0 + (p1[0] - x0) * u
    y1 = y0 + (p1[1] - y0) * u
    d = ImageDraw.Draw(im)
    d.line((x0, y0, x1, y1), fill=(10, 14, 24), width=ancho + 8)
    flecha(im, x0, y0, x1, y1, col, ancho=ancho)


def etiqueta(im, texto, xy, tam=46, col=(255, 255, 255), a=255, dy=-48):
    if not xy:
        return
    d = ImageDraw.Draw(im, "RGBA")
    fnt = ImageFont.truetype(FONT, tam)
    x = max(40 + fnt.getlength(texto) / 2, min(1040 - fnt.getlength(texto) / 2, xy[0]))
    y = max(260, min(940, xy[1] + dy))
    texto_sombra(d, (x, y), texto, fnt, col=col, a=a)
    G.registrar("etiqueta", (x - fnt.getlength(texto) / 2, y - tam / 2, x + fnt.getlength(texto) / 2, y + tam / 2))


def foco_en(im, xy, r=360, fuerza=0.38):
    """Oscurece suave todo lo que no es el chico (lleva el ojo sin poner nada encima de su cara)."""
    if not xy:
        return
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt((xx - xy[0]) ** 2 + ((yy - xy[1]) * 0.85) ** 2) / r
    m = 1 - fuerza * np.clip((dd - 0.55) / 0.9, 0, 1)
    a = np.asarray(im).astype(np.float32) * m[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


ISLAS = ["guadalcanal", "nueva_guinea", "saipan", "guam", "leyte", "luzon", "iwo_jima"]


def contador(im, f, k, t0, hasta=12700, dur=1.6):
    t = t_de(f)
    if t < t0:
        return
    u = sale((t - t0) / dur)
    n = int(round(hasta * u / 100.0)) * 100
    txt = f"{n:,}".replace(",", ".") + " AVIONES"
    cx, cy = libre(k, "cont", "12.700 AVIONES", [(540, 560), (540, 480)], tam=72)
    pildora(im, txt, cx, cy, fondo=AMBAR, tinta=(24, 24, 28), s=pop(t - t0), tam=72)


def barras(im, f, k):
    """MARINEROS 4.907 (azul, desde el mar) contra EJÉRCITO 4.675 (verde): crecen en 1,2 s; la azul pasa a la verde."""
    t = t_de(f) - T0(k) - 0.15
    if t <= 0:
        return
    base_y, alto_max = 900, 400
    lay = _capa_rgba(im)
    d = ImageDraw.Draw(lay)
    fnt = ImageFont.truetype(FONT, 40)
    fnum = ImageFont.truetype(FONT, 58)
    for i, (nombre, val, col, x) in enumerate((("MARINEROS", 4907, AZUL, 330), ("EJÉRCITO", 4675, VERDE, 750))):
        u = sale(min(1.0, t / (1.4 if i == 0 else 1.2)))
        h = alto_max * val / 4907 * u
        d.rounded_rectangle((x - 95 + 5, base_y - h + 7, x + 95 + 5, base_y + 7), radius=10, fill=(0, 0, 0, 110))
        d.rounded_rectangle((x - 95, base_y - h, x + 95, base_y), radius=10, fill=(*col, 240))
        num = f"{int(val * u):,}".replace(",", ".")
        texto_sombra(d, (x, base_y - h - 40), num, fnum)
        texto_sombra(d, (x, base_y + 40), nombre, fnt)
    _componer(im, lay)
    G.registrar("barras", (200, base_y - alto_max - 80, 880, base_y + 70))


def graficos(im, f, k):
    t = t_de(f)
    a0 = T0(k) - 0.3
    P = [(540, 560), (540, 640), (540, 480)]
    if k == 1:
        t0 = T0(1) + 0.25
        pild(im, f, 1, "kami", "KAMIKAZE · 17 AÑOS", t0, [(540, 455), (540, 400), (540, 500)], tam=54)
        cx, cy = libre(1, "kami", "KAMIKAZE · 17 AÑOS", [(540, 455)], 54)
        pc = meta(1, f, "casco")
        if pc and t >= t0 + 0.25 and pc[1] - cy > 110:
            flecha(im, cx + 30, cy + 48, pc[0], pc[1] - 22, (255, 255, 255), ancho=7)
    elif k == 2:
        pild(im, f, 2, "fecha", "26 DE MAYO DE 1945", tw("1945", a0) - 0.05, [(540, 300), (420, 300), (540, 420)], tam=50)
        pild(im, f, 2, "real", "FOTO REAL", T0(2) + 0.2, [(190, 600), (890, 600), (190, 700)], fondo=(28, 30, 34), tinta=(255, 255, 255), tam=38)
    elif k == 4:
        u = max(0.0, t - T0(4))
        for i, n in enumerate(ISLAS):
            ti = 0.15 + 0.22 * i
            col = ROJO if u < ti else GRIS
            punto_isla(im, _lug(4, f, n), col, r=11)
        etiqueta(im, "JAPÓN", _lug(4, f, "japon"), tam=50, dy=-50)
        pj = _lug(4, f, "kyushu")
        flecha_parcial(im, _lug(4, f, "saipan"), _lug(4, f, "iwo_jima"), sale((u - 0.3) / 0.8))
        flecha_parcial(im, _lug(4, f, "leyte"), _lug(4, f, "okinawa"), sale((u - 0.7) / 0.9))
    elif k in (6, 7, 8):
        pild(im, f, k, "real", "FOTO REAL", T0(k) + 0.1, [(190, 300), (890, 300), (190, 380)], fondo=(28, 30, 34), tinta=(255, 255, 255), tam=38)
        if k == 6:
            pild(im, f, 6, "vol", "VOLUNTARIOS", tw("voluntarios", a0), [(540, 880), (540, 820), (540, 940)], fondo=AMBAR, tam=60)
    elif k == 9:
        pild(im, f, 9, "carta", "ÚLTIMA CARTA", T0(9) + 0.3, P, fondo=AMBAR, tam=60)
        pild(im, f, 9, "recr", "RECREACIÓN", T0(9), [(860, 300), (200, 300)], fondo=(28, 30, 34), tinta=(255, 255, 255), tam=34)
    elif k == 10:
        pild(im, f, 10, "perdon", "PERDÓN", tw("perdón", a0), P, fondo=AMBAR, tam=72)
        pild(im, f, 10, "recr", "RECREACIÓN", T0(10), [(860, 300), (200, 300)], fondo=(28, 30, 34), tinta=(255, 255, 255), tam=34)
    elif k == 16:
        tb = E.T[16][1] - 0.2
        if t >= tb:
            u = min(1.0, (t - tb) / 0.08)
            blanco = Image.new("RGB", im.size, (255, 255, 255))
            im.paste(Image.blend(im, blanco, u))
    elif k == 17:
        pild(im, f, 17, "oki", "OKINAWA, 1945", T0(17) + 0.15, [(270, 330), (540, 330), (270, 420)], fondo=ACERO, tinta=(255, 255, 255), tam=50)
    elif k == 18:
        punto_isla(im, _lug(18, f, "okinawa"), ROJO, r=10)
        barras(im, f, 18)
    elif k == 19:
        u = max(0.0, t - T0(19))
        po, pk = _lug(19, f, "okinawa"), _lug(19, f, "kyushu")
        if po and pk:
            for dx in (-40, 0, 40):
                flecha_parcial(im, (po[0] + dx, po[1]), (pk[0] + dx * 0.4, pk[1] + 30), sale((u - 0.1 - 0.15 * abs(dx) / 40) / 1.6))
        punto_isla(im, po, AZUL, r=10)
        pild(im, f, 19, "inv", "INVASIÓN · 1 DE NOVIEMBRE", tw("invadir", a0) - 0.1, P, fondo=ACERO, tinta=(255, 255, 255), tam=50)
    elif k == 20:
        contador(im, f, 20, tw("junta", a0))
    elif k == 22:
        u = t - T0(22)
        late = 0.55 + 0.45 * abs(math.sin(u * math.pi * 1.1))
        mancha(im, _lug(22, f, "okinawa"), 70, late)
        etiqueta(im, "OKINAWA", _lug(22, f, "okinawa"), tam=44, dy=-80)
        pild(im, f, 22, "tru", "PRESIDENTE TRUMAN", T0(22) + 0.1, P, fondo=ACERO, tinta=(255, 255, 255), tam=54)
    elif k in (23, 24):
        u = t - T0(23)
        apaga = 1.0 if k == 23 else max(0.0, 1 - (t - T0(24)) / 1.4)
        late = (0.6 + 0.4 * abs(math.sin(u * math.pi * 1.3))) * apaga
        mancha(im, _lug(k, f, "okinawa"), 40, late)
        for i, n in enumerate(("kyushu", "hiroshima", "japon", "tokio")):
            v = sale((u - 0.2 - 0.35 * i) / 0.5) if k == 23 else 1.0
            mancha(im, _lug(k, f, n), 70 * v, late * v)
    elif k == 25:
        u = t - T0(25)
        for n, t1, txt in (("hiroshima", 0.1, "6 DE AGOSTO"), ("nagasaki", 0.8, "9 DE AGOSTO")):
            p = _lug(25, f, n)
            destello(im, p, (u - t1) / 0.8)
            if u >= t1 + 0.1 and p:
                etiqueta(im, txt, p, tam=42, dy=-70 if n == "hiroshima" else 70)
    elif k == 26:
        pild(im, f, 26, "fecha", "15 DE AGOSTO DE 1945", T0(26) + 0.1, [(540, 330), (540, 420)], tam=50)
        pild(im, f, 26, "rinde", "JAPÓN SE RINDE", tw("rinde", a0), [(540, 560), (540, 640)], fondo=AMBAR, tam=64)


_GRANO = np.random.default_rng(10).standard_normal((4, H, W)).astype(np.float32)
_yy, _xx = np.mgrid[0:H, 0:W]
_VIN = (1 - 0.22 * np.clip((np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2) - 0.55) / 0.6, 0, 1)).astype(np.float32)


def epoca(im, f, k):
    """Gradación de 1945: un poco menos de color, contraste, viñeta y grano (el mapa de la NASA va limpio)."""
    if E2_ESCENA.get(k) == "E4":
        return grado(im, color=1.05, contraste=1.04, calido=1.0)
    im = grado(im, color=0.86, contraste=1.10, calido=1.035)
    a = np.asarray(im).astype(np.float32)
    a *= _VIN[..., None]
    a += _GRANO[f % 4][..., None] * 4.5
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


LOOP0 = E.F(E.T[27][1] - 0.30)          # 53,40 s: vuelve la foto (cuadros del principio del plano 1)


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    if f >= LOOP0:
        a1, b1 = FR[1]
        im = cuadro(a1 + (f - LOOP0), a1, b1)
        k_img = 1
    else:
        im = cuadro(f, a, b)
        k_img = k
    if im is None:
        return False
    im = epoca(im, f, k_img)
    if k_img in (1, 2):
        im = foco_en(im, meta(k_img, a if k_img == 2 and f >= LOOP0 else f, "chico"), r=380 if k_img == 1 else 460, fuerza=0.34 if k_img == 1 else 0.28) or im
    if f < LOOP0:
        graficos(im, f, k)
    subtitulos(im, f)
    im.save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    return True


if __name__ == "__main__":
    cuadros = range(1, END)
    lista = os.environ.get("LISTA")
    if lista:
        cuadros = [int(v) for v in lista.split(",")]
    faltan = [f for f in cuadros if not procesar(f)]
    json.dump(SUB_LOG, open(os.path.join(OUT, "subs_log.json"), "w"))
    G.guardar(os.path.join(OUT, "graficos.json"))
    json.dump({"T": {str(k): list(v) for k, v in E.T.items()}, "FR": {str(k): list(v) for k, v in FR.items()}, "END": END},
              open(os.path.join(OUT, "ep10_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
