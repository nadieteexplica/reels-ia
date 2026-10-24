"""Post del Ep. 5: arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Gradación común (grado.py), píldoras (v3: ESTO SÍ PASÓ, SIN HILOS, IMÁN, AGUA, HASTA 60 % AGUA, UN POQUITO, ≈ 16 TESLAS,
  PASO 1/2/3, NO CABE, ≈ 40 TESLAS O MÁS, ≈ 1 GIGAVATIO y SIMULACIÓN fija en todo lo hipotético), flechas de fuerza al
  lado de la rana (gris = gravedad, naranja = imán), la cota de 3 cm, el contorno de una mano real, las barras 16 T
  contra 40 T y los subtítulos palabra por palabra (franja y 1000–1250). Las posiciones salen del meta de cada cuadro
  (pantalla() de la escena) y las píldoras se ubican sin tapar ojos (graficos.lugar_libre).
- Escribe subs_log.json, graficos.json y ep05_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep05 as E
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
CLAVE = {"AGUA": AZUL, "TESLAS": NARANJO, "GIGAVATIO": NARANJO}
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
NUMEROS = [("cuarenta", "40"), ("tres", "3")]


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


def cota(im, f, a=1.0):
    """Cota de 3 cm de pared a pared del tubo, 9 mm POR ENCIMA de la rana (puerta 3: sobre la rana le tapaba los ojos),
    con flechas en los bordes reales del tubo (calculados en la escena) y "3 cm" encima."""
    if a <= 0.01:
        return
    (xi, yi), (xd, yd) = meta(11, f, "izq"), meta(11, f, "der")
    yl = (yi + yd) / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    al = int(255 * a)
    for (x0, y0, x1, y1, w) in ((xi, yl - 34, xi, yl + 34, 5), (xd, yl - 34, xd, yl + 34, 5), (xi, yl, xd, yl, 7)):
        d.line((x0 + 2, y0 + 4, x1 + 2, y1 + 4), fill=(0, 0, 0, int(0.5 * al)), width=w + 4)
        d.line((x0, y0, x1, y1), fill=(255, 255, 255, al), width=w)
    for x, s in ((xi, 1), (xd, -1)):
        d.polygon([(x, yl), (x + 26 * s, yl - 12), (x + 26 * s, yl + 12)], fill=(255, 255, 255, al))
    texto_sombra(d, ((xi + xd) / 2, yl - 70), "3,2 cm", ImageFont.truetype(FONT, 64), a=al)
    im.paste(lay, (0, 0), lay)
    G.registrar("cota", (xi - 30, yl - 110, xd + 30, yl + 40))


def mano(im, f, a=1.0):
    """Contorno blanco de una mano adulta a escala real (palma de 8,5 cm, 20 cm de largo, dedos hacia arriba) al lado del
    tubo de la rana, con la misma proyección de la escena: se ve cuántas veces más ancha es que el hueco (puerta 3 v3)."""
    if a <= 0.01:
        return
    cx, cy = meta(11, f, "mano_c")
    mx, _my = meta(11, f, "mano_m")
    pxm = (mx - cx) * 100.0
    if pxm <= 0:
        return
    S = 2
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)

    def P(x, y):            # x: a lo largo de los dedos (hacia arriba), y: a lo ancho (+ hacia el tubo)
        return (cx + y * pxm) * S, (cy - x * pxm) * S

    def caps(x0, y0, x1, y1, r):
        a_, b_ = P(x0, y0), P(x1, y1)
        rr = r * pxm * S
        d.line((a_, b_), fill=255, width=int(2 * rr))
        for (x, y) in (a_, b_):
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=255)

    (x0, y0), (x1, y1) = P(0.05, -0.0425), P(-0.05, 0.0425)
    d.rounded_rectangle((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), radius=0.016 * pxm * S, fill=255)
    for y, largo in ((-0.031, 0.072), (-0.0105, 0.080), (0.0105, 0.075), (0.031, 0.060)):   # índice, medio, anular, meñique
        caps(0.04, y * 0.95, 0.04 + largo, y * 1.12, 0.0088)
    caps(-0.005, -0.034, 0.045, -0.078, 0.0108)                                      # pulgar, hacia afuera (lejos del tubo)
    caps(-0.06, 0.0, -0.085, 0.0, 0.028)                                             # muñeca
    m = m.filter(ImageFilter.GaussianBlur(1.2 * S))
    borde = m.filter(ImageFilter.MaxFilter(13))
    contorno = Image.fromarray(np.clip(np.asarray(borde, np.int16) - np.asarray(m, np.int16), 0, 255).astype(np.uint8))
    contorno = contorno.resize((W, H), Image.LANCZOS)
    relleno = m.resize((W, H), Image.LANCZOS)
    blanco = Image.new("RGBA", im.size, (255, 255, 255, 0))
    blanco.putalpha(Image.fromarray(np.clip(np.asarray(contorno, np.float32) * 1.6 * a + np.asarray(relleno, np.float32) * 0.12 * a, 0, 255).astype(np.uint8)))
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sombra.putalpha(Image.fromarray((np.asarray(contorno.filter(ImageFilter.GaussianBlur(4)), np.float32) * 0.6 * a).astype(np.uint8)))
    im.paste(sombra, (3, 5), sombra)
    im.paste(blanco, (0, 0), blanco)
    G.registrar("mano", tuple(int(v) for v in contorno.getbbox() or (0, 0, 0, 0)))


def barras(im, f, t0):
    """RANA 16 T contra TÚ 40 T O MÁS, en proporción real (16/40), sobre un panel oscuro."""
    t = t_de(f)
    if t < t0:
        return
    x0, L = 140, 800
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 - 30, 520, x0 + L + 30, 712), radius=28, fill=(10, 12, 16, int(150 * min(1, (t - t0) / 0.2))))
    fnt = ImageFont.truetype(FONT, 40)
    for i, (txt, val, col, tinta) in enumerate((("RANA · 16 T", 16, CIAN, (10, 30, 40)), ("TÚ · 40 T O MÁS", 40, NARANJO, (255, 255, 255)))):
        x = sale(min(1.0, max(0.0, (t - t0 - 0.12 * i) / 0.5)))
        if x <= 0:
            continue
        y = 548 + 92 * i
        w = max(60, L * val / 40 * x)
        d.rounded_rectangle((x0, y, x0 + w, y + 64), radius=32, fill=(*col, 245))
        d.text((x0 + 26, y + 32), txt, font=fnt, fill=tinta, anchor="lm")
    im.paste(lay, (0, 0), lay)
    G.registrar("barras", (x0 - 30, 520, x0 + L + 30, 712))


SIM = {1, 2, 10, 12, 13, 14, 15, 16}


def graficos(im, f, k):
    t = t_de(f)
    if k in SIM or k == 9:            # desde el corte del 9 (17,0 s), no a mitad del plano (puerta 6 v3)
        simulacion(im)
    if k == 3:
        pild(im, f, 3, "real", "ESTO SÍ PASÓ", tw("pasó", 4.0), [(540, 330), (540, 400)], marca="v")
    elif k == 4:
        t_im = tw("imán", 7.0)
        pild(im, f, 4, "hilos", "SIN HILOS", tw("sola", 6.0), [(540, 330), (540, 400)], hasta=t_im)
        pild(im, f, 4, "iman", "IMÁN", t_im, [(540, 330), (540, 400)], fondo=CIAN, tinta=(10, 30, 40))
    elif k == 5:
        pild(im, f, 5, "agua", "AGUA", tw("nada", 8.0), [(540, 330), (540, 400)], fondo=AZUL, tinta=(255, 255, 255))
    elif k == 6:
        pild(im, f, 6, "agua", "HASTA 60 % AGUA", T0(6) + 0.05, [(540, 400), (540, 330)], fondo=AZUL, tinta=(255, 255, 255))
    elif k == 7:
        t_e = tw("empuja", 10.0)
        pild(im, f, 7, "agua", "AGUA", T0(7), [(540, 400), (540, 330)], fondo=AZUL, tinta=(255, 255, 255), hasta=t_e)
        pild(im, f, 7, "poco", "UN POQUITO", tw("poquito", 12.0), [(540, 400), (540, 330)])
    elif k == 8:
        rx, y0 = meta(8, f, "rana", (440, 650))
        x = min(980, max(640, rx + 230))
        t_g, t_i, t_w = T0(8) + 0.3, T0(8) + 0.8, tw("gana", 14.0)
        if t > t_g:
            L = 170 * sale(min(1, (t - t_g) / 0.3))
            flecha(im, x + 40, y0, x + 40, y0 + L, GRIS, ancho=16)
            pildora(im, "GRAVEDAD", x + 40, y0 + 260, fondo=GRIS, tinta=(255, 255, 255), tam=38, s=pop(t - t_g))
        if t > t_i:
            L = 120 + 120 * suave(min(1, (t - t_i) / max(0.3, t_w + 0.3 - t_i)))
            flecha(im, x - 40, y0, x - 40, y0 - L, NARANJO, ancho=16)
            pildora(im, "IMÁN", x - 40, y0 - L - 70, fondo=NARANJO, tinta=(255, 255, 255), tam=38, s=pop(t - t_i))
        pild(im, f, 8, "t16", "≈ 16 TESLAS", tw("fuerte", 14.0), [(300, 330), (300, 400)], fondo=NARANJO, tinta=(255, 255, 255), tam=50)
    elif k == 10:
        pild(im, f, 10, "p1", "PASO 1 · EL HUECO", tw("primero", 19.0), [(330, 470), (540, 470)], tam=48)
    elif k == 11:
        t_tres, t_mano = tw("tres", 22.0), tw("mano", 23.0)
        if t >= t_tres:
            cota(im, f, a=min(1.0, (t - t_tres) / 0.15) * (1 - suave(min(1.0, max(0.0, (t - t_mano + 0.75) / 0.25)))))
        mano(im, f, a=suave(min(1.0, max(0.0, (t - t_mano + 0.15) / 0.28))))
        pild(im, f, 11, "nocabe", "NO CABE", t_mano, [(790, 330), (790, 400)])
    elif k == 12:
        pild(im, f, 12, "p2", "PASO 2 · BOBINAS", tw("después", 25.0), [(330, 470), (540, 470)], tam=48)
    elif k == 13:
        pild(im, f, 13, "t40", "≈ 40 TESLAS O MÁS", tw("cuarenta", 28.0) + 0.05, [(540, 450)], fondo=NARANJO, tinta=(255, 255, 255))
        barras(im, f, tw("más", 30.0))          # con "Más del doble", la frase que las explica (puerta 6 v3)
    elif k == 14:
        t_re = tw("reactor", 33.0)
        pild(im, f, 14, "p3", "PASO 3 · ENERGÍA", tw("final", 32.0), [(540, 470), (330, 470)], tam=48, hasta=t_re)
        t_gw = tw("entero", 34.0)
        if t >= t_gw:
            cxp, cyp = meta(14, f, "central", (700, 780))
            pildora(im, "≈ 1 GIGAVATIO", min(330, cxp - 290), max(430, min(760, cyp - 120)), fondo=NARANJO,
                    tinta=(255, 255, 255), s=pop(t - t_gw), tam=52)




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
              open(os.path.join(OUT, "ep05_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
