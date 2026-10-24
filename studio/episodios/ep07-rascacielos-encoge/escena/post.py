"""Post del Ep. 7 (sobre el del Ep. 5): arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Gradación común (grado.py), píldoras (v3: ESTO SÍ PASÓ, SIN HILOS, IMÁN, AGUA, HASTA 60 % AGUA, UN POQUITO, ≈ 16 TESLAS,
  PASO 1/2/3, NO CABE, ≈ 40 TESLAS O MÁS, ≈ 1 GIGAVATIO y SIMULACIÓN fija en todo lo hipotético), flechas de fuerza al
  lado de la rana (gris = gravedad, naranja = imán), la cota de 3 cm, el contorno de una mano real, las barras 16 T
  contra 40 T y los subtítulos palabra por palabra (franja y 1000–1250). Las posiciones salen del meta de cada cuadro
  (pantalla() de la escena) y las píldoras se ubican sin tapar ojos (graficos.lugar_libre).
- Escribe subs_log.json, graficos.json y ep07_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep07 as E
import graficos as G
from grado import grado

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
AMARILLO = (255, 210, 63)          # palabra activa (manual §6) y SIMULACIÓN
AZUL = (60, 140, 255)              # agua
CIAN = (40, 205, 255)              # líneas del imán
NARANJO = (255, 140, 30)           # el empujón del imán
GRIS = (150, 156, 166)             # la gravedad
CLAVE = {"SOMBRERO": NARANJO, "ELECTRICIDAD": (255, 190, 40), "EXPLOSIÓN": (255, 140, 30)}
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
NUMEROS = [("diez", "10"), ("dos", "2")]


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
# "Es más que nada agua": cortado en "NADA AGUA" se leía "nada de agua" (puerta 6 v3) → ES MÁS QUE NADA / AGUA, / COMO TÚ
_i = next((i for i, w in enumerate(words) if limpiar(w["w"]) == "NADA"), None)
if _i is not None:
    _js = [j for j, (tx, idx, fin) in enumerate(TOK) if idx[0] in range(_i - 3, _i + 1)]
    g3 = []
    for g in grupos:
        resto = [j for j in g if j not in _js]
        if any(j in _js for j in g) and _js[0] in g:
            g3.append(_js)
        if resto and resto != g or not any(j in _js for j in g):
            g3.append(resto)
    grupos = [g for g in g3 if g]
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


def simulacion(im):
    pildora(im, "SIMULACIÓN", 250, 330, fondo=AMARILLO, tinta=(24, 24, 28), tam=44)


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


DORADO = (255, 190, 40)            # la electricidad
RAPIDO = {1, 2, 3, 6, 8, 11, 12}      # tomas en cámara rápida (la torre real baja ~2 pisos cada 10 días)
CONTADOR = {1, 2, 8, 12}


def camara_rapida(im):
    pildora(im, "CÁMARA RÁPIDA", 250, 330, fondo=(30, 32, 36), tinta=(255, 255, 255), tam=40)


def contador(im, f, k):
    n = meta(k, f, "pisos", None)
    if n is None:
        return
    pildora(im, f"QUEDAN {n} PISOS", 760, 330, fondo=(250, 250, 248), tinta=(24, 24, 28), tam=46)
    fx, fy = meta(k, f, "fant", (540, 300))
    if 380 < fy < 900:
        pildora(im, "ANTES: 40 PISOS", max(260, min(860, fx + 340)), max(440, fy + 60), fondo=(30, 32, 36), tinta=(255, 255, 255), tam=38)


def _envolvente(pts):
    pts = sorted(set(map(tuple, pts)))
    if len(pts) < 3:
        return pts
    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    abajo, arriba = [], []
    for p in pts:
        while len(abajo) >= 2 and cruz(abajo[-2], abajo[-1], p) <= 0:
            abajo.pop()
        abajo.append(p)
    for p in reversed(pts):
        while len(arriba) >= 2 and cruz(arriba[-2], arriba[-1], p) <= 0:
            arriba.pop()
        arriba.append(p)
    return abajo[:-1] + arriba[:-1]


def contorno_techo(im, f):
    """Plano 4: contorno naranja que late alrededor de todo el sombrero (el último piso y su techo), desde "nunca"."""
    esq = meta(4, f, "techo", None)
    late = meta(4, f, "late", 0.0) or 0.0
    if not esq or late <= 0.01:
        return
    poli = _envolvente(esq)
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    a = int(255 * min(1.0, late))
    d.line(poli + [poli[0]], fill=(*NARANJO, a), width=12, joint="curve")
    glow = capa.filter(ImageFilter.GaussianBlur(10))
    im.paste(glow, (0, 0), glow)
    im.paste(capa, (0, 0), capa)


def _capa():
    return Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))


def _pegar(im, capa, glow=8):
    if glow:
        g = capa.filter(ImageFilter.GaussianBlur(glow))
        im.paste(g, (0, 0), g)
    im.paste(capa, (0, 0), capa)


def _trazo(pts, u):
    """El tramo de la polilínea pts recorrido hasta la fracción u (0–1) de su largo."""
    L = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    tot = sum(L) or 1
    obj = u * tot
    out = [tuple(pts[0])]
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if obj >= l:
            out.append(tuple(b)); obj -= l
        else:
            r = obj / l if l else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r)); break
    return out


def capa_pieza(im, f):
    """Plano 6: contorno blanco de la losa que la grúa está sacando y flecha hacia el pozo y hacia abajo."""
    esq = meta(6, f, "pieza", None)
    if not esq or str(f) not in META.get("6", {}).get("cuadros", {}) or "pieza" not in META["6"]["cuadros"][str(f)]:
        return
    poli = _envolvente(esq)
    c = _capa(); d = ImageDraw.Draw(c)
    d.line(poli + [poli[0]], fill=(255, 255, 255, 235), width=7, joint="curve")
    _pegar(im, c, 6)
    cx = sum(p[0] for p in poli) / len(poli); cy = sum(p[1] for p in poli) / len(poli)
    px, py = meta(6, f, "pozo", (540, 900)); qx, qy = meta(6, f, "pozo_abajo", (540, 1100))
    flecha(im, cx, cy, px, py, (255, 255, 255), ancho=8)
    flecha(im, px, py, qx, min(qy, 1000), (255, 255, 255), ancho=8)


def capa_electricidad(im, f, t):
    """Plano 9: la electricidad sale del generador y corre dorada por el cable hacia las lámparas (desde "genera")."""
    t_ge = tw("genera", 28.2)
    c = _capa(); d = ImageDraw.Draw(c)
    bx, by = meta(9, f, "bulto", (540, 900)); kx, ky = meta(9, f, "carro", (540, 700))
    if t < t_ge + 0.6:
        flecha(im, kx + 60, ky + 40, bx + 60, by, (255, 255, 255), ancho=8)          # el bulto baja
    if t >= t_ge:
        u = min(1.0, (t - t_ge) / 1.0)
        for clave in ("cable", "cable2"):
            pts = meta(9, f, clave, None)
            if pts:
                tr = _trazo(pts, u)
                if len(tr) > 1:
                    d.line(tr, fill=(*DORADO, 255), width=12, joint="curve")
                    hx, hy = tr[-1]
                    d.ellipse((hx - 16, hy - 16, hx + 16, hy + 16), fill=(255, 245, 200, 255))
        _pegar(im, c, 10)


def capa_luces(im, f, t):
    """Plano 10: cada lámpara se prende con su resplandor y su cono de luz hacia el piso."""
    t_pr = tw("prenden", 30.2)
    lam = meta(10, f, "lamparas", None); pis = meta(10, f, "piso", None)
    if not lam or not pis:
        return
    c = _capa(); d = ImageDraw.Draw(c)
    for k, ((lx, ly), (fx, fy)) in enumerate(zip(lam, pis)):
        on = min(1.0, max(0.0, (t - (t_pr + 0.2 * k)) / 0.1))
        if on <= 0 or not (0 < lx < 1080 and 0 < ly < 1920):
            continue
        w = max(30, abs(fy - ly) * 0.55)
        d.polygon([(lx - 18, ly), (lx + 18, ly), (fx + w, fy), (fx - w, fy)], fill=(255, 214, 140, int(70 * on)))
        d.ellipse((lx - 26, ly - 14, lx + 26, ly + 14), fill=(255, 236, 190, int(255 * on)))
    _pegar(im, c, 12)


def graficos(im, f, k):
    t = t_de(f)
    if k in RAPIDO:
        camara_rapida(im)
    if k in CONTADOR:
        contador(im, f, k)
    P = [(540, 560), (540, 640)]
    if k == 3:
        pild(im, f, 3, "sinex", "SIN EXPLOSIONES", tw("Sin", 3.5), [(740, 330), (740, 420)])
    elif k == 4:
        contorno_techo(im, f)
        pild(im, f, 4, "techo", "EL TECHO QUEDA ENTERO", tw("techo", 7.0), P, fondo=NARANJO, tinta=(255, 255, 255))
    elif k == 5:
        t_so, t_ga = tw("sombrero", 9.0), tw("gatos", 10.8)
        pild(im, f, 5, "p1", "PASO 1 · SOMBRERO", tw("Primero", 8.0), P, tam=50, hasta=t_ga)
        if t >= t_ga:
            gx, gy = meta(5, f, "gata", (540, 900))
            py = max(520, min(760, gy - 230))
            px = max(350, min(730, gx))
            if gy - py > 90:
                flecha(im, px, py + 45, gx, gy - 20, AMARILLO, ancho=9)
            pildora(im, "GATOS HIDRÁULICOS", px, py, fondo=AMARILLO, tinta=(24, 24, 28), s=pop(t - t_ga), tam=48)
    elif k == 6:
        capa_pieza(im, f)
        pild(im, f, 6, "p2", "PASO 2 · DESARMAN", tw("Después", 12.0), P, tam=50)
    elif k == 7:
        t_pi = tw("piso", 19.5)
        pild(im, f, 7, "p3", "PASO 3 · BAJAN", tw("final", 16.5), P, tam=50, hasta=t_pi)
        pild(im, f, 7, "menos1", "−1 PISO", t_pi, P, tam=58)
    elif k == 8:
        pild(im, f, 8, "rev", "EN REVERSA", tw("reversa", 24.5), P)
    elif k == 9:
        capa_electricidad(im, f, t)
        pild(im, f, 9, "elec", "ELECTRICIDAD", tw("electricidad", 28.5), P, fondo=DORADO, tinta=(24, 24, 28))
    elif k == 10:
        capa_luces(im, f, t)
        pild(im, f, 10, "luces", "LUCES DE LA OBRA", tw("luces", 30.8), P, fondo=DORADO, tinta=(24, 24, 28))
    elif k == 12:
        t_di = tw("diez", 35.5)
        pild(im, f, 12, "menos2", "−2 PISOS", tw("dos", 34.3), P, hasta=t_di)
        pild(im, f, 12, "diez", "−2 PISOS · CADA 10 DÍAS", t_di, P, tam=50)


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    im = cuadro(f, a, b)
    if im is None:
        return False
    im = grado(im)                                            # la misma gradación de los cuadros de estilo (grado.py)
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
              open(os.path.join(OUT, "ep07_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
